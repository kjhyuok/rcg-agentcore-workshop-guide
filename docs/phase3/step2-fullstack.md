# Step 2: 풀스택 Agent 조립하기 <span class="badge-time">⏱️ 30분</span> <span class="badge-difficulty">★★★</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 Orchestrator 연결</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 2 Agent 조립</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 3 배포 & 검증</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 4 발표</span>
</div>

!!! info "소요 시간: 30분"
    Phase 1~2의 코드를 복사한 뒤 **3가지만 바꿉니다**.
    그리고 Orchestrator에 등록하여 Multi-Agent 시스템에 참여합니다.

<div class="file-target">agents/phase3_custom.py</div>
---

## 전략: Copy → Modify 3 Things → Register

```
Phase 1-2 코드 복사 → 아래 3개만 수정:
  1. System Prompt (역할 변경)
  2. Gateway Tools (선택적 조합 변경)
  3. Memory 네임스페이스 (도메인 변경)
→ 배포 후 Orchestrator에 등록
```

!!! tip "왜 이렇게?"
    30분 안에 Lambda를 새로 배포하기는 어렵습니다.
    하지만 **같은 Tool이라도 System Prompt와 Memory 전략이 다르면 완전히 다른 Agent**가 됩니다.
    이것이 AgentCore의 "조합형 아키텍처"의 강점입니다.

---

## 기본 템플릿

`agents/phase3_custom.py`로 새 파일을 만드세요:

```python title="agents/phase3_custom.py"
import os
import uuid
from strands import Agent
from strands.models import BedrockModel
from strands_tools.code_interpreter import AgentCoreCodeInterpreter
from strands_tools.browser import AgentCoreBrowser
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from mcp import ClientSession

from mcp.client.streamable_http import streamablehttp_client

# --- 설정 ---
GATEWAY_URL = os.environ.get("AGENTCORE_GATEWAY_URL", "")
REGION = "us-east-1"

# --- 모델 ---
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6-20250514-v1:0",
    region_name=REGION,
)

# --- 추가 Tool 초기화 ---
code_interpreter_tool = AgentCoreCodeInterpreter(region=REGION)
browser_tool = AgentCoreBrowser(region=REGION)

# ╔══════════════════════════════════════════════╗
# ║  수정 포인트 1: System Prompt               ║
# ╚══════════════════════════════════════════════╝
SYSTEM_PROMPT = """당신은 [여기에 역할]입니다.

## 역할
- [구체적인 역할 설명]

## 사용 가능한 도구
- [Tool 1]: [언제 사용하는지]
- [Tool 2]: [언제 사용하는지]

## 응답 규칙
- [규칙 1]
- [규칙 2]

## 계산/분석이 필요할 때
- code_interpreter를 사용하여 정확한 수치를 계산하세요

## 외부 정보가 필요할 때
- browser를 사용하여 웹에서 실시간 정보를 가져오세요
"""

# ╔══════════════════════════════════════════════╗
# ║  수정 포인트 2: 사용할 Tool 선택             ║
# ╚══════════════════════════════════════════════╝
# 아래에서 필요한 Tool만 주석 해제하세요
EXTRA_TOOLS = [
    code_interpreter_tool.code_interpreter,  # 데이터 분석/계산
    # browser_tool.browser,                  # 외부 웹 조회
]

# ╔══════════════════════════════════════════════╗
# ║  수정 포인트 3: Memory 네임스페이스           ║
# ╚══════════════════════════════════════════════╝
MEMORY_NAMESPACE = "/custom/{actorId}/"  # 여기를 변경!


# --- Runtime Entrypoint ---
app = BedrockAgentCoreApp()

@app.entrypoint
def custom_agent(payload: dict) -> dict:
    """Orchestrator 또는 직접 호출 시 실행되는 엔트리포인트"""
    user_message = payload.get("message", "")
    session_id = payload.get("session_id", f"sess-{uuid.uuid4()}")

    mcp = MCPClient(lambda: streamablehttp_client(GATEWAY_URL, auth=auth))

    with mcp:
        gateway_tools = mcp.list_tools_sync()

        # Gateway Tools + 추가 Tools 조합
        all_tools = gateway_tools + EXTRA_TOOLS

        agent = Agent(
            model=model,
            system_prompt=SYSTEM_PROMPT,
            tools=all_tools
        )
        result = agent(user_message)

    return {
        "response": str(result),
        "session_id": session_id,
    }


# --- 로컬 테스트 ---
if __name__ == "__main__":
    test_payload = {
        "message": "테스트 질문을 여기에 입력하세요",
        "session_id": "test-local"
    }
    response = custom_agent(test_payload)
    print(response["response"])
```

---

## 수정 예시: 프로모션 Agent로 변환

```python
# 수정 1: System Prompt
SYSTEM_PROMPT = """당신은 매장 맞춤형 프로모션 전략가입니다.

## 역할
1. 매장의 고객 세그먼트를 분석합니다
2. 최근 판매 트렌드를 확인합니다
3. 과거 성공한 프로모션 패턴을 참고합니다
4. 맞춤형 프로모션 전략을 제안합니다

## 응답 형식
- 타겟 고객층, 추천 상품, 할인율, 예상 효과를 포함
- 과거 유사 프로모션의 성과와 비교

## 계산이 필요할 때
- 할인율, ROI 계산은 code_interpreter를 사용하세요
- 경쟁사 가격은 browser로 확인하세요
"""

# 수정 2: Tools — Code Interpreter + Browser 모두 사용
EXTRA_TOOLS = [
    code_interpreter_tool.code_interpreter,  # ROI 계산
    browser_tool.browser,                    # 경쟁사 가격 확인
]

# 수정 3: Memory 네임스페이스
MEMORY_NAMESPACE = "/promotions/{actorId}/"
```

---

## 배포하기

```bash
# 배포 설정
agentcore configure --entrypoint agents/phase3_custom.py --non-interactive

# 배포 실행
agentcore deploy

# 배포된 Agent ARN 확인
AGENT_ARN=$(agentcore describe --name phase3-custom --query 'agentArn' --output text)
echo "내 Agent ARN: $AGENT_ARN"
```

---

## Orchestrator에 등록하기

배포된 Agent를 Orchestrator에 등록하면, 사용자 요청이 자동으로 여러분의 Agent에게 라우팅됩니다:

```bash
# Orchestrator 등록 스크립트 실행
python3 scripts/register-with-orchestrator.py \
  --agent-name "my-custom-agent" \
  --agent-arn "$AGENT_ARN" \
  --description "매장 맞춤형 프로모션 전략을 수립하는 Agent" \
  --capabilities "추천,분석,프로모션"
```

??? example "등록 스크립트 내부 (참고용)"
    ```python
    import requests
    import boto3

    ORCHESTRATOR_URL = os.environ["ORCHESTRATOR_URL"]

    # 등록 요청
    response = requests.post(
        f"{ORCHESTRATOR_URL}/agents/register",
        json={
            "agent_name": args.agent_name,
            "agent_arn": args.agent_arn,
            "description": args.description,
            "capabilities": args.capabilities.split(","),
        },
        headers={"Authorization": f"Bearer {get_token()}"}
    )
    print(f"✅ 등록 완료: {response.json()}")
    ```

??? success "정상 출력"
    ```
    ✅ Orchestrator 등록 완료!
    - Agent 이름: my-custom-agent
    - Agent ARN: arn:aws:bedrock-agentcore:us-east-1:123456:agent/abc123
    - 상태: ACTIVE
    - 라우팅 키워드: 추천, 분석, 프로모션
    ```

---

## 평가 스크립트로 품질 측정

등록이 완료되면, 평가 스크립트로 Agent의 품질을 측정합니다:

```bash
python3 scripts/run-evaluation.py --agent-name my-custom-agent
```

??? success "평가 결과 예시"
    ```
    ╔══════════════════════════════════════════════════╗
    ║          Agent 품질 평가 결과                     ║
    ╠══════════════════════════════════════════════════╣
    ║                                                  ║
    ║  Agent: my-custom-agent                          ║
    ║  테스트 시나리오: 5개                              ║
    ║                                                  ║
    ║  ┌────────────────┬────────┬───────────┐        ║
    ║  │ 평가 항목       │ 점수   │ 등급      │        ║
    ║  ├────────────────┼────────┼───────────┤        ║
    ║  │ 정확도          │ 85/100 │ ⭐⭐⭐⭐  │        ║
    ║  │ Tool 활용도     │ 90/100 │ ⭐⭐⭐⭐⭐│        ║
    ║  │ 응답 품질       │ 78/100 │ ⭐⭐⭐⭐  │        ║
    ║  │ 안전성 (Policy) │ 95/100 │ ⭐⭐⭐⭐⭐│        ║
    ║  │ 응답 속도       │ 82/100 │ ⭐⭐⭐⭐  │        ║
    ║  ├────────────────┼────────┼───────────┤        ║
    ║  │ 종합            │ 86/100 │ A         │        ║
    ║  └────────────────┴────────┴───────────┘        ║
    ║                                                  ║
    ║  💡 개선 제안:                                    ║
    ║  - System Prompt에 응답 형식 규칙 추가 권장       ║
    ║  - Memory 활용 시 이전 결과 참조 패턴 추가 가능   ║
    ║                                                  ║
    ╚══════════════════════════════════════════════════╝
    ```

!!! tip "점수 올리기 팁"
    - **정확도**: System Prompt에 구체적인 행동 규칙 추가
    - **Tool 활용도**: 필요한 Tool을 빠짐없이 사용하도록 Prompt 작성
    - **응답 품질**: 응답 형식(구조화된 출력)을 Prompt에 명시
    - **안전성**: Policy 규칙에 맞게 에스컬레이션 처리
    - **응답 속도**: 불필요한 Tool 호출 최소화

---

## 조합 가능한 Tool 전체 목록

| Tool | 도메인 | 활용 예 |
|------|--------|---------|
| `customer_profile` | 고객 | 세그먼트, VIP 확인 |
| `product_search` | 상품 | 카테고리별 상품 검색 |
| `purchase_history` | 거래 | 구매 패턴 분석 |
| `lookup_order` | 주문 | 주문 상태 확인 |
| `return_policy` | 정책 | 반품 규정 조회 |
| `inventory_status` | 재고 | 재고 현황 파악 |
| `sales_trend` | 분석 | 매출 트렌드 |
| `external_factors` | 외부 | 날씨/이벤트 영향 |
| `code_interpreter` | 계산 | 데이터 분석, 통계, 시각화 |
| `browser` | 웹 | 경쟁사 가격, 뉴스, 날씨 |

!!! note "창의적 조합을 환영합니다"
    예: `customer_profile` + `sales_trend` + `external_factors` + `browser`
    → "이 고객에게 폭염 시즌에 맞는 상품을 추천"하는 **컨텍스트 인지 추천 Agent**
    
    예: `inventory_status` + `code_interpreter` + `browser`
    → "재고 부족 예측 + 경쟁사 가격 비교 + 최적 발주량 계산"하는 **스마트 발주 Agent**

---

## 체크리스트

- [ ] 템플릿 복사 완료
- [ ] System Prompt 작성 (최소 역할 + 도구 설명)
- [ ] Tool 조합 선택 (Gateway 2~4개 + 추가 Tool)
- [ ] Memory 네임스페이스 결정
- [ ] `agentcore deploy` 성공
- [ ] Orchestrator 등록 완료
- [ ] 평가 스크립트 실행 (점수 확인)

!!! success "다음 단계"
    코드 준비 완료! [Step 3: 배포 & 검증](step3-deploy.md)으로 이동합니다.
