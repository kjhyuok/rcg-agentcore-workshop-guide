# Step 3: Runtime 배포 & Playground 테스트 <span class="badge-time">⏱️ 15분</span> <span class="badge-difficulty">★★☆</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 설계</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 2 바이브코딩</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 3 배포 & 테스트</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 4 Memory 고도화</span>
</div>

::: info 이 Step의 목표
바이브코딩으로 만든 `my_agent.py`를 AgentCore Runtime에 배포하고,
설계서의 테스트 질문으로 검증한 뒤 Playground에 연결합니다.
:::


<div class="file-target">agents/phase3/app/phase3/main.py</div>

## 3-1. 배포

Phase 1~2에서 사용한 배포 스크립트를 그대로 사용합니다:

```bash
cd ~/workshop/starter-code
./scripts/deploy-agent.sh phase3
```

배포가 완료되면 상태와 ARN을 확인합니다:

```bash
cd agents/phase3
agentcore status
```

::: details ✅ 정상 출력 예시
```
AgentCore Status (target: default, us-west-2)

Agents
phase3: Deployed - Runtime: READY (arn:aws:bedrock-agentcore:us-west-2:123456789012:runtime/phase3_phase3-xxxxxxxxxx)
URL: https://bedrock-agentcore.us-west-2.amazonaws.com/runtimes/.../invocations
```
:::


출력된 ARN을 환경변수로 저장해두세요 (setup의 `.env.w001` Phase 3 블록):

```bash
export MY_AGENT_ARN=<위 출력에 나온 실제 ARN>
```

::: warning RUNTIME_ROLE_ARN 확인
터미널을 새로 열었다면 `source ~/workshop/.env.w001` 후
`echo $RUNTIME_ROLE_ARN`으로 값이 채워져 있는지 확인하세요.
비어 있으면 `deploy-agent.sh`가 에러로 중단됩니다.
:::

## 3-2. 테스트 호출

**Step 1 설계서에 적은 테스트 질문**으로 호출합니다:

```bash
cd ~/workshop/starter-code/agents/phase3
agentcore invoke --prompt "여기에 설계서의 테스트 질문"
```

::: info 출력이 여러 줄의 JSON으로 나옵니다
entrypoint가 async generator라서 이벤트가 여러 번 출력됩니다 (Phase 1 Step 3-3 참고).
:::

## 3-3. 에러가 나면? (트러블슈팅)

::: warning 흔한 실수 Top 4

1. **Tool 이름 오타** — System Prompt에 `prodcut_search` 같은 typo. 설계서의 Tool 이름과 [Step 1의 Tool 팔레트](step1-design.md)를 대조하세요
2. **환경변수 누락** — `AGENTCORE_GATEWAY_URL` 미설정. `source ~/workshop/.env.w001` 후 재배포
3. **import 에러** — AI가 존재하지 않는 패키지를 import한 경우. **바이브코딩 특유의 에러입니다** — AI 도구에게 "참고 코드(agents/phase2a/app/phase2a/main.py)의 import 블록만 사용해서 다시 써줘"라고 요청하세요
4. **콜드스타트 타임아웃** — Browser를 import 시점에 즉시 생성한 경우. 지연 생성 패턴(`get_browser_tool()`)으로 고쳐달라고 요청하세요

```bash
# 로그 확인
agentcore logs --name my_agent --tail 50
```
:::


::: tip 에러도 바이브코딩으로 해결
에러 메시지를 그대로 AI 도구에 붙여넣으세요 (Step 2-3의 디버깅 프롬프트).
"참고 코드는 정상 동작한다"는 사실을 알려주면 AI가 diff 관점에서 원인을 빨리 찾습니다.
:::

## 3-4. Agent Playground에 연결

CLI 테스트가 통과했다면, 웹 화면에서 대화형으로 테스트합니다:

1. Playground 접속 → **⚙️ Settings** → **Custom Agent** 입력란에 `MY_AGENT_ARN` 붙여넣기 → **저장**

![Agent 설정 화면](../assets/images/playground/playground-settings.png)

2. 채팅창에서 설계서의 테스트 질문을 입력하고, 응답이 **응답 규칙**대로 나오는지 확인

3. 설계서에 없는 질문도 던져보세요 — Agent가 범위 밖 질문을 어떻게 처리하는지 보는 것도 중요한 검증입니다

## 3-5. Observability로 내 Agent 들여다보기

AWS Console > CloudWatch > Application Signals > GenAI Dashboard에서 방금 호출의 Trace를 확인합니다:

```mermaid
sequenceDiagram
    participant RT as Runtime
    participant LLM as My Agent (LLM)
    participant GW as Gateway

    RT->>LLM: call #1 — 요청 분석
    LLM->>GW: tool_call: (설계서의 Tool 1)
    GW-->>LLM: 데이터
    LLM->>GW: tool_call: (설계서의 Tool 2)
    GW-->>LLM: 데이터
    RT->>LLM: call #2 — 최종 응답 생성
    Note over RT: 설계서에 적은 Tool들이 실제로 호출되는지 확인!
```

**확인 포인트:**

- 설계한 Tool이 실제로 호출되는가? (안 쓰이는 Tool이 있다면 System Prompt에서 사용 시점을 더 명확히)
- 불필요한 Tool 호출이 반복되는가? (응답 규칙에 "N개 이하 Tool 사용" 제약 추가)

::: info Memory 스팬은 아직 없습니다
지금 Trace에는 Runtime/Gateway/LLM 스팬만 보입니다.
다음 Step에서 Memory를 연동하면 `MEMORY_RETRIEVE` / `MEMORY_SAVE` 스팬이 추가됩니다.
:::

## 검증 체크리스트

- [ ] `./scripts/deploy-agent.sh` 성공
- [ ] `agentcore status` READY
- [ ] `agentcore invoke` 정상 응답 (설계서의 테스트 질문)
- [ ] Playground에서 대화 가능
- [ ] Observability에서 설계한 Tool 호출 확인

---

::: tip ✅ 다음
내 Agent가 세상에 공개됐습니다! → [Step 4: Memory로 고도화하기](step4-memory.md)
:::

