# Step 4: Memory로 고도화하기 <span class="badge-time">⏱️ 10분</span> <span class="badge-difficulty">★★☆</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 설계</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 2 바이브코딩</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 3 배포 & 테스트</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 4 Memory 고도화</span>
</div>

::: info 이 Step의 목표
내 Agent에 **Memory**를 연동합니다. 설계서에 적어둔 Memory 전략이 드디어 등장합니다.

패턴: Memory 조회 → 프롬프트에 주입 → Agent 실행 → 대화 기록 저장
:::


<div class="file-target">agents/phase3/app/phase3/main.py</div>

## 4-1. Memory 준비 (트랙별로 다릅니다)

#### Phase 2A를 진행했다면

이미 Memory가 있습니다. 환경변수만 확인하세요:

```bash
echo $AGENTCORE_MEMORY_ID
```

비어 있다면 `source ~/workshop/.env.w001`로 복구합니다.

#### Phase 2B를 진행했다면

Memory를 새로 생성합니다 (2A 트랙이 Phase 2A Step 1에서 했던 것과 동일):

```bash
cd ~/workshop/starter-code
python3.12 scripts/setup-memory.py
```

스크립트가 `bedrock-agentcore-control` API로 Memory와 3개 Strategy(CustomerFacts, SessionSummaries, CustomerPreferences)를 생성합니다.

::: danger 반드시 실행: 출력된 export 명령어를 복사 → 붙여넣기
```bash
export AGENTCORE_MEMORY_ID=<출력에 나온 실제 Memory ID>
```
이 값이 없으면 Agent가 Memory에 접근하지 못합니다.
:::

## 4-2. 바이브코딩으로 Memory 연동

Memory 연동도 프롬프트 한 번이면 됩니다. AI 코딩 도구에 아래를 입력하세요:

```text
~/workshop/starter-code/agents/phase3/app/phase3/main.py 에 Memory 연동을 추가해줘.
참고 코드: ~/workshop/starter-code/agents/phase2a/app/phase2a/main.py 의
fetch_customer_context() (retrieve_memory_records 사용)와
save_turn() (create_event 사용, 응답 후 백그라운드 스레드) 패턴을 그대로 가져와줘.

바꿀 것:
1. namespace는 참고 코드와 동일하게 "/users/{actor_id}/facts/" 를 사용해줘.
   (워크샵 Memory의 Strategy가 이 네임스페이스로 기록을 생성하기 때문)
2. entrypoint 흐름: Memory 조회 → System Prompt에 맥락 주입 →
   Agent 실행(스트리밍 유지) → 응답 완료 후 save_turn을 백그라운드 스레드로.
3. MEMORY_ID는 os.environ.get("AGENTCORE_MEMORY_ID", "") 에서 읽고,
   비어 있으면 Memory 없이도 동작하게 (참고 코드와 동일).
4. actor_id는 payload에서 읽어줘: payload.get("actor_id", "anonymous")
```

::: info 설계서의 커스텀 네임스페이스는 어디에?
Step 1 설계서에 적은 `/promotions/{actorId}/` 같은 커스텀 네임스페이스를 쓰려면
Memory에 해당 네임스페이스의 **Strategy를 추가로 생성**해야 합니다 (오늘은 시간 관계상 생략).
오늘 워크샵 Memory는 `users/{actorId}/facts`(사실), `users/{actorId}/preferences`(선호),
`users/{actorId}/summaries/{sessionId}`(요약) 3개 네임스페이스를 제공합니다 —
`actor_id`를 도메인 키(고객 ID, 매장 ID 등)로 활용하면 설계서의 의도를 충분히 표현할 수 있습니다.
:::


::: details 🧪 AI 도구가 없다면: 직접 추가하는 핵심 코드

`agents/phase2a/app/phase2a/main.py`에서 아래 3가지를 복사해 `agents/phase3/app/phase3/main.py`에 넣으세요:

```python
# 1. Memory 클라이언트 (모듈 레벨)
import boto3
from datetime import datetime, timezone
MEMORY_ID = os.environ.get("AGENTCORE_MEMORY_ID", "")
memory_client = boto3.client("bedrock-agentcore", region_name=REGION)

# 2. 조회 — Agent 실행 전 (namespace는 워크샵 Memory의 Strategy와 일치해야 함)
def fetch_context(actor_id: str, query: str) -> str:
    if not MEMORY_ID:
        return "이전 맥락 없음"
    try:
        results = memory_client.retrieve_memory_records(
            memoryId=MEMORY_ID,
            namespace=f"/users/{actor_id}/facts/",
            searchCriteria={"searchQuery": query, "topK": 5},
        )
        records = results.get("memoryRecordSummaries", [])
        if records:
            return "\n".join(r["content"]["text"] for r in records)
    except Exception as e:
        print(f"[Memory Retrieve Error] {e}")
    return "이전 맥락 없음"

# 3. 저장 — 응답 완료 후 백그라운드 스레드 (app/phase2a/main.py의 save_turn 그대로)
```

entrypoint에서는 `fetch_context()` 결과를 System Prompt에 주입하고,
스트리밍 완료 후 `threading.Thread(target=save_turn, ...).start()`를 호출합니다.
전체 흐름은 [Phase 2A Step 3](../phase2a/step3-agent.md)을 참고하세요.
:::

## 4-3. 재배포 & 두 번째 호출 효과 확인

```bash
cd ~/workshop/starter-code
./scripts/deploy-agent.sh phase3
```

**첫 번째 대화:**

```bash
cd agents/phase3
agentcore invoke --prompt "설계서의 테스트 질문"
```

**두 번째 대화 (같은 질문을 한 번 더 — Memory가 이전 대화를 기억하는지 확인):**

```bash
agentcore invoke --prompt "아까 그 건 이어서 진행해줘"
```

::: details ✅ Memory 연동 확인 포인트
두 번째 대화에서 Agent가:

- 첫 번째 대화의 내용을 **기억**하고 있음 ("아까 그 건"이 무엇인지 다시 묻지 않음)
- 이전 분석/조회 결과를 활용하여 이어서 답변
- 세션이 바뀌었는데도 맥락이 유지됨 — 이것이 Memory의 가치입니다
:::

## 4-4. Trace에서 Memory 스팬 확인

Observability Dashboard에서 Step 3과 비교해보세요:

```
Step 3 (Memory 연동 전):
  AGENT_START → TOOL_CALL(...) → AGENT_END

Step 4 (Memory 연동 후):
  MEMORY_RETRIEVE → AGENT_START → TOOL_CALL(...) → AGENT_END → MEMORY_SAVE
  ^^^^^^^^^^^^^^^^^                                              ^^^^^^^^^^^
  새로 추가된 Memory 스팬
```

## 검증 체크리스트

- [ ] `AGENTCORE_MEMORY_ID` 환경변수 설정
- [ ] Memory 연동 코드 추가 후 재배포 성공
- [ ] 두 번째 호출에서 맥락 기억 확인
- [ ] Trace에 `MEMORY_RETRIEVE` / `MEMORY_SAVE` 스팬 확인

## Workshop 완료!

::: tip ✅ 축하합니다! 전체 Workshop을 완료했습니다!

**오늘 여러분이 구축한 것:**

| Phase | 구축물 | AgentCore 서비스 |
|-------|--------|-----------------|
| Phase 1 | 추천 Agent | Runtime + Gateway + Observability + Code Interpreter |
| Phase 2A | CS Agent | + Memory + Policy + Browser |
| Phase 2B | 뉴스/날씨 수집 Agent | + Gateway 확장 (외부요인/재고/트렌드/발주) |
| Phase 3 | **나만의 Agent (바이브코딩)** | Runtime + Gateway + Memory 조합 |

**핵심 메시지:**

> Agent 개발은 "코드를 짜는 것"이 아니라 "서비스를 조합하는 것"입니다.
> Gateway Target만 바꾸면 Tool이 바뀌고,
> System Prompt만 바꾸면 역할이 바뀌고,
> Memory 전략만 바꾸면 지능이 바뀝니다.
> 
> 그리고 그 조합은 오늘 경험했듯 **말로 지시할 수 있습니다**.
> **여러분은 이미 프로덕션 Agent 개발자입니다.**
:::


---

::: info 다음 단계
- [부록: AgentCore 서비스 맵](../appendix/service-map.md)
- [부록: 우리 회사에서 이어가기](../appendix/next-steps.md)
:::

