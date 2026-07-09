# Step 4: Observability (Trace 확인) <span class="badge-time">⏱️ 15분</span> <span class="badge-difficulty">★☆☆</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 Gateway</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 2 Agent</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 3 Runtime</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 4 Observability</span>
</div>

!!! info "이 Step의 목표"
    배포된 Agent의 동작을 **GenAI Observability Dashboard**에서 실시간 관찰합니다.
    
    Agent가 어떤 Tool을 어떤 순서로 호출했는지, 각 단계의 소요 시간을 확인합니다.

---

## Observability란?

Agent 내부에서 일어나는 모든 일을 **투명하게 추적**합니다:

- 어떤 Tool을 호출했는지
- 각 호출에 얼마나 걸렸는지
- LLM이 몇 토큰을 사용했는지
- 에러가 어디서 발생했는지

**AgentCore Runtime에 배포하면 자동으로 활성화됩니다.** 별도 설정 불필요.

---

## 4-1. CLI로 Trace 확인

```bash
agentcore obs list --name rcg-recommend-agent --limit 5
```

특정 세션의 상세 Trace:

```bash
agentcore obs show --session-id "test-001"
```

??? success "Trace 출력 예시"
    ```
    Trace: ac-tr-67aa52c5
    Duration: 3,439ms
    Status: SUCCESS
    
    Spans:
    ├─ [RUNTIME] Invoke received (2ms)
    ├─ [MODEL] Claude Sonnet 4.6 — in:1,200 out:89 — tool_use (2.1s)
    ├─ [GATEWAY] customer_profile — PERMIT (184ms)
    ├─ [MODEL] Claude Sonnet 4.6 — in:1,450 out:67 — tool_use (1.8s)
    ├─ [GATEWAY] purchase_history — PERMIT (92ms)
    ├─ [MODEL] Claude Sonnet 4.6 — in:1,680 out:112 — tool_use (2.0s)
    ├─ [GATEWAY] product_search — PERMIT (156ms)
    ├─ [GATEWAY] product_search — PERMIT (148ms)
    ├─ [MODEL] Claude Sonnet 4.6 — in:2,100 out:423 — end_turn (2.8s)
    └─ [RUNTIME] Complete — SUCCESS (3,439ms)
    ```

---

## 4-2. GenAI Observability Dashboard

AWS Console에서 확인합니다:

1. AWS Console → CloudWatch → **Application Signals** → **GenAI**
2. 또는 직접 URL: `https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#genai-observability`

### Dashboard에서 볼 수 있는 것

| 메트릭 | 의미 |
|--------|------|
| **Invocations** | Agent 호출 횟수 |
| **Latency P50/P95** | 응답 시간 분포 |
| **Token Usage** | 입력/출력 토큰 사용량 |
| **Tool Calls** | Tool별 호출 횟수 |
| **Error Rate** | 에러 비율 |

---

## 4-3. Trace에서 관찰할 것

배포된 Agent를 한 번 더 호출하고 Trace를 확인하세요:

```bash
agentcore invoke \
  --name rcg-recommend-agent \
  --payload '{"message": "고객 C002에게 뷰티 상품 추천해주세요", "session_id": "obs-test-002"}'
```

그리고 Trace에서 확인:

- [ ] **Tool 호출 순서** — customer_profile → purchase_history → product_search
- [ ] **각 Tool 응답 시간** — Gateway 경유 시 보통 100~200ms
- [ ] **LLM 호출 횟수** — 보통 3~5회 (Tool 호출마다 1회)
- [ ] **총 토큰** — 입력 ~5,000 + 출력 ~500 정도

---

## 4-4. 문제 디버깅 시나리오

의도적으로 에러를 발생시켜봅니다:

```bash
agentcore invoke \
  --name rcg-recommend-agent \
  --payload '{"message": "고객 C999에게 추천해주세요", "session_id": "error-test-003"}'
```

Trace에서 확인:

- `customer_profile` Tool이 `{"error": "고객 C999를 찾을 수 없습니다"}` 반환
- Agent가 에러를 보고 어떻게 응답하는지 관찰

!!! tip "Observability의 진짜 가치"
    문제가 생겼을 때 **어디서 실패했는지** 즉시 파악할 수 있습니다.
    
    - Tool이 에러를 반환했나? → Gateway Trace에서 확인
    - LLM이 잘못 판단했나? → Model Span에서 입출력 확인
    - 느린 응답? → 각 Span의 duration으로 병목 식별

---

## Phase 1 완료!

축하합니다. 여러분은 지금:

- [x] **Gateway** — 3개 Lambda를 MCP Tool로 등록
- [x] **Runtime** — Agent를 HTTPS 엔드포인트로 배포
- [x] **Observability** — Trace로 Agent 동작을 실시간 관찰

이제 이 Agent에 **Memory**(맥락 유지)와 **Policy**(행동 제어)를 추가합니다.

---

<div class="phase-complete">
<h3>🎉 Phase 1 완료!</h3>
<p>여러분의 Agent는 이미 <b>프로덕션 HTTPS 엔드포인트</b>로 동작하고 있습니다.</p>
<p>이제 Memory(기억) + Policy(규칙) + Browser(실시간 정보)를 추가합니다. 아래에서 택1 하세요:</p>
<div class="next-options">
<a href="../../phase2a/" class="option-2a">📞 Phase 2A: CS 자동화 Agent (★★★)</a>
<a href="../../phase2b/" class="option-2b">📊 Phase 2B: 수요예측 Agent (★★★★)</a>
</div>
</div>
