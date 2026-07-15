# Step 1: 데이터 재료 준비하기 (Gateway 확장) <span class="badge-time">⏱️ 15분</span> <span class="badge-difficulty">★★☆</span>

<div class="step-progress">
  <span class="step active">● Step 1 Gateway</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 2 Agent</span>
</div>

::: info 이 Step의 목표
Phase 1에서 만든 Gateway에 **`external-factors` Tool**을 추가 등록합니다.
이 Tool은 날씨 예보/지역 이벤트/공휴일 데이터를 Agent에게 제공합니다.
:::

## 현재 Gateway 상태 확인

Phase 1에서 이미 Gateway를 생성하고 3개 Target을 등록했습니다:

```
현재: customer-profile, product-search, purchase-history (3개)
추가: external-factors (1개)
───────────────────────────────────────────────────────────────
Gateway 합계: 4개 Target = Agent가 사용할 수 있는 Tool
```

::: tip Gateway의 핵심 가치
Agent 코드를 수정하지 않고 Gateway Target만 추가하면 Agent 기능이 확장됩니다.
이것이 Gateway의 관심사 분리 — Tool 확장과 Agent 코드가 분리되어 있습니다.
:::

## 1-1. `external-factors` Target 등록

Bedrock AgentCore Gateway 콘솔에서 추가 버튼을 누릅니다.

![Gateway Target 추가](image.png)

아래 설정으로 등록합니다:

- **Target configuration**: MCP target
- **대상 이름**: `external-factors`
- **대상 유형**: Lambda ARN
- **Lambda ARN**: 배포되어 있는 `rcg-workshop-demand-external-factors` 함수의 ARN을 붙여넣습니다

**인라인 스키마**에 아래 JSON을 넣습니다:

```json
{
  "name": "external-factors",
  "description": "매장 운영에 영향을 주는 외부 요인을 조회합니다. 날씨 예보, 지역 이벤트, 공휴일, 프로모션 일정을 포함합니다.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "store_id": {
        "type": "string",
        "description": "매장 ID (예: store-001)"
      },
      "forecast_days": {
        "type": "integer",
        "description": "향후 며칠간의 요인을 조회할지 (기본: 7)"
      }
    },
    "required": ["store_id"]
  }
}
```

::: tip 스키마의 description이 Tool 선택을 좌우합니다
Agent는 이 description을 읽고 "날씨 관련 질문에 이 Tool을 쓸지" 판단합니다.
Phase 3에서 나만의 Tool을 조합할 때도 이 원리를 활용하게 됩니다.
:::

## 1-2. 결과 확인

등록 후 터미널에서 확인합니다:

```bash
aws bedrock-agentcore-control list-gateway-targets \
  --gateway-identifier "$GATEWAY_ID" \
  --query 'items[].name' --output table
```

::: details ✅ 정상 출력 (4개 Target)
```
----------------------
| ListGatewayTargets |
+--------------------+
|  customer-profile  |
|  product-search    |
|  purchase-history  |
|  external-factors  |
+--------------------+
```
:::


::: info 4개 모두 확인되면 성공
Status가 `CREATING`이면 30초 정도 기다린 후 다시 확인하세요.
:::

## 이해 체크

- [x] 같은 Gateway에 Target을 **추가**만 하면 Agent가 자동 인식
- [x] Agent는 Tool의 **description**을 읽고 사용 시점을 판단
- [x] `external_factors`로 날씨 예보/지역 이벤트/공휴일을 한 번에 조회 가능

---

::: tip ✅ 다음
데이터 재료 준비 완료! → [Step 2: 나만의 수집 Agent 만들어 배포하기](step2-agent.md)
:::

