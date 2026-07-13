# Step 3: Agent + Memory 연동 <span class="badge-time">⏱️ 20분</span> <span class="badge-difficulty">★★★</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 Memory</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 2 Gateway+Browser</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 3 Agent</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 4 Policy</span>
</div>

!!! info "이 Step의 목표"
    Agent에 **Memory를 연동**하여 고객 맥락을 기억하게 합니다.
    
    패턴: Memory 조회 → 프롬프트에 주입 → Agent 실행 → 대화 기록 저장

<div class="file-target">agents/phase2a_cs.py</div>
---

## 핵심 패턴

```python
# Phase 1: 상태 없는 Agent
agent("주문 조회해주세요")  # 매번 새로운 대화

# Phase 2A: Memory 연동 Agent
context = fetch_customer_context(actor_id, message)   # 이전 맥락 가져오기 (retrieve_memory_records)
agent(message, context=context)                        # 맥락과 함께 실행
save_turn(actor_id, session_id, message, response)     # 이번 대화 저장 (create_event)
```

Agent 호출 **전후**로 Memory 작업이 추가됩니다.

---

## 3-1. agents/phase2a_cs.py 열기

핵심 구조를 확인합니다:

```python title="agents/phase2a_cs.py — Import & 설정"
import os
import uuid
import boto3
from datetime import datetime, timezone
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from strands_tools.browser import AgentCoreBrowser
from mcp.client.streamable_http import streamablehttp_client
from bedrock_agentcore.runtime import BedrockAgentCoreApp

GATEWAY_URL = os.environ.get("AGENTCORE_GATEWAY_URL", "")
MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_ID", "")
REGION = os.environ.get("AWS_REGION", "us-east-1")

model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6",
    region_name=REGION,
)

memory_client = boto3.client("bedrock-agentcore", region_name=REGION)
browser_tool = AgentCoreBrowser(region=REGION)
```

---

## 3-2. Memory 조회 함수

Agent 호출 **전에** 고객의 이전 맥락을 가져옵니다:

```python title="Memory에서 고객 맥락 가져오기"
def fetch_customer_context(actor_id: str, query: str) -> str:
    """Memory에서 이 고객의 이전 맥락을 검색"""
    if not MEMORY_ID:
        return "신규 고객 (Memory 미설정)"
    try:
        results = memory_client.retrieve_memory_records(
            memoryId=MEMORY_ID,
            namespace=f"/users/{actor_id}/facts/",
            searchCriteria={
                "searchQuery": query,
                "topK": 5,
            },
        )
        records = results.get("memoryRecordSummaries", [])
        if records:
            return "\n".join(r["content"]["text"] for r in records)
    except Exception as e:
        print(f"[Memory Retrieve Error] {e}")
    return "신규 고객 (이전 맥락 없음)"
```

!!! tip "retrieve_memory_records의 동작"
    `searchQuery`로 **의미 기반 검색**을 합니다.
    
    "반품하고 싶어요"라고 물으면, 이전 대화에서 반품 관련 내용을 우선 검색합니다.

---

## 3-3. 대화 기록 저장 함수

Agent 응답 **후에** 이번 대화를 Memory에 저장합니다:

```python title="이번 대화를 Memory에 저장"
def save_turn(actor_id: str, session_id: str, user_msg: str, agent_response: str):
    """이번 턴(user + agent)을 Memory Event로 저장"""
    if not MEMORY_ID:
        return
    try:
        memory_client.create_event(
            memoryId=MEMORY_ID,
            actorId=actor_id,
            sessionId=session_id,
            eventTimestamp=datetime.now(timezone.utc),
            payload=[
                {"conversational": {"role": "USER", "content": {"text": user_msg}}},
                {"conversational": {"role": "ASSISTANT", "content": {"text": agent_response}}},
            ],
        )
    except Exception as e:
        print(f"[Memory Save Error] {e}")
```

!!! info "Event vs Record"
    - **Event**: 원본 대화 (user/assistant 메시지 쌍)
    - **Record**: Strategy가 Event에서 자동 추출한 결과 (선호, 요약, 사실)
    
    Event를 저장하면, Strategy가 백그라운드에서 Record를 자동 생성합니다.

---

## 3-4. Agent Entrypoint (전체 흐름)

```python title="Runtime Entrypoint — Memory 연동 패턴"
app = BedrockAgentCoreApp()

SYSTEM_PROMPT = """당신은 리테일 CS 전문 상담사입니다.

## 행동 규칙
1. 고객의 이전 맥락이 주어지면 참고하여 자연스럽게 응대
2. 주문 조회 → 상태 확인 → 적절한 안내
3. 반품 요청 시: 정책 확인 → 반품 처리 → 결과 안내
4. 5만원 초과 환불은 "CS 팀 리더 승인이 필요합니다"로 안내
5. 항상 공손하고 명확하게 답변

## 고객 맥락 (Memory에서 가져온 정보)
{customer_context}
"""

@app.entrypoint
def cs_agent(payload: dict) -> dict:
    user_message = payload.get("message", "")
    session_id = payload.get("session_id", f"sess-{uuid.uuid4()}")
    actor_id = payload.get("actor_id", "anonymous")

    # 1️⃣ Memory에서 고객 맥락 가져오기
    context = fetch_customer_context(actor_id, user_message)

    # 2️⃣ 맥락을 System Prompt에 주입
    prompt_with_context = SYSTEM_PROMPT.format(customer_context=context)

    # 3️⃣ Agent 실행 (Gateway MCP + Browser Tool)
    mcp_client = MCPClient(
        lambda: streamablehttp_client(GATEWAY_URL)
    )

    agent = Agent(
        model=model,
        system_prompt=prompt_with_context,
        tools=[mcp_client, browser_tool.browser],
    )
    result = agent(user_message)

    # 4️⃣ 이번 대화를 Memory에 저장
    save_turn(actor_id, session_id, user_message, str(result))

    return {
        "response": str(result),
        "session_id": session_id,
    }


if __name__ == "__main__":
    app.run()
```

---

## 3-5. 배포

```bash
cd ~/workshop/starter-code
chmod +x scripts/*.sh
./scripts/deploy-agent.sh agents/phase2a_cs.py rcg_cs_agent
```

!!! note "Memory ID 전달"
    `deploy-agent.sh`가 `AGENTCORE_GATEWAY_URL`, `AGENTCORE_MEMORY_ID`, `AWS_REGION`을 모두 자동으로 Runtime 환경변수에 전달합니다.
    실행 전에 `echo $AGENTCORE_MEMORY_ID`로 값이 비어있지 않은지 먼저 확인하세요.

!!! warning "RUNTIME_ROLE_ARN 확인 필수"
    `RUNTIME_ROLE_ARN`은 `./infra/onestop.sh`가 CloudShell에서 생성한 값으로, `.env.w001`에 저장되어 있습니다.
    Code Editor 터미널을 새로 열었다면 반드시 `source ~/workshop/.env.w001` 후 `echo $RUNTIME_ROLE_ARN`으로 값이 채워졌는지 확인하세요.
    이 값이 비어있으면 Memory 접근 권한이 없는 Role로 잘못 배포될 수 있어, `deploy-agent.sh`가 값이 없을 경우 즉시 에러로 중단하도록 되어 있습니다.

---

## 3-6. 테스트 (Memory 동작 확인)

!!! tip "테스트 방법"
    같은 터미널에서 순서대로 실행합니다. `session_id`만 다르게 — 실제 고객이 채팅창을 닫고 다시 열었을 때를 시뮬레이션합니다.

**첫 번째 대화:**

```bash
agentcore invoke --agent rcg_cs_agent \
  '{"message": "주문 ORD-20260620-001 배송 상태 확인해주세요", "actor_id": "C001", "session_id": "cs-test-001"}'
```

**두 번째 대화 (같은 고객, 새 세션):**

```bash
agentcore invoke --agent rcg_cs_agent \
  '{"message": "아까 그 주문 반품하고 싶어요", "actor_id": "C001", "session_id": "cs-test-002"}'
```

??? success "Memory 연동 확인 포인트"
    두 번째 대화에서 Agent가:
    
    - "아까 그 주문" = ORD-20260620-001을 **기억**하고 있음
    - 주문번호를 다시 물어보지 않음
    - Memory에서 이전 세션의 맥락을 가져왔기 때문
    
    ```
    🤖 Agent: ORD-20260620-001 반품을 도와드리겠습니다.
    지난번 배송 확인하셨던 유기농 프로틴바 주문이시죠?
    반품 사유를 알려주시겠어요?
    ```

---

## 3-7. Trace 비교 (Observability)

Phase 1 Trace와 비교해봅니다:

```
Phase 1 Trace:
  AGENT_START → TOOL_CALL(product_search) → TOOL_CALL(...) → AGENT_END

Phase 2A Trace:
  MEMORY_RETRIEVE → AGENT_START → TOOL_CALL(lookup_order) → AGENT_END → MEMORY_SAVE
  ^^^^^^^^^^^^^^^^^^                                                      ^^^^^^^^^^^^
  새로 추가된 Memory 스팬
```

!!! info "Memory 스팬이 보임"
    Observability에서 `MEMORY_RETRIEVE`와 `MEMORY_SAVE` 스팬을 확인할 수 있습니다.
    
    - `MEMORY_RETRIEVE`: 몇 개의 record를 가져왔는지, 검색 시간
    - `MEMORY_SAVE`: Event 저장 성공 여부

---

## 이해 체크

- [x] Memory 조회 → 프롬프트 주입 → Agent 실행 → 대화 저장 (4단계 패턴)
- [x] `retrieve_memories`는 의미 기반 검색 (현재 질문과 관련된 기억 우선)
- [x] `create_memory_event`로 대화를 저장하면 Strategy가 자동으로 Record 생성
- [x] Trace에 MEMORY 스팬이 추가됨

---

!!! success "다음"
    Memory 연동 완료! → [Step 4: Policy (에스컬레이션)](step4-policy.md)
