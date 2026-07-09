# Step 1: Memory 네임스페이스 추가 (주문 이력) <span class="badge-time">⏱️ 5분</span> <span class="badge-difficulty">★☆☆</span>

<div class="step-progress">
  <span class="step active">● Step 1 Memory</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 2 Gateway+Browser</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 3 Agent</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 4 Policy</span>
</div>

!!! info "소요 시간: 5분"
    Phase 2A에서 이미 Memory를 생성했다면, 같은 Memory를 재사용합니다.
    새로운 네임스페이스(`/orders/{actorId}/`)로 주문 데이터를 저장하는 방식입니다.

<div class="file-target">scripts/setup-memory.py</div>
---

## 2A에서 Memory를 이미 만들었다면?

Phase 2A에서 생성한 Memory를 그대로 사용합니다. AgentCore Memory는 **하나의 Memory에 여러 네임스페이스**를 가질 수 있습니다.

| 네임스페이스 | 용도 | Phase |
|-------------|------|-------|
| `/conversations/{actorId}/` | 고객 대화 맥락 | 2A |
| `/orders/{actorId}/` | 주문/발주 이력 | **2B** |

!!! tip "핵심 인사이트"
    Memory를 여러 개 만들 필요 없습니다. **네임스페이스로 데이터를 분리**하면 됩니다.
    마치 하나의 DB에 여러 테이블이 있는 것과 같습니다.

---

## Memory ID 확인

```bash
# Phase 2A에서 만든 Memory 확인
agentcore memory list
```

출력 예시:
```json
{
  "memories": [
    {
      "memoryId": "mem-abc123def456",
      "name": "retail-workshop-memory",
      "status": "ACTIVE"
    }
  ]
}
```

!!! warning "Memory가 없다면?"
    Phase 2A를 건너뛰었다면 아래 명령으로 새로 생성하세요.

---

## (선택) Memory 새로 생성하기

Phase 2A를 하지 않은 경우에만 실행합니다.

```bash
agentcore memory create \
  --name "retail-workshop-memory" \
  --description "Retail workshop - CS conversations and order history" \
  --strategy "SEMANTIC" \
  --namespace-template "/orders/{actorId}/"
```

---

## 주문 이력 데이터 구조

이 Memory에 저장될 주문 데이터의 형태입니다:

```json
{
  "namespace": "/orders/store-001/",
  "content": "2024-12 발주: 라면류 500박스 (2,500,000원), 음료류 300박스 (1,800,000원). 리드타임 3일. 연말 프로모션 대비 20% 추가 발주.",
  "metadata": {
    "store_id": "store-001",
    "order_date": "2024-12-15",
    "total_amount": 4300000,
    "category": "식품"
  }
}
```

---

## Agent에서 Memory 사용하는 패턴

```python
from bedrock_agentcore.memory import MemoryClient

memory_client = MemoryClient(memory_id="mem-abc123def456")

# 특정 매장의 발주 이력 조회
results = memory_client.retrieve(
    namespace=f"/orders/{store_id}/",
    query="최근 3개월 발주 패턴",
    max_results=10
)

# 새 발주 기록 저장
memory_client.store(
    namespace=f"/orders/{store_id}/",
    content=f"발주 완료: {order_summary}",
    metadata={"amount": total_amount, "date": order_date}
)
```

---

## 확인 체크리스트

- [x] Memory ID 확인 (또는 새로 생성)
- [x] `/orders/{actorId}/` 네임스페이스 개념 이해
- [x] 주문 데이터 구조 파악

!!! success "다음 단계"
    Memory 준비 완료! [Step 2: Gateway Target 추가](step2-gateway.md)로 이동합니다.
