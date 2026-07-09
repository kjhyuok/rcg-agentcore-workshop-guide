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
memories = retrieve_memories(customer_id)   # 이전 맥락 가져오기
agent(message, context=memories)            # 맥락과 함께 실행
save_turn(customer_id, message, response)   # 이번 대화 저장
```

Agent 호출 **전후**로 Memory 작업이 추가됩니다.

---

## 3-1. agents/phase2a_cs.py 열기

핵심 구조를 확인합니다:

```python title="agents/phase2a_cs.py — Import & 설정"
from strands import Agent
from strands.models import BedrockModel
from mcp import ClientSession

from mcp.client.streamable_http import streamablehttp_client
from bedrock_agentcore.memory import MemoryClient
from bedrock_agentcore.runtime import BedrockAgentCoreApp

GATEWAY_URL = os.environ.get("AGENTCORE_GATEWAY_URL", "")
MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_ID", "")
REGION = "us-east-1"

model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6-20250514-v1:0",
    region_name=REGION,
)

memory_client = MemoryClient(region_name=REGION)
```

---

## 3-2. Memory 조회 함수

Agent 호출 **전에** 고객의 이전 맥락을 가져옵니다:

```python title="Memory에서 고객 맥락 가져오기"
def fetch_customer_context(customer_id: str, current_message: str) -> str:
    """Memory에서 이 고객의 이전 맥락을 검색"""
    
    # 의미 기반 검색 (현재 질문과 관련된 기억 우선)
    results = memory_client.retrieve_memories(
        memoryId=MEMORY_ID,
        query=current_message,
        actorId=customer_id,
        maxResults=5,
    )
    
    if not results.get("records"):
        return ""  # 첫 대화인 경우
    
    # 맥락을 텍스트로 조합
    context_parts = []
    for record in results["records"]:
        namespace = record.get("namespace", "")
        content = record.get("content", "")
        
        if "/preferences/" in namespace:
            context_parts.append(f"[고객 선호] {content}")
        elif "/summaries/" in namespace:
            context_parts.append(f"[이전 대화 요약] {content}")
        elif "/facts/" in namespace:
            context_parts.append(f"[참고 정보] {content}")
    
    return "\n".join(context_parts)
```

!!! tip "retrieve_memories의 동작"
    `query` 파라미터로 **의미 기반 검색**을 합니다.
    
    "반품하고 싶어요"라고 물으면, 이전 대화에서 반품 관련 내용을 우선 검색합니다.

---

## 3-3. 대화 기록 저장 함수

Agent 응답 **후에** 이번 대화를 Memory에 저장합니다:

```python title="이번 대화를 Memory에 저장"
def save_turn(customer_id: str, session_id: str, user_msg: str, agent_response: str):
    """이번 턴(user + agent)을 Memory Event로 저장"""
    
    memory_client.create_memory_event(
        memoryId=MEMORY_ID,
        actorId=customer_id,
        sessionId=session_id,
        messages=[
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": agent_response},
        ],
    )
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
    customer_id = payload.get("customer_id", "unknown")
    session_id = payload.get("session_id", f"sess-{uuid.uuid4()}")
    
    # 1️⃣ Memory에서 고객 맥락 가져오기
    context = fetch_customer_context(customer_id, user_message)
    
    # 2️⃣ 맥락을 System Prompt에 주입
    prompt = SYSTEM_PROMPT.format(customer_context=context or "없음 (첫 대화)")
    
    # 3️⃣ Agent 실행 (Gateway에서 Tool 로드)
    mcp = MCPClient(lambda: streamablehttp_client(GATEWAY_URL, auth=auth))
    
    with mcp:
        tools = mcp.list_tools_sync()
        agent = Agent(model=model, system_prompt=prompt, tools=tools)
        result = agent(user_message)
    
    response_text = str(result)
    
    # 4️⃣ 이번 대화를 Memory에 저장
    save_turn(customer_id, session_id, user_message, response_text)
    
    return {
        "response": response_text,
        "session_id": session_id,
        "memory_used": bool(context),
    }
```

---

## 3-5. 배포

```bash
./scripts/deploy-agent.sh agents/phase2a_cs.py rcg-cs-agent \
  --env AGENTCORE_MEMORY_ID=$AGENTCORE_MEMORY_ID
```

??? example "deploy-agent.sh가 하는 일"
    1. Agent 코드를 컨테이너로 패키징
    2. AgentCore Runtime에 배포 (or 업데이트)
    3. 환경변수 `AGENTCORE_MEMORY_ID`를 Runtime에 전달
    4. Endpoint URL 출력

배포 완료 후:

```
🚀 CS Agent 배포 완료!
   Runtime:  rcg-cs-agent
   Endpoint: https://rcg-cs-agent.runtime.agentcore.us-east-1.amazonaws.com
   
   export CS_AGENT_ENDPOINT=https://rcg-cs-agent.runtime...
```

---

## 3-6. 테스트 (Memory 동작 확인)

**첫 번째 대화:**

```bash
python3 scripts/invoke-agent.py \
  --endpoint "$CS_AGENT_ENDPOINT" \
  --customer-id "C001" \
  --message "주문 ORD-2024-789 배송이 어디쯤 왔는지 알 수 있을까요?"
```

**두 번째 대화 (같은 고객, 새 세션):**

```bash
python3 scripts/invoke-agent.py \
  --endpoint "$CS_AGENT_ENDPOINT" \
  --customer-id "C001" \
  --message "아까 그 주문 반품하고 싶어요"
```

??? success "Memory 연동 확인 포인트"
    두 번째 대화에서 Agent가:
    
    - "아까 그 주문" = ORD-2024-789를 **기억**하고 있음
    - 주문번호를 다시 물어보지 않음
    - Memory에서 이전 세션의 맥락을 가져왔기 때문
    
    ```
    🤖 Agent: ORD-2024-789 반품을 도와드리겠습니다.
    지난번 배송 추적하셨던 그 주문이시죠?
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
