# Step 1: 나만의 Agent 설계하기 <span class="badge-time">⏱️ 10분</span> <span class="badge-difficulty">★☆☆</span>

<div class="step-progress">
  <span class="step active">● Step 1 설계</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 2 바이브코딩</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 3 배포 & 테스트</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 4 Memory 고도화</span>
</div>

::: info 이 Step의 목표
코드를 쓰기 전에 **무엇을 만들지** 먼저 정합니다.
빈칸 채우기 설계서를 완성하면, 그게 그대로 Step 2의 **바이브코딩 프롬프트**가 됩니다.
:::

## 시나리오 떠올리기

정해진 패턴이나 정답은 없습니다. 아래 질문에 스스로 답하면서 **여러분의 시나리오**를 찾아보세요:

::: warning ❓ 스스로에게 묻는 4가지 질문
1. 우리 회사(또는 우리 팀)에서 **가장 반복적인 업무**는? → 그게 Use Case
2. 그 업무에서 **사람이 매번 판단하는 포인트**는? → 그게 Agent의 역할
3. 그 판단에 **어떤 정보가 필요한가**? → 그게 Tool 조합 (아래 팔레트에서 고르세요)
4. **과거 이력을 기억하면** 더 잘할 수 있는 일인가? → 그게 Memory
:::


떠오른 아이디어가 오늘의 Tool 팔레트로 표현이 안 될 수도 있습니다. 괜찮습니다 — 비슷한 성격의 Tool로 **축소판을 만든다**고 생각하세요. 예를 들어 "우리 회사의 물류 데이터"가 필요하면 오늘은 `inventory_status`로 대신하는 식입니다. 실무 적용 시 Gateway Target만 실제 API로 바꾸면 됩니다.

::: details 그래도 아이디어가 떠오르지 않는다면 (펼쳐보기)
몇 가지 방향만 예로 들면 — 매장 실적과 경쟁사 가격을 비교해 프로모션 전략을 제안하는 Agent, 유통기한 임박 상품을 찾아 할인 전략을 세우는 Agent, 단골 고객의 구매 패턴에 맞춰 신상품을 추천하는 Agent, 반품 문의를 처리하며 이전 상담 이력을 기억하는 Agent 같은 것들이 가능합니다. 어디까지나 예시일 뿐입니다 — **여러분 회사에서 실제로 반복되는 업무**에서 출발하는 것이 가장 좋은 설계입니다.
:::

## 오늘 등록된 Tool 팔레트

### 지금 내 Gateway에 등록된 Tool

`aws bedrock-agentcore-control list-gateway-targets --gateway-identifier "$GATEWAY_ID" --query 'items[].name' --output table` 로 직접 확인할 수 있습니다:

| Tool | Lambda 함수 | 기능 | 등록 시점 |
|------|------------|------|----------|
| `customer_profile` | `rcg-workshop-customer-profile` | 고객 프로필 조회 (등급, 선호도, 알러지) | Phase 1 |
| `product_search` | `rcg-workshop-product-search` | 카테고리/태그로 상품 검색 | Phase 1 |
| `purchase_history` | `rcg-workshop-purchase-history` | 고객 구매 이력 조회 | Phase 1 |
| `cs_lookup_order` 외 3개 | `rcg-workshop-cs-*` | 주문 조회/반품 정책/반품 처리/배송 추적 | Phase 2A 트랙 |
| `external_factors` | `rcg-workshop-demand-external-factors` | 날씨 예보/지역 이벤트/공휴일 | Phase 2B 트랙 |

### 더 필요하면 직접 등록할 수 있는 재료 (Lambda는 배포되어 있음)

아래 Lambda들은 계정에 이미 배포되어 있지만 Gateway에는 아직 등록되지 않았습니다.
설계에 필요하면 **Phase 2B Step 1에서 배운 콘솔 등록 방법** 그대로 Target을 추가하면 됩니다:

| Lambda 함수 | 기능 |
|------------|------|
| `rcg-workshop-demand-inventory` | 매장 재고 현황 조회 |
| `rcg-workshop-demand-sales-trend` | 판매 트렌드 분석 (7d/30d/90d) |
| `rcg-workshop-demand-purchase-order` | 발주 실행 |
| `rcg-workshop-weather-forecast` | 상세 날씨 예보 조회 |

::: info 내 트랙에 따라 등록된 Tool이 다릅니다
Phase 2A를 진행했다면 `cs_*` 4개, Phase 2B를 진행했다면 `external_factors`가
내 Gateway에 등록되어 있습니다. Phase 1의 3개는 공통입니다.
다른 트랙의 Tool이 필요하면 위 표의 Lambda를 콘솔에서 Target으로 등록하세요.
:::


::: info 창의적 조합을 환영합니다
예: `customer_profile` + `purchase_history` + `external_factors`
→ "이 고객에게 폭염 시즌에 맞는 상품을 추천"하는 **컨텍스트 인지 추천 Agent**

예: `external_factors` + 재고 Tool(직접 등록) + `code_interpreter`(Built-in)
→ "날씨 반영 + 재고 확인 + 최적 발주량 계산"하는 **스마트 발주 Agent**
:::

## Fill-in-the-blank 설계서

설계서를 **파일로 저장**하세요 — Step 2에서 AI 코딩 도구에게 이 파일을 읽게 하거나 내용을 붙여넣게 됩니다:

```bash
cd ~/workshop/starter-code
touch my-agent-design.md
```

VS Code에서 `my-agent-design.md`를 열고, 아래 템플릿을 복사한 뒤 빈칸을 채우세요 (5분):

```markdown
## 나의 Agent 설계서

**Agent 이름**: _________________________ Agent

**한 줄 설명**: "_________________________를 도와주는 AI Agent"

**해결하는 반복 업무**: _________________________

**Gateway Tools (최대 4개)**:
1. _________________ — (기능: __________________)
2. _________________ — (기능: __________________)
3. _________________ — (기능: __________________)
4. _________________ — (기능: __________________)

**추가 Tool**:
- [ ] Code Interpreter (데이터 분석/계산)

**Memory 전략** (Step 4에서 연동):
- 기억의 주체 (actor_id로 쓸 것): [ ] 고객 ID  [ ] 매장 ID  [ ] 기타: ________
- 저장하는 것: _________________________
- 활용 방식: _________________________

**응답 규칙** (Agent가 지켜야 할 것 2가지):
1. _________________________________________
2. _________________________________________

**테스트 질문** (Agent에게 물어볼 말):
"_________________________________________________"
```

::: tip 이 설계서가 곧 바이브코딩 프롬프트입니다
Step 2에서 이 설계서를 AI 코딩 도구에 **그대로 붙여넣습니다**.
빈칸이 구체적일수록 AI가 생성하는 코드가 정확해집니다.
특히 **응답 규칙**과 **테스트 질문**을 명확히 쓰면 System Prompt 품질이 올라갑니다.
:::

## 모범 사례: 컨텍스트 인지 추천 Agent

::: details 🧪 이렇게 채우면 됩니다 (펼쳐보기)

```markdown
## 나의 Agent 설계서

**Agent 이름**: Weather-Aware Recommender Agent

**한 줄 설명**: "고객 프로필과 날씨/이벤트를 종합해 지금 이 고객에게 딱 맞는 상품을 추천해주는 AI Agent"

**해결하는 반복 업무**: 매장 직원이 매번 날씨 확인 + 고객 이력 확인 + 재고 확인을 수동으로 한 뒤 추천하는 일

**Gateway Tools (최대 4개)**:
1. customer_profile — (기능: 고객 ID로 선호도, 알러지, 등급 조회)
2. purchase_history — (기능: 고객의 최근 구매 이력 → 중복 추천 방지)
3. external_factors — (기능: 향후 7일 날씨 예보 + 지역 이벤트 조회)
4. product_search — (기능: 카테고리/태그로 상품 검색, 재고 있는 것만)

**추가 Tool**:
- [ ] Code Interpreter (데이터 분석/계산)
- [ ] Browser (외부 사이트 실시간 조회)

**Memory 전략** (Step 4에서 연동):
- 기억의 주체 (actor_id로 쓸 것): [x] 고객 ID  [ ] 매장 ID  [ ] 기타: ________
- 저장하는 것: 추천 결과와 고객 반응 (구매 여부)
- 활용 방식: 다음 추천 시 이전에 추천했던 상품 제외 + 선호 반영

**응답 규칙** (Agent가 지켜야 할 것 2가지):
1. 알러지 성분 포함 상품은 절대 추천하지 않는다 (이유를 명시)
2. 추천 상품마다 "왜 지금 이 상품인지" 이유를 날씨/이벤트와 연결해 설명한다

**테스트 질문** (Agent에게 물어볼 말):
"고객 C001에게 이번 주에 맞는 상품 3개 추천해줘"
```

**왜 이 설계가 좋은가:**

- Tool 4개를 **순서 있게** 조합합니다: 프로필(알러지 확인) → 구매 이력(중복 방지) → 날씨/이벤트(시즌 반영) → 상품 검색(최종 추천)
- 응답 규칙이 **구체적**이라 System Prompt가 명확해집니다
- 테스트 질문에 `C001`(Mock 데이터에 존재하는 고객 ID)을 사용해 즉시 검증 가능
:::


---

::: warning 10분 타이머
완벽하지 않아도 됩니다. **빈칸을 70%만 채우면** 다음으로 넘어가세요.
구현하면서 수정할 수 있습니다.
:::


---

::: tip ✅ 다음
설계 완료! → [Step 2: 바이브코딩으로 구현하기](step2-vibecoding.md)
:::

