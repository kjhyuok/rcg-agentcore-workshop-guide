# Step 1: Memory 생성 & Strategy <span class="badge-time">⏱️ 10분</span> <span class="badge-difficulty">★☆☆</span>

<div class="step-progress">
  <span class="step active">● Step 1 Memory</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 2 Gateway+Browser</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 3 Agent</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 4 Policy</span>
</div>

!!! info "이 Step의 목표"
    **AgentCore Memory**를 생성하고, 고객 맥락을 기억하기 위한 **Strategy**를 설정합니다.
    
    이후 Agent는 이전 대화 내용과 고객 선호를 기억한 채 응대합니다.

<div class="file-target">scripts/setup-memory.py</div>
---

## Memory란?

```
기존 방식:  매 대화마다 "누구세요?" (상태 없음)
AgentCore: "김건강님, 지난번 반품 건 해결되셨나요?" (맥락 유지)
```

**Memory의 가치:**

- 고객이 같은 말을 반복하지 않아도 됨
- 이전 대화에서 파악한 선호/불만을 활용
- 세션이 끊어져도 맥락이 유지됨
- Agent가 더 자연스럽고 효율적으로 응대

!!! tip "Memory = Agent의 장기 기억"
    단기 기억(현재 대화)은 LLM의 Context Window가 담당합니다.
    
    장기 기억(이전 대화, 선호도, 요약)은 **AgentCore Memory**가 담당합니다.

---

## 1-1. Memory 생성 스크립트 실행

```bash
cd ~/workshop/starter-code
python3 scripts/setup-memory.py
```

??? example "스크립트가 하는 일 (내부)"
    ```python
    from bedrock_agentcore.memory import MemoryClient

    client = MemoryClient(region_name="us-east-1")

    # 1. Memory 생성
    memory = client.create_memory(
        name="rcg-cs-memory-XXXX",
        description="CS Agent용 고객 맥락 저장소",
    )

    # 2. Strategy 추가 — UserPreference (고객 선호 자동 추출)
    client.create_memory_strategy(
        memoryId=memory["memoryId"],
        name="user-preferences",
        strategy={
            "extractionStrategy": {
                "type": "UserPreference",
                "namespacePattern": "/preferences/{actorId}/",
                "description": "고객의 선호도, 관심사, 스타일 자동 추출",
            }
        },
    )

    # 3. Strategy 추가 — Summary (대화 요약)
    client.create_memory_strategy(
        memoryId=memory["memoryId"],
        name="conversation-summary",
        strategy={
            "extractionStrategy": {
                "type": "Summary",
                "namespacePattern": "/summaries/{actorId}/{sessionId}/",
                "description": "각 세션 종료 시 대화 내용 자동 요약",
            }
        },
    )

    # 4. Strategy 추가 — Semantic (의미 기반 검색용)
    client.create_memory_strategy(
        memoryId=memory["memoryId"],
        name="semantic-facts",
        strategy={
            "extractionStrategy": {
                "type": "Semantic",
                "namespacePattern": "/facts/{actorId}/",
                "description": "대화에서 추출한 사실 정보 (주문번호, 이슈 등)",
            }
        },
    )
    ```

---

## 1-2. Strategy 이해하기

| Strategy | 용도 | Namespace 패턴 | 예시 |
|----------|------|---------------|------|
| **UserPreference** | 고객 선호 자동 추출 | `/preferences/{actorId}/` | "이 고객은 빠른 배송을 선호" |
| **Summary** | 세션별 대화 요약 | `/summaries/{actorId}/{sessionId}/` | "지난 대화: 반품 문의 → 처리 완료" |
| **Semantic** | 의미 기반 사실 저장 | `/facts/{actorId}/` | "주문 ORD-2024-789 관련 불만 제기" |

!!! info "Namespace 패턴의 역할"
    `{actorId}`는 고객 ID로 대체됩니다. 이를 통해:
    
    - 고객별로 데이터가 **격리**됨
    - 특정 고객의 기억만 빠르게 **검색** 가능
    - 세션별 요약도 독립적으로 관리

---

## 1-3. 결과 확인

스크립트 출력을 확인합니다:

??? success "정상 출력 예시"
    ```
    🧠 Memory 생성: rcg_workshop_memory_6846
    ✅ Memory 생성 완료: rcg_workshop_memory_6846-jC9peMDFLx

    ==================================================
    🎉 Memory 설정 완료!
       Memory ID: rcg_workshop_memory_6846-jC9peMDFLx

       환경변수 설정:
       export AGENTCORE_MEMORY_ID=rcg_workshop_memory_6846-jC9peMDFLx
    ==================================================
    ```

!!! danger "반드시 실행: 출력된 export 명령어를 복사 → 붙여넣기"
    ```bash
    export AGENTCORE_MEMORY_ID=<위 출력에 나온 실제 Memory ID>
    ```
    스크립트 출력 마지막의 `export AGENTCORE_MEMORY_ID=...` 줄을 **그대로 복사해서 터미널에 붙여넣기** 하세요.
    이 값이 없으면 이후 Agent가 Memory에 접근하지 못합니다.

CLI로 확인:

```bash
aws bedrock-agentcore-control get-memory \
  --memory-id "$AGENTCORE_MEMORY_ID" \
  --query 'memory.{name: name, status: status, strategies: strategies[].name}' \
  --output yaml
```

??? success "정상 출력"
    ```yaml
    name: rcg-cs-memory-XXXX
    status: ACTIVE
    strategies:
      - user-preferences
      - conversation-summary
      - semantic-facts
    ```

---

## 1-4. 환경변수 설정

!!! warning "환경변수 설정 필수"
    ```bash
    export AGENTCORE_MEMORY_ID=<위에서 출력된 Memory ID>
    ```
    이 값은 Step 3에서 Agent가 Memory에 접근할 때 사용됩니다.

---

## 이해 체크

- [x] Memory = Agent의 **장기 기억** 저장소
- [x] Strategy = **어떤 정보를 어떻게 추출/저장할지** 정의하는 규칙
- [x] Namespace = 고객별, 세션별 데이터를 **격리**하는 경로 패턴
- [x] 3개 Strategy가 각각 다른 종류의 맥락을 담당

---

!!! success "다음"
    Memory 준비 완료! → [Step 2: CS Gateway Target 추가](step2-gateway.md)
