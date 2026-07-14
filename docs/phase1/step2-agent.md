# Step 2: Agent 코드 작성 + 시나리오 테스트 <span class="badge-time">⏱️ 20분</span> <span class="badge-difficulty">★★☆</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 Gateway</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 2 Agent</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 3 Runtime</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 4 Observability</span>
</div>

!!! info "이 Step의 목표"
    Gateway에서 가져온 3개 Tool로 Agent를 구성하고, **여러 시나리오**로 호출하며
    Agent가 상황에 따라 Tool을 얼마나, 어떤 순서로 쓰는지 관찰합니다.

    Agent = Model + System Prompt + Gateway(Tools)

<div class="file-target">agents/phase1_recommend.py</div>

---

## 핵심 패턴

```python
# AgentCore Native Agent의 구조
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client

# Gateway를 MCPClient로 래핑 (Tool 목록을 자동으로 가져옴)
# 모듈 로드 시 1회만 생성 — 요청마다 새로 만들면 매번 MCP 핸드셰이크 비용이 붙음
mcp_client = MCPClient(lambda: streamablehttp_client(GATEWAY_URL))

# Agent 조립: Gateway(MCPClient)의 Tool을 그대로 전달
agent = Agent(
    model=model,
    system_prompt=SYSTEM_PROMPT,
    tools=[mcp_client]
)

# stream_async로 토큰이 생성되는 즉시 yield — 답을 다 만들 때까지 기다리지 않음
async for event in agent.stream_async("사용자 질문"):
    if event.get("data"):
        print(event["data"], end="")
```

`MCPClient`가 Gateway 연결과 Tool 목록 조회를 자동으로 처리합니다. Lambda ARN을 몰라도 됩니다.
Agent는 System Prompt의 분기 규칙에 따라, 고객 ID가 있으면 `customer_profile` → `purchase_history` → `product_search` 순서로, 없으면 `product_search`만 호출합니다.

!!! tip "agent(prompt) vs agent.stream_async(prompt)"
    `agent("질문")`은 Agent가 답을 전부 만든 뒤에야 결과를 반환합니다 — Tool 호출이 몇 번 도는 동안 아무 반응이 없어 느리게 느껴집니다.
    `agent.stream_async("질문")`은 토큰이 생성되는 즉시 하나씩 넘겨줍니다. `phase1_recommend.py`의 entrypoint는 이 방식을 씁니다(2-2 참고).

---

## 2-1. agents/phase1_recommend.py 열기

Step 1에서 쓰던 터미널을 그대로 이어서 사용하면 됩니다. venv 활성화는 필요 없습니다 — 워크샵 환경은 `python3.12`에 라이브러리가 직접 설치되어 있습니다.

터미널 세션이 끊겼거나 환경변수가 비어 있으면 다음만 다시 실행하세요:

```bash
cd ~/workshop/starter-code
source ~/workshop/.env.w001
```

Explorer에서 `starter-code/agents/phase1_recommend.py`를 클릭하여 코드를 확인하세요:

```python title="agents/phase1_recommend.py — 핵심 부분"
import os
import uuid
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# 환경변수 (agentcore deploy --env 로 주입)
GATEWAY_URL = os.environ.get("AGENTCORE_GATEWAY_URL", "")
REGION = os.environ.get("AWS_REGION", "us-west-2")

# MCPClient는 모듈 로드 시 1회만 생성 (요청마다 새로 만들면 매번 핸드셰이크 비용)
mcp_client = MCPClient(lambda: streamablehttp_client(GATEWAY_URL))

# 모델
model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6",
    region_name=REGION,
)
```

같은 파일에서 `SYSTEM_PROMPT`를 찾아보면, 4개 섹션으로 짜여 있습니다:

```python title="agents/phase1_recommend.py — SYSTEM_PROMPT"
SYSTEM_PROMPT = """당신은 리테일 상품 추천 전문가입니다.
고객의 선호도, 알러지, 구매 이력을 종합 분석하여 개인화된 상품을 추천합니다.

## 1. 조회 분기 — 질문 유형에 따라 다르게 시작
- 특정 고객 ID가 있는 질문 → customer_profile로 먼저 조회 (알러지/선호도 확인 없이는 추천 금지)
- 고객 ID가 없는 일반 질문("요즘 잘 나가는 상품은?") → product_search로 바로 답변 (프로필 조회 불필요)
- customer_profile 조회 결과가 없거나 에러 → "고객 ID를 찾을 수 없습니다"라고 답하고, 일반 인기 상품으로 대안 제안 (가상 프로필 생성 금지)

## 2. 추천 준비 (고객 ID가 있는 경우)
1. purchase_history 조회 → 이미 구매한 상품은 후보에서 제외
2. 선호 카테고리로 product_search (최대 2회, 결과가 부족해도 재검색으로 채우지 않음)
3. 알러지 성분 포함 상품은 후보에서 절대 제외

## 3. 데이터 무결성 — 위반 시 추천 전체가 무효
- 상품명·가격·평점·product_id는 반드시 Tool 응답에 있는 값만 사용 (Tool 호출 없이 아는 상품 언급 금지)
- 재고 0인 상품 제외
- 최종 후보가 3개 미만이면 있는 개수만 추천 (개수를 채우려고 상품을 지어내거나 이름을 바꾸지 않음)
- 최종 후보가 0개면 "추천 가능한 상품이 없습니다"라고 답하고, 조건을 완화하면 나올 대안(다른 카테고리 등)을 제안

## 4. 응답 규칙
- Tool 호출은 총 4회 이내 (프로필1 + 이력1 + 검색2), 고객 ID 없는 질문은 검색만 1~2회
- 추천 상품은 번호 매기기(1, 2, 3...)로 실제 개수만큼만, 각 상품에 추천 이유 1줄
- 알러지로 제외한 상품은 마지막에 별도 표기
- 장식용 헤딩(##)·표 없이 목록으로 간결하게, 이모지는 상품당 0~1개로 최소화
"""
```

!!! tip "섹션 순서 = 실행 흐름"
    "1. 조회 분기 → 2. 추천 준비 → 3. 데이터 무결성 → 4. 응답 규칙" 순서는 Agent가 실제로 판단하는 순서와 같습니다.
    질문 유형부터 먼저 나누고(1), 그 경로에서 데이터를 모으고(2), 모은 데이터를 검증하고(3), 마지막에 형식을 맞추는(4) 구조라 어떤 규칙이 언제 적용되는지 추적하기 쉽습니다.

---

## 2-2. Gateway 연결 + entrypoint 코드

Agent가 Gateway에서 Tool을 가져와 호출하는 핵심 코드:

```python title="agents/phase1_recommend.py 내부"
@app.entrypoint
async def recommend_agent(payload: dict):
    user_message = payload.get("message", payload.get("prompt", ""))
    session_id = payload.get("session_id", f"sess-{uuid.uuid4()}")

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=[mcp_client],
    )

    # return 대신 yield — 토큰이 생성되는 즉시 흘려보냄 (SSE 스트리밍)
    full_text = ""
    async for event in agent.stream_async(user_message):
        chunk = event.get("data")
        if chunk:
            full_text += chunk
            yield {"type": "chunk", "response": chunk, "session_id": session_id}

    yield {"type": "done", "response": full_text, "session_id": session_id}
```

!!! info "MCPClient가 하는 일"
    `MCPClient`는 Gateway URL에 연결하여 등록된 Tool 목록을 자동으로 가져옵니다. 비동기 연결, 세션 관리, Tool 목록 조회를 모두 내부에서 처리하므로 `asyncio.run()`을 직접 호출할 필요가 없습니다. Runtime 내부에서는 IAM Role 기반으로 인증됩니다.

!!! info "entrypoint가 async generator인 이유"
    함수가 `return`이 아니라 `yield`를 쓰면, `BedrockAgentCoreApp`이 이를 자동으로 SSE(Server-Sent Events) 스트리밍 응답으로 변환합니다.
    참가자가 `agentcore invoke`로 호출하면 답을 다 만들 때까지 기다리지 않고, 토큰이 생성되는 즉시 화면에 흘러나옵니다 (3-3 참고).

!!! tip "System Prompt = Agent의 행동을 결정하는 핵심"
    같은 Tool이라도 Prompt가 다르면 Agent의 행동이 완전히 달라집니다.

    - "3. 데이터 무결성"의 알러지 제외 규칙이 없으면 → 견과류 상품도 추천할 수 있음
    - "1. 조회 분기"의 분기 규칙이 없으면 → 고객 ID 유무와 상관없이 항상 같은 순서로 Tool을 호출할 수 있음

---

## 2-3. 로컬 테스트 — 여러 시나리오로 Tool 호출 전략 관찰

배포 전에 로컬에서 동작을 확인합니다:

```bash
cd ~/workshop/starter-code/agents/phase1
agentcore dev --no-browser
```

해당 명령어를 실행하면 아래와 Terminal에서 Agent를 테스트 해볼수 있습니다.
![Open Folder](../assets/images/phase1/phase1_2-3.png)

같은 Agent에게 아래 4가지 시나리오를 순서대로 입력해보고, **매번 Tool을 어떤 순서·횟수로 호출하는지** 비교하세요.

### 시나리오 1 — 기본 추천 (알러지 고려)

```bash
고객 C001에게 적합한 상품 3개 추천해주세요. 알러지 고려해서요
```

??? success "정상 출력 예시"
    ![Open Folder](../assets/images/phase1/phase1_2-3-result.png)

    조건을 만족하는 상품이 3개보다 적으면 Agent는 있는 만큼만 추천합니다 — 억지로 3개를 채우려고 존재하지 않는 상품을 만들어내지 않도록 System Prompt에 명시되어 있습니다.

    !!! warning "스크린샷은 예전 SYSTEM_PROMPT 버전 결과입니다"
        위 이미지는 "4. 응답 규칙"(장식용 헤딩·이모지 최소화) 반영 전에 캡처된 것이라, `##` 헤딩과 이모지가 많이 보입니다.
        실제로 실행하면 지금의 SYSTEM_PROMPT에 따라 더 간결한 목록 형태로 나와야 정상입니다 — 스크린샷과 다르게 나온다고 오류로 오해하지 마세요.

### 시나리오 2 — 목록에 없는 고객 ID

```bash
고객 C099에게 상품을 추천해주세요
```

!!! tip "C099는 워크샵 Mock 데이터에 없는 임의의 ID입니다"
    SYSTEM_PROMPT "1. 조회 분기"의 세 번째 규칙(`customer_profile 조회 결과가 없거나 에러 → ...`)이 바로 이 상황을 위한 지시입니다.

**관찰 포인트**: `customer_profile` 조회 결과가 비었을 때 Agent가 "고객 ID를 찾을 수 없습니다"라고 정직하게 답하는지, 아니면 규칙을 어기고 가상의 알러지/선호도를 지어내 추천을 진행하는지 확인하세요. 지어낸다면 프롬프트의 "가상 프로필 생성 금지" 지시가 지켜지지 않은 것입니다.

### 시나리오 3 — 조건을 만족하는 상품이 0개인 경우

```bash
고객 C001에게 견과류 성분이 들어간 상품만 추천해주세요
```

**관찰 포인트**: "3. 데이터 무결성"의 "알러지 성분 포함 상품은 후보에서 절대 제외" 규칙과 "견과류만 추천해달라"는 사용자 요청이 정면으로 충돌합니다. Agent가 규칙을 우선시해서 "추천 가능한 상품이 없습니다"라고 답하는지, 아니면 사용자 요청에 따라 규칙을 어기는지 확인하세요.

### 시나리오 4 — 모호한 질문 (Tool 호출 범위 판단)

```bash
요즘 잘 나가는 상품이 뭐예요?
```

!!! tip "SYSTEM_PROMPT가 이 케이스를 명시적으로 분기합니다"
    "1. 조회 분기"의 두 번째 규칙(`고객 ID가 없는 일반 질문 → product_search로 바로 답변`)이 정답을 정해두고 있습니다.

**관찰 포인트**: Agent가 `customer_profile`을 호출하지 않고 `product_search`만으로 곧바로 답하는지 확인하세요. 만약 고객 ID를 되묻거나 프로필을 먼저 조회하려 한다면, 프롬프트의 분기 규칙이 지켜지지 않은 것입니다.

---

## 관찰 포인트 정리

!!! abstract "4가지 시나리오에서 공통으로 확인할 것"
    - ✅ Agent가 Gateway를 통해 **3개 Tool을 자동으로 인식**했는가?
    - ✅ "1. 조회 분기" 규칙대로 질문 유형에 따라 Tool 호출 경로가 달라지는가 (시나리오 1·2 vs 시나리오 4)?
    - ✅ "3. 데이터 무결성" 규칙대로, 조회 결과가 비어있거나 조건에 안 맞을 때 있는 그대로 정직하게 답하는가 (지어내지 않는가)?
    - ✅ SYSTEM_PROMPT의 규칙과 사용자 요청이 충돌할 때(시나리오 3) 규칙을 우선하는가?

    Step 4의 Observability에서 이 시나리오들의 Trace를 다시 확인하며 "왜 이렇게 호출했는지"를 검증합니다.

---

!!! success "다음"
    Agent 동작 확인! → [Step 3: Runtime 배포](step3-runtime.md)
