# Step 2: 나만의 수집 Agent 만들어 배포하기 <span class="badge-time">⏱️ 25분</span> <span class="badge-difficulty">★★★</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 Gateway</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 2 Agent</span>
</div>

!!! info "이 Step의 목표"
    Step 1에서 등록한 Gateway Tool(날씨/이벤트, 재고, 트렌드, 발주)을 활용하는 Agent를 만들어 배포합니다.
    
    **이 Agent가 무엇을 하는지는 여러분이 정합니다.** 가이드는 코드 골격과 툴 사용법만 제공합니다.
    이 코드는 Phase 3 바이브코딩의 **참고 코드**가 됩니다 — 구조를 눈에 익혀두세요.

<div class="file-target">agents/phase2b/app/phase2b/main.py</div>
---

## 2-1. 시나리오 정하기 (3분)

등록된 Tool로 무엇을 시킬지 먼저 정하세요. 예를 들면 — 날씨와 이벤트를 보고 음료 발주를 제안하는 Agent, 재고와 트렌드를 분석해 품절 위험을 알려주는 Agent, 매일 아침 점장에게 외부 요인 브리핑을 만들어주는 Agent... 어떤 것이든 좋습니다.

아래 두 가지만 정하면 됩니다:

```
내 Agent의 역할 한 줄: ______________________________________
테스트 질문 (Agent에게 물어볼 말): "____________________________"
```

!!! tip "조합할 수 있는 Tool (Gateway에 등록됨)"
    | Tool | 기능 |
    |------|------|
    | `customer_profile` | 고객 프로필 조회 (세그먼트, VIP, 알러지) |
    | `product_search` | 카테고리별 상품 검색 |
    | `purchase_history` | 고객 구매 이력 |
    | `external_factors` | 날씨 예보, 지역 이벤트, 공휴일 조회 |
    
    시나리오에 필요한 Tool만 System Prompt에서 언급하세요 — Agent는 프롬프트를 보고 Tool을 고릅니다.

---

## 2-2. Agent 코드: `agents/phase2b/app/phase2b/main.py`

코드 골격은 아래와 같습니다. **System Prompt를 여러분의 시나리오에 맞게 수정하는 것**이 이 Step의 핵심 작업입니다:

```python
import os
from strands import Agent
from strands.models.bedrock import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from bedrock_agentcore.runtime import BedrockAgentCoreApp

app = BedrockAgentCoreApp()

GATEWAY_URL = os.environ.get("AGENTCORE_GATEWAY_URL", "")
REGION = os.environ.get("AWS_REGION", "us-west-2")

model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6",
    region_name=REGION,
)

# MCPClient는 모듈 로드 시 1회만 생성 (요청마다 재생성하면 매번 핸드셰이크 비용)
mcp_client = MCPClient(lambda: streamablehttp_client(GATEWAY_URL)) if GATEWAY_URL else None


# ╔══════════════════════════════════════════════════════╗
# ║  여기를 수정하세요: 여러분의 시나리오를 담은 Prompt    ║
# ╚══════════════════════════════════════════════════════╝
SYSTEM_PROMPT = """당신은 리테일 매장의 시장 정보 수집 분석가입니다.

## 역할
- 사용자의 질문에 대해 날씨, 이벤트, 재고, 트렌드 등 관련 정보를 수집하여 답변합니다
- 여러 정보원을 조합해 매장 운영에 유용한 인사이트를 제공합니다

## 사용할 수 있는 정보원 (Gateway Tools)
- 날씨 예보/지역 이벤트/공휴일은 external_factors 도구로 조회하세요
- 재고 현황은 inventory_status 도구로 조회하세요
- 판매 트렌드는 sales_trend 도구로 조회하세요
- 매장 ID를 모르면 기본값 store-001 을 사용하세요

## 응답 규칙
- 질문에 관련된 정보원만 선택적으로 사용합니다 (모두 호출할 필요 없음)
- Tool 결과에 없는 정보는 절대 지어내지 않습니다
"""


@app.entrypoint
async def invoke(payload, context):
    prompt = payload.get("prompt", "") or payload.get("message", "") or payload.get("input", "")
    if not prompt.strip():
        yield {"event": "error", "data": "프롬프트가 비어 있습니다."}
        return

    tools = [mcp_client] if mcp_client else []
    agent = Agent(model=model, system_prompt=SYSTEM_PROMPT, tools=tools)

    async for event in agent.stream_async(prompt):
        if not isinstance(event, dict) or "event" not in event:
            continue
        yield event


if __name__ == "__main__":
    app.run()
```

!!! tip "이 코드에서 눈여겨볼 것 (Phase 3에서 그대로 씁니다)"
    1. **모듈 레벨 MCPClient** — Gateway 연결은 1회만
    2. **async generator + yield** — 스트리밍 응답
    3. **System Prompt로 Tool 사용 시점을 지시** — Agent는 프롬프트를 읽고 어떤 Tool을 쓸지 판단
    
    코드 구조는 그대로 두고 **System Prompt만 바꿔도 완전히 다른 Agent**가 됩니다.

!!! note "Memory가 없습니다"
    Phase 2A와 달리 이 Agent에는 Memory 연동이 없습니다 — 의도적입니다.
    Memory는 Phase 3 Step 4에서 **여러분이 직접** 나만의 Agent에 연동합니다.

---

## 2-3. 배포

```bash
cd ~/workshop/starter-code
./scripts/deploy-agent.sh phase2b
```

!!! note "환경변수 자동 전달"
    `deploy-agent.sh`가 `AGENTCORE_GATEWAY_URL`, `AWS_REGION`을
    `agentcore.json`에 주입한 뒤 `agentcore deploy`를 실행합니다.

배포 상태 확인:

```bash
cd agents/phase2b
agentcore status
```

---

## 2-4. 테스트 — 나의 테스트 질문으로

2-1에서 정한 테스트 질문으로 호출합니다:

```bash
cd ~/workshop/starter-code/agents/phase2b
agentcore invoke --prompt "이번 주 날씨와 이벤트 알려줘"
```

**응답 확인 포인트:**

- `external_factors` Tool이 호출되어 날씨/이벤트 데이터가 응답에 포함되는가
- System Prompt에 적은 응답 규칙대로 답하는가
- Tool 결과에 없는 내용을 지어내지 않았는가

시나리오와 다르게 동작하면 System Prompt를 수정하고 재배포하세요 — 이 "프롬프트 수정 → 재배포 → 확인" 사이클이 Agent 개발의 기본 리듬입니다.

---

## 2-5. Agent Playground에 연결

배포 시 출력된 **Agent ARN**을 Playground에 등록하면 웹 화면에서 대화할 수 있습니다:

1. Playground 접속 → **⚙️ Settings** → **Phase 2 Agent** 입력란에 Agent ARN 붙여넣기 → **저장**

![Agent 설정 화면](../assets/images/playground/playground-settings.png)

2. 채팅창에서 테스트 질문 외에 다양한 질문을 던져보세요 — 시나리오 밖 질문에 Agent가 어떻게 반응하는지 보는 것도 중요한 검증입니다

---

## 2-6. Trace 확인 (Observability)

AWS Console > CloudWatch > Application Signals > GenAI Dashboard에서 방금 호출의 Trace를 확인합니다.

내 시나리오에 따라 다르지만, 대략 이런 흐름이 보입니다:

```
1. [Gateway] external_factors — 날씨/이벤트 조회
2. [Gateway] inventory_status — 재고 확인 (필요 시)
3. [LLM] 최종 응답 생성
```

!!! note "Agent가 스스로 판단합니다"
    Agent는 여러분의 질문과 System Prompt를 보고 필요한 Tool을 **자율적으로 선택**합니다.
    설계한 Tool이 호출되지 않았다면 System Prompt에서 그 Tool의 사용 시점을 더 명확히 써주세요.

---

## 검증 체크리스트

- [ ] 시나리오(역할 한 줄 + 테스트 질문) 정함
- [ ] System Prompt에 내 시나리오 반영
- [ ] `./scripts/deploy-agent.sh phase2b` 성공
- [ ] `agentcore invoke` 응답이 내 시나리오대로 동작
- [ ] Playground에서 대화 가능
- [ ] Trace에서 Gateway Tool 호출 확인

---

!!! success "Phase 2B 완료! 재료 준비 끝"
    여러분의 Agent는 이제 **날씨/이벤트/재고/트렌드 데이터를 조합**할 수 있습니다.

    | 준비된 재료 | 내용 |
    |------------|------|
    | Gateway Tool 7개 | 고객/상품/구매이력 + 재고/트렌드/외부요인/발주 |
    | 참고 코드 | `agents/phase2b/app/phase2b/main.py` (배포 검증 완료) |

    점심 후 [Phase 3: 바이브코딩으로 나만의 Agent 만들기](../phase3/index.md)에서
    이 재료들을 조합해 시나리오를 더 크게 키워봅니다!
