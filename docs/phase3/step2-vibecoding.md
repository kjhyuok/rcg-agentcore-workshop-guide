# Step 2: 바이브코딩으로 구현하기 <span class="badge-time">⏱️ 25분</span> <span class="badge-difficulty">★★★</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 설계</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 2 바이브코딩</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 3 배포 & 테스트</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 4 Memory 고도화</span>
</div>

::: info 이 Step의 목표
Step 1의 설계서를 AI 코딩 도구에 전달하여 `agents/phase3/app/phase3/main.py`를 생성합니다.

핵심 공식: **설계서 + 동작하는 참고 코드 + 명확한 제약 = 좋은 Agent 코드**
:::


<div class="file-target">agents/phase3/app/phase3/main.py</div>

## 2-1. 바이브코딩이란

자연어로 의도를 설명하면 AI가 코드를 작성하고, 사람은 **방향 제시와 검증**에 집중하는 개발 방식입니다.

사용할 도구는 자유입니다:

| 도구 | 사용 방법 |
|------|----------|
| **Claude Code** | 터미널에서 `claude` 실행 후 프롬프트 입력 |
| **Amazon Q Developer** | VS Code 확장의 채팅창에 프롬프트 입력 |
| **Kiro** | Kiro IDE/CLI에서 프롬프트 입력 |
| **웹 기반 챗** | 프롬프트 + 참고 코드를 붙여넣고, 생성된 코드를 파일로 복사 |

::: tip 도구보다 중요한 것
바이브코딩의 품질은 도구가 아니라 **AI에게 주는 컨텍스트**가 결정합니다.
"Agent 만들어줘"라고만 하면 AI는 존재하지 않는 API를 상상해서 씁니다.
**동작이 검증된 참고 코드**와 **명확한 제약 조건**을 함께 주는 것이 핵심입니다.
:::

## 2-2. AI에게 줄 컨텍스트 3가지

바이브코딩을 시작하기 전에 아래 3가지를 준비합니다:

| # | 컨텍스트 | 어디서 가져오나 |
|---|---------|---------------|
| 1 | **설계서** | Step 1에서 작성한 `~/workshop/starter-code/my-agent-design.md` |
| 2 | **참고 코드** | 내 트랙에서 배포에 성공한 Agent 코드 — 2A 트랙: `agents/phase2a/app/phase2a/main.py` / 2B 트랙: `agents/phase2b/app/phase2b/main.py` |
| 3 | **제약 조건** | 아래 2-3의 프롬프트에 포함된 5가지 제약 |

::: warning 참고 코드가 왜 필수인가요?
AgentCore SDK는 비교적 새로운 라이브러리라서, AI가 학습하지 못한 부분을 그럴듯하게 지어낼 수 있습니다.
오늘 **여러분이 직접 배포에 성공한 코드**를 참고 코드로 주면, AI는 검증된 구조 위에서 역할만 바꿉니다.
이것이 30분 안에 동작하는 Agent를 만드는 비결입니다.
:::

## 2-3. 프롬프트 예시 (복사해서 사용)

### ① 초기 생성 프롬프트

AI 코딩 도구에 아래 프롬프트를 입력하세요. Claude Code처럼 파일을 직접 읽는 도구라면 설계서와 참고 코드는 **경로만** 알려주면 되고, 웹 챗이라면 파일 내용을 함께 붙여넣으세요.

```text
설계서: ~/workshop/starter-code/my-agent-design.md 를 읽고,
그 설계서대로 ~/workshop/starter-code/agents/phase3/app/phase3/main.py 를 만들어줘.
참고 코드: ~/workshop/starter-code/agents/phase2a/app/phase2a/main.py (동작 검증된 코드야. 이 구조를 그대로 따라줘)

반드시 지켜야 할 제약:
1. BedrockAgentCoreApp + @app.entrypoint 의 async generator(yield 스트리밍) 구조는
   참고 코드와 완전히 동일하게 유지해줘.
2. Gateway 연결은 참고 코드처럼 모듈 레벨에서 1회만:
   MCPClient(lambda: streamablehttp_client(os.environ.get("AGENTCORE_GATEWAY_URL", "")))
3. 모델은 us.anthropic.claude-sonnet-4-6, region은 os.environ.get("AWS_REGION", "us-west-2").
4. Browser를 쓴다면 참고 코드의 지연 생성 싱글톤 get_browser_tool() 패턴을 그대로 사용해줘
   (import 시점에 만들면 콜드스타트 타임아웃에 걸려).
5. Memory 연동 코드는 아직 넣지 마. (Step 4에서 추가할 거야)

바꿔야 할 것은 System Prompt(설계서의 역할/응답 규칙 반영)와
설계서에 없는 Tool 사용 지시 제거뿐이야. 참고 코드에 없는 패키지는 import하지 마.
```

::: info 웹 챗을 쓴다면
파일 경로를 읽을 수 없으므로, `my-agent-design.md`의 내용과 참고 코드(main.py) 전체를
프롬프트 아래에 직접 붙여넣으세요.
:::


### ② 반복 개선 프롬프트

첫 코드가 나오면, 대화로 다듬습니다:

```text
System Prompt에 응답 형식 규칙을 추가해줘:
분석 결과는 markdown 표로 정리하고, 마지막에 "추천 액션" 섹션을 넣어줘.
```

```text
지금은 Tool을 너무 많이 호출해. System Prompt에
"inventory_status와 sales_trend 두 가지만 사용하고,
그 외 Tool은 호출하지 말 것"이라고 명시해줘.
```

### ③ 디버깅 프롬프트

에러가 나면 에러 메시지를 그대로 붙여넣습니다:

```text
agents/phase3/app/phase3/main.py를 실행하니 아래 에러가 나. 원인을 찾아서 고쳐줘.
참고 코드(agents/phase2a/app/phase2a/main.py)는 정상 동작하니까, 참고 코드와 다른 부분을 의심해봐.

(에러 메시지 전체 붙여넣기)
```

::: tip 바이브코딩 진행 팁
- **한 번에 하나씩** — "생성 → 확인 → 개선 요청" 사이클을 짧게 반복하세요
- **AI의 설명을 읽으세요** — 코드가 왜 그렇게 생겼는지 이해해야 Step 3에서 디버깅할 수 있습니다
- **참고 코드와 diff** — 생성된 코드와 참고 코드를 나란히 놓고, 구조가 달라진 곳이 있으면 의심하세요
:::

## 2-4. (Fallback) AI 도구가 없다면: 템플릿 복사 → 3가지만 수정

::: details 🧪 직접 수정 템플릿 (바이브코딩 결과물의 검증 기준으로도 활용하세요)

AI 도구를 쓸 수 없거나, 생성된 코드가 미덥지 않다면 이 템플릿에서 시작하세요.
**같은 Tool이라도 System Prompt와 Tool 조합이 다르면 완전히 다른 Agent**가 됩니다.

```python
# agents/phase3/app/phase3/main.py
import os
import uuid
import threading
from strands import Agent
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp.client.streamable_http import streamablehttp_client
from bedrock_agentcore.runtime import BedrockAgentCoreApp

# --- 설정 ---
GATEWAY_URL = os.environ.get("AGENTCORE_GATEWAY_URL", "")
REGION = os.environ.get("AWS_REGION", "us-west-2")

model = BedrockModel(
    model_id="us.anthropic.claude-sonnet-4-6",
    region_name=REGION,
)

# MCPClient는 모듈 로드 시 1회만 생성
mcp_client = MCPClient(lambda: streamablehttp_client(GATEWAY_URL))

# Browser Tool은 지연 생성 + 싱글톤 캐싱 (콜드스타트 타임아웃 예방)
_browser_tool = None
_browser_tool_lock = threading.Lock()


def get_browser_tool():
    global _browser_tool
    if _browser_tool is None:
        with _browser_tool_lock:
            if _browser_tool is None:
                from strands_tools.browser import AgentCoreBrowser
                _browser_tool = AgentCoreBrowser(region=REGION)
    return _browser_tool

# ╔══════════════════════════════════════════════╗
# ║  수정 포인트 1: System Prompt (설계서 반영)   ║
# ╚══════════════════════════════════════════════╝
SYSTEM_PROMPT = """당신은 [설계서의 한 줄 설명]입니다.

## 역할
- [구체적인 역할 설명]

## 사용 가능한 도구
- [Tool 1]: [언제 사용하는지]
- [Tool 2]: [언제 사용하는지]

## 응답 규칙
- [설계서의 응답 규칙 1]
- [설계서의 응답 규칙 2]
- Tool 결과에 없는 정보는 절대 지어내지 않습니다
"""

# ╔══════════════════════════════════════════════╗
# ║  수정 포인트 2: 사용할 추가 Tool 선택         ║
# ╚══════════════════════════════════════════════╝
def build_tools():
    tools = [mcp_client]                       # Gateway Tools (항상 포함)
    # tools.append(get_browser_tool().browser)  # Browser가 필요하면 주석 해제
    return tools

# ╔══════════════════════════════════════════════╗
# ║  수정 포인트 3: Memory의 기억 주체            ║
# ║  (Step 4에서 사용 — 지금은 주석만 남겨두세요) ║
# ╚══════════════════════════════════════════════╝
# Memory 연동은 Step 4에서 추가합니다.
# actor_id로 무엇을 쓸지(고객 ID? 매장 ID?)만 설계서에서 정해두세요.


# --- Runtime Entrypoint ---
app = BedrockAgentCoreApp()


@app.entrypoint
async def my_agent(payload: dict):
    user_message = payload.get("message", "")
    session_id = payload.get("session_id", f"sess-{uuid.uuid4()}")

    agent = Agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        tools=build_tools(),
    )

    # return 대신 yield — 토큰이 생성되는 즉시 스트리밍
    full_text = ""
    async for event in agent.stream_async(user_message):
        chunk = event.get("data")
        if chunk:
            full_text += chunk
            yield {"type": "chunk", "response": chunk, "session_id": session_id}

    yield {"type": "done", "response": full_text, "session_id": session_id}


if __name__ == "__main__":
    app.run()
```

수정하는 것은 딱 3곳입니다:

1. **System Prompt** — 설계서의 역할/응답 규칙 반영
2. **build_tools()** — Browser/Code Interpreter 필요 시 추가
3. **Memory 주석** — 기억의 주체(actor_id)만 정해두기 (연동은 Step 4에서)

:::

## 2-5. 완성 체크리스트

배포 전에 아래를 확인하세요:

```bash
cd ~/workshop/starter-code

# 문법 오류 확인 (통과하면 아무 출력 없음)
python3.12 -m py_compile agents/phase3/app/phase3/main.py && echo "✅ 문법 OK"
```

- [ ] `@app.entrypoint`가 붙은 async generator 함수가 있다 (`yield` 사용)
- [ ] `AGENTCORE_GATEWAY_URL`을 환경변수에서 읽는다 (하드코딩 ❌)
- [ ] region이 `AWS_REGION` 환경변수 기반이다 (us-west-2)
- [ ] 참고 코드에 없는 패키지를 import하지 않았다
- [ ] Browser를 쓴다면 지연 생성 패턴(`get_browser_tool()`)이다
- [ ] `python3.12 -m py_compile` 통과

::: warning 25분 타이머
완벽한 코드보다 **배포되는 코드**가 우선입니다.
체크리스트를 통과하면 바로 Step 3으로 — 세부 개선은 배포 후에도 할 수 있습니다.
:::


---

::: tip ✅ 다음
코드 완성! → [Step 3: Runtime 배포 & Playground 테스트](step3-deploy.md)
:::

