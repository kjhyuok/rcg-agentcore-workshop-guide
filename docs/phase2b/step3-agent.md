# Step 3: 수요 예측 Agent 작성 & 배포 <span class="badge-time">⏱️ 15분</span> <span class="badge-difficulty">★★★</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 Memory</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 2 Gateway+Browser</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 3 Agent</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 4 Policy</span>
</div>

!!! info "소요 시간: 15분"
    Memory에서 발주 이력을 가져오고, Gateway Tool로 현황을 분석한 뒤,
    발주 판단까지 하는 Agent를 작성합니다.

<div class="file-target">agents/phase2b_demand.py</div>
---

## Agent 코드: `agents/phase2b_demand.py`

```python
import os
import json
import asyncio
import nest_asyncio
from strands import Agent
from strands.models import BedrockModel
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from bedrock_agentcore.memory import MemoryClient
from strands_tools.browser import AgentCoreBrowser
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

nest_asyncio.apply()

# --- 설정 ---
GATEWAY_URL = os.environ.get("AGENTCORE_GATEWAY_URL", "")
MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_ID", "")
REGION = os.environ.get("AWS_REGION", "us-east-1")

# --- Memory 클라이언트 ---
memory_client = MemoryClient(region_name=REGION)

# --- Browser Tool ---
browser_tool = AgentCoreBrowser(region=REGION)

# --- Gateway에서 Tool 가져오기 ---
async def get_gateway_tools(gateway_url: str, headers: dict) -> list:
    async with streamablehttp_client(gateway_url, headers=headers) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return (await session.list_tools()).tools

# --- System Prompt ---
SYSTEM_PROMPT = """당신은 리테일 매장의 수요 예측 & 발주 전문가입니다.

## 역할
1. 매장의 재고 현황을 파악합니다
2. 판매 트렌드와 외부 요인을 분석합니다
3. 분석 결과를 바탕으로 최적 발주량을 결정합니다
4. 발주를 실행합니다

## 분석 프로세스 (반드시 순서대로)
1단계: inventory_status → 현재 재고 부족 품목 확인
2단계: sales_trend → 해당 품목의 판매 추이 확인
3단계: external_factors → 수요 영향 요인 확인
4단계: 종합 판단 후 purchase_order 실행

## 발주 규칙
- 안전재고 이하 품목은 긴급(urgent) 발주
- 트렌드 상승 + 외부 요인 존재 시 20% 추가 발주
- 50만원 초과 발주는 승인이 필요함을 안내

## 응답 형식
- 분석 결과를 표로 정리
- 발주 추천 사유를 명확히 설명
- 예상 비용과 리드타임 포함

## Memory 활용
- 이전 발주 이력을 참고하여 패턴 기반 판단
- 과거 실수(과다발주/부족)를 반복하지 않도록 학습
"""

# --- Memory에서 이전 이력 가져오기 ---
def get_order_history(store_id: str) -> str:
    """매장의 이전 발주 이력을 Memory에서 조회"""
    results = memory_client.retrieve(
        namespace=f"/orders/{store_id}/",
        query="최근 발주 이력과 패턴",
        max_results=5
    )
    if results:
        return "\n".join([r["content"] for r in results])
    return "이전 발주 이력 없음 (첫 발주)"


# --- Agent 생성 ---
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6-20250514-v1:0",
    region_name="us-east-1"
)

agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=tools
)


# --- 엔트리 포인트 ---
def handler(event, context):
    """AgentCore Runtime 핸들러"""
    user_input = event.get("input", "")
    store_id = event.get("store_id", "store-001")

    # Memory에서 이력 가져와서 컨텍스트에 추가
    history = get_order_history(store_id)
    enriched_input = f"""[매장: {store_id}]
[이전 발주 이력]
{history}

[요청] {user_input}"""

    # Agent 실행
    response = agent(enriched_input)

    # 발주 결과를 Memory에 저장
    memory_client.store(
        namespace=f"/orders/{store_id}/",
        content=f"발주 요청: {user_input}\n결과: {str(response)[:500]}",
        metadata={"store_id": store_id}
    )

    return {
        "statusCode": 200,
        "body": str(response)
    }
```

---

## 배포

```bash
cd agents/

agentcore deploy \
  --name "demand-forecast-agent" \
  --entry-point "phase2b_demand.handler" \
  --env MEMORY_ID=$MEMORY_ID \
  --env GATEWAY_URL=$GATEWAY_URL
```

---

## 테스트

```bash
agentcore invoke \
  --agent "demand-forecast-agent" \
  '{"input": "현재 재고 분석하고 긴급 발주 진행해", "store_id": "store-001"}'
```

---

## 예상 응답

```markdown
## 재고 분석 결과 (store-001)

| 카테고리 | 현재재고 | 안전재고 | 상태 |
|---------|---------|---------|------|
| 라면류   | 45박스  | 100박스 | 부족 |
| 음료류   | 23박스  | 80박스  | 긴급 |
| 과자류   | 120박스 | 90박스  | 정상 |

## 트렌드 분석
- 음료류: 주간 +35% 성장 (폭염 예보 영향)
- 라면류: 월간 -5% (계절적 감소)

## 외부 요인
- 향후 7일 폭염 예보 (35도 이상)
- 근처 축제 예정 (7/5~7/7)

## 발주 추천

| 품목 | 수량 | 금액 | 긴급도 | 사유 |
|------|------|------|--------|------|
| 음료류 | 200박스 | 1,200,000원 | urgent | 안전재고 미달 + 폭염 |
| 라면류 | 80박스 | 400,000원 | normal | 안전재고 보충 |

**총 발주 금액: 1,600,000원**
> 50만원 초과 — 승인 필요 (approval_needed: true)
```

---

## Trace에서 확인되는 호출 흐름

Observability Dashboard에서 11개 Tool 호출이 보입니다:

```
1. [Memory] retrieve — 이전 발주 이력 조회
2. [Gateway] inventory_status — store-001 전체 재고
3. [Gateway] inventory_status — store-001 음료 카테고리 상세
4. [Gateway] sales_trend — store-001, 7d, 음료
5. [Gateway] sales_trend — store-001, 30d, 라면
6. [Gateway] sales_trend — store-001, 7d, 과자
7. [Gateway] external_factors — store-001, 7일 예보
8. [Gateway] purchase_order — 음료류 200박스 (urgent)
9. [Gateway] purchase_order — 라면류 80박스 (normal)
10. [Policy] check — 총액 1,600,000원 > 500,000원
11. [Memory] store — 발주 결과 저장
```

!!! note "Agent가 스스로 판단합니다"
    System Prompt에 "순서대로 분석하라"고 했지만, Agent는 상황에 따라
    필요한 Tool을 **자율적으로 선택**합니다. 항상 정확히 11번이 아닐 수 있습니다.

---

!!! success "다음 단계"
    Agent가 동작합니다! 하지만 50만원 초과 발주가 그냥 실행되면 안 되겠죠?
    [Step 4: Policy 설정](step4-policy.md)으로 이동합니다.
