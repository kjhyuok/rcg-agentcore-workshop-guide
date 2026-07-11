# Step 4: Policy 설정 (발주 승인 규칙) <span class="badge-time">⏱️ 10분</span> <span class="badge-difficulty">★★☆</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 Memory</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 2 Gateway+Browser</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 3 Agent</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 4 Policy</span>
</div>

!!! info "소요 시간: 10분"
    50만원 초과 발주 시 자동으로 승인 대기 상태가 되는 Policy를 설정합니다.

<div class="file-target">scripts/setup-policy.py</div>
---

## Policy가 필요한 이유

Agent가 "긴급 발주해"라고 하면 바로 실행해버리면?

- 실수로 수천만 원 발주 가능
- 예산 초과 위험
- 승인 프로세스 없이 자율 실행 = 리스크

!!! quote "AgentCore Policy의 철학"
    "Agent에게 자율성을 주되, **가드레일** 안에서만 행동하게 한다"

---

## Policy 생성

```bash
agentcore policy create \
  --name "purchase-approval-policy" \
  --description "500,000원 초과 발주 시 관리자 승인 필요" \
  --rules '[
    {
      "condition": {
        "tool": "purchase_order",
        "field": "total_amount",
        "operator": "GREATER_THAN",
        "value": 500000
      },
      "action": "REQUIRE_APPROVAL",
      "message": "발주 금액이 500,000원을 초과합니다. 관리자 승인이 필요합니다."
    }
  ]'
```

---

## Policy를 Agent에 연결

```bash
agentcore runtime update \
  --name "demand-forecast-agent" \
  --policy-id $POLICY_ID
```

---

## 테스트 Case 1: 50만원 이하 (자동 승인)

```bash
agentcore invoke \
  --agent "demand-forecast-agent" \
  '{"input": "라면류 80박스만 발주해줘", "store_id": "store-001"}'
```

**응답:**
```json
{
  "status": "completed",
  "approval_needed": false,
  "order": {
    "items": [{"product": "라면류", "quantity": 80, "amount": 400000}],
    "total_amount": 400000,
    "message": "발주가 정상 처리되었습니다."
  }
}
```

---

## 테스트 Case 2: 50만원 초과 (승인 필요)

```bash
agentcore invoke \
  --agent "demand-forecast-agent" \
  '{"input": "현재 재고 분석하고 긴급 발주 진행해", "store_id": "store-001"}'
```

**응답:**
```json
{
  "status": "pending_approval",
  "approval_needed": true,
  "order": {
    "items": [
      {"product": "음료류", "quantity": 200, "amount": 1200000},
      {"product": "라면류", "quantity": 80, "amount": 400000}
    ],
    "total_amount": 1600000,
    "policy_triggered": "purchase-approval-policy",
    "message": "발주 금액 1,600,000원 > 500,000원. 관리자 승인 대기 중입니다."
  }
}
```

---

## Trace에서 Policy 동작 확인

Observability Dashboard에서 Policy 체크 포인트를 확인할 수 있습니다:

```
... (분석 Tool 호출들) ...
├─ [Gateway] purchase_order 호출 시도
├─ [Policy] purchase-approval-policy 평가
│   ├─ condition: total_amount(1,600,000) > 500,000
│   ├─ result: BLOCKED
│   └─ action: REQUIRE_APPROVAL
└─ [Agent] "승인 대기" 응답 생성
```

---

## Policy 규칙 확장 예시

실제 운영에서는 더 복잡한 규칙을 추가할 수 있습니다:

```json
{
  "rules": [
    {
      "name": "high-value-approval",
      "condition": {"field": "total_amount", "operator": "GT", "value": 500000},
      "action": "REQUIRE_APPROVAL"
    },
    {
      "name": "urgent-auto-approve",
      "condition": {
        "AND": [
          {"field": "priority", "operator": "EQ", "value": "urgent"},
          {"field": "total_amount", "operator": "LTE", "value": 1000000}
        ]
      },
      "action": "ALLOW",
      "note": "긴급이면서 100만원 이하는 자동 승인"
    },
    {
      "name": "block-weekend",
      "condition": {"field": "day_of_week", "operator": "IN", "value": ["SAT", "SUN"]},
      "action": "BLOCK",
      "message": "주말 발주는 불가합니다."
    }
  ]
}
```

!!! tip "Policy는 선언적입니다"
    Agent 코드를 수정하지 않고도 Policy만 변경하면 행동이 바뀝니다.
    이것이 AgentCore의 핵심 가치입니다.

---

## Phase 2B 완료!

!!! success "축하합니다! Phase 2B를 완료했습니다"

    **지금까지 구축한 것:**

    | 서비스 | 역할 | Phase |
    |--------|------|-------|
    | Runtime | Agent HTTPS 배포 | Phase 1 |
    | Gateway | Lambda를 MCP Tool로 | Phase 1 |
    | Observability | Trace 모니터링 | Phase 1 |
    | Memory | 대화/주문 이력 기억 | Phase 2A/2B |
    | Policy | 금액 기반 자동 분기 | Phase 2A/2B |

    **다음은 [Phase 3](../phase3/index.md)에서 자사 Agent를 직접 설계합니다!**
