# Step 4: Policy (에스컬레이션) <span class="badge-time">⏱️ 15분</span> <span class="badge-difficulty">★★☆</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 Memory</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 2 Gateway+Browser</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 3 Agent</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 4 Policy</span>
</div>

!!! info "이 Step의 목표"
    **AgentCore Policy**를 설정하여 Agent에 가드레일을 적용합니다.
    
    규칙: 환불 금액 > 50,000원이면 CS 팀 리더 승인 필요

<div class="file-target">scripts/setup-policy.py</div>
---

## Policy란?

```
Policy 없이:  Agent가 100만원 환불도 마음대로 처리
Policy 있으면: "이 건은 제가 직접 처리할 수 없습니다. CS 팀 리더에게 전달합니다."
```

**Policy의 가치:**

- Agent가 지켜야 할 **비즈니스 규칙**을 코드 외부에서 관리
- Agent 코드 수정 없이 규칙 변경 가능
- 감사 로그(Trace)에 ALLOW/DENY 결정이 기록됨
- LLM이 규칙을 "까먹는" 것을 시스템 레벨에서 방지

!!! tip "System Prompt vs Policy"
    | | System Prompt | Policy |
    |--|--|--|
    | 방식 | LLM에게 "하지 마" 요청 | 시스템이 **강제** 차단 |
    | 신뢰도 | LLM이 무시할 수 있음 | 100% 적용 보장 |
    | 변경 | Agent 재배포 필요 | 정책만 수정 |
    | 감사 | 로그 없음 | Trace에 기록 |

---

## 4-1. 에스컬레이션 규칙 설계

CS 시나리오의 에스컬레이션 규칙:

```
IF process_return 응답에 needs_escalation == true
THEN Agent는 직접 처리하지 않고 "CS 팀 리더에게 전달" 응답
```

`process_return` Lambda의 로직:

```python title="process_return Lambda (이미 배포됨)"
def handler(event, context):
    refund_amount = event["refund_amount"]
    
    if refund_amount > 50000:
        return {
            "status": "PENDING_APPROVAL",
            "needs_escalation": True,
            "message": "환불 금액이 50,000원을 초과하여 CS 팀 리더 승인이 필요합니다.",
            "escalation_to": "cs-team-lead",
        }
    else:
        return {
            "status": "COMPLETED",
            "needs_escalation": False,
            "message": f"환불 {refund_amount:,}원 처리 완료",
            "refund_method": "원래 결제수단으로 3~5영업일 내 환불",
        }
```

---

## 4-2. Policy 생성

```bash
python3 scripts/setup-policy.py
```

??? example "스크립트가 하는 일 (내부)"
    ```python
    import boto3

    client = boto3.client("bedrock-agentcore-control", region_name="us-east-1")

    # Policy Engine 생성
    engine = client.create_policy_engine(
        name="rcg-cs-policy-engine",
        description="CS Agent 에스컬레이션 정책",
    )

    # Policy 규칙 등록
    client.create_policy(
        policyEngineId=engine["policyEngineId"],
        name="refund-escalation",
        description="5만원 초과 환불은 CS 팀 리더 승인 필요",
        policyType="TOOL_RESPONSE_GUARD",
        rules=[
            {
                "toolName": "process_return",
                "condition": "response.needs_escalation == true",
                "action": "ESCALATE",
                "message": "환불 금액이 기준(50,000원)을 초과합니다. CS 팀 리더에게 에스컬레이션합니다.",
            }
        ],
    )
    ```

---

## 4-3. Agent에 Policy 적용

Agent의 System Prompt에도 규칙을 명시합니다 (이중 안전장치):

```python title="System Prompt에 에스컬레이션 규칙 추가"
SYSTEM_PROMPT = """당신은 리테일 CS 전문 상담사입니다.

## 에스컬레이션 규칙 (반드시 준수)
- process_return 결과에서 needs_escalation=true이면:
  → 직접 처리하지 않음
  → "CS 팀 리더에게 전달하겠습니다"로 안내
  → 예상 처리 시간 안내 (24시간 이내)
- needs_escalation=false이면:
  → 환불 완료 안내
  → 환불 방법 및 소요 기간 안내

## 고객 맥락 (Memory)
{customer_context}
"""
```

!!! warning "System Prompt + Policy = 이중 안전장치"
    System Prompt만으로는 LLM이 규칙을 무시할 수 있습니다.
    
    Policy Engine이 **시스템 레벨에서** 강제하므로, LLM이 규칙을 어기는 것이 불가능합니다.

---

## 4-4. 3가지 시나리오 테스트

### 테스트 1: 상품 불량 반품 (35,000원 — 에스컬레이션 없음)

```bash
python3 scripts/invoke-agent.py \
  --endpoint "$CS_AGENT_ENDPOINT" \
  --customer-id "C001" \
  --message "주문 ORD-2024-101 상품이 불량이에요. 반품하고 싶습니다."
```

??? success "예상 결과"
    ```
    🤖 Agent: ORD-2024-101 주문을 확인했습니다.
    
    - 상품: 비타민C 세럼 (35,000원)
    - 반품 사유: 상품불량
    
    ✅ 환불 처리가 완료되었습니다.
    - 환불 금액: 35,000원
    - 환불 방법: 원래 결제수단으로 3~5영업일 내 환불
    
    더 도와드릴 것이 있으신가요?
    ```

### 테스트 2: 배송 추적 (단순 조회)

```bash
python3 scripts/invoke-agent.py \
  --endpoint "$CS_AGENT_ENDPOINT" \
  --customer-id "C002" \
  --message "주문 ORD-2024-555 배송 어디쯤 왔나요?"
```

??? success "예상 결과"
    ```
    🤖 Agent: ORD-2024-555 배송 상태를 확인했습니다.
    
    📦 배송 추적:
    - 현재 상태: 배송중 (간선 운송)
    - 현재 위치: 서울 송파 물류센터
    - 예상 도착: 내일(6/30) 오전 중
    
    배송 완료 시 알림을 받으실 수 있습니다.
    ```

### 테스트 3: 고가 반품 (69,000원 — 에스컬레이션 발동!)

```bash
python3 scripts/invoke-agent.py \
  --endpoint "$CS_AGENT_ENDPOINT" \
  --customer-id "C003" \
  --message "주문 ORD-2024-999 환불 요청합니다. 단순변심이에요."
```

??? success "예상 결과 — 에스컬레이션"
    ```
    🤖 Agent: ORD-2024-999 주문을 확인했습니다.
    
    - 상품: 프리미엄 스킨케어 세트 (69,000원)
    - 반품 사유: 단순변심
    
    ⚠️ 환불 금액이 50,000원을 초과하여, 
    CS 팀 리더에게 전달하겠습니다.
    
    - 에스컬레이션 사유: 환불 금액 기준 초과 (69,000원 > 50,000원)
    - 예상 처리 시간: 24시간 이내
    - 담당: CS 팀 리더
    
    처리 결과는 등록된 연락처로 안내드리겠습니다.
    ```

---

## 4-5. Trace에서 Policy 확인

Observability에서 테스트 3의 Trace를 확인합니다:

```
Trace (테스트 3 — 에스컬레이션):
  MEMORY_RETRIEVE
  AGENT_START
  TOOL_CALL(lookup_order) → 200 OK
  TOOL_CALL(return_policy) → 200 OK
  TOOL_CALL(process_return) → needs_escalation: true
  POLICY_CHECK → ESCALATE ⚠️   ← Policy가 개입한 지점
  AGENT_END
  MEMORY_SAVE
```

```
Trace (테스트 1 — 정상 처리):
  MEMORY_RETRIEVE
  AGENT_START
  TOOL_CALL(lookup_order) → 200 OK
  TOOL_CALL(process_return) → needs_escalation: false
  POLICY_CHECK → ALLOW ✅      ← Policy 통과
  AGENT_END
  MEMORY_SAVE
```

!!! info "POLICY_CHECK 스팬"
    - **ALLOW**: 정책 위반 없음, Agent가 정상 응답 가능
    - **ESCALATE**: 정책에 의해 에스컬레이션 트리거됨
    - Trace에 조건(`refund_amount > 50000`)과 결정(`ESCALATE`)이 기록됨

---

## Phase 2A 완성!

축하합니다! Phase 2A에서 추가한 것들:

| 서비스 | 역할 | 효과 |
|--------|------|------|
| **Memory** | 고객 맥락 유지 | 같은 말 반복 안 해도 됨 |
| **Gateway 확장** | CS Tool 4개 추가 | Agent 코드 수정 없이 확장 |
| **Policy** | 에스컬레이션 규칙 | 금액 기준 자동 분기 + 감사 로그 |

---

## Phase 1 → 2A 성장 비교

```
Phase 1:  Gateway → Agent → Observability
          (도구를 쓸 줄 아는 Agent)

Phase 2A: Memory → Gateway → Agent → Policy → Observability
          (기억하고, 규칙을 지키는 Agent)
```

!!! success "Phase 2A 완료!"
    Memory + Policy를 추가하여 **실제 CS 업무에 투입 가능한** Agent가 되었습니다.
    
    다음 Phase에서는 더 복잡한 시나리오를 다룹니다.
