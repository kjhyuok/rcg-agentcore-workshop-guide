# Step 2: 수요 예측 Gateway Target 추가 <span class="badge-time">⏱️ 10분</span> <span class="badge-difficulty">★★☆</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 Memory</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 2 Gateway+Browser</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 3 Agent</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 4 Policy</span>
</div>

!!! info "소요 시간: 10분"
    수요 예측에 필요한 4개 Tool을 Gateway에 등록하고,
    **Browser Tool**을 추가하여 뉴스/날씨 사이트에서 실시간 외부 요인을 수집합니다.

<div class="file-target">scripts/add-demand-targets.py</div>
---

## 추가할 Tool 목록

| Tool 이름 | 기능 | Lambda |
|-----------|------|--------|
| `inventory_status` | 현재 재고 현황 조회 | `workshop-inventory-status` |
| `sales_trend` | 최근 판매 트렌드 분석 | `workshop-sales-trend` |
| `external_factors` | 외부 요인 (날씨/이벤트) 조회 | `workshop-external-factors` |
| `purchase_order` | 발주 실행 | `workshop-purchase-order` |
| **`browser`** | 뉴스/날씨 사이트 실시간 조회 | Agent 내장 Tool |

---

## Tool Schema 정의

### 1. inventory_status (재고 현황)

```json
{
  "name": "inventory_status",
  "description": "매장의 현재 재고 현황을 카테고리별로 조회합니다. 재고 부족 품목을 확인할 때 사용합니다.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "store_id": {
        "type": "string",
        "description": "매장 ID (예: store-001)"
      },
      "category": {
        "type": "string",
        "description": "상품 카테고리 (예: 식품, 음료, 생활용품). 생략하면 전체 조회."
      }
    },
    "required": ["store_id"]
  }
}
```

### 2. sales_trend (판매 트렌드)

```json
{
  "name": "sales_trend",
  "description": "최근 판매 데이터를 분석하여 트렌드를 반환합니다. 주간/월간 비교, 성장률, 계절성 패턴을 포함합니다.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "store_id": {
        "type": "string",
        "description": "매장 ID"
      },
      "period": {
        "type": "string",
        "enum": ["7d", "30d", "90d"],
        "description": "분석 기간"
      },
      "category": {
        "type": "string",
        "description": "상품 카테고리"
      }
    },
    "required": ["store_id", "period"]
  }
}
```

### 3. external_factors (외부 요인)

```json
{
  "name": "external_factors",
  "description": "수요에 영향을 주는 외부 요인을 조회합니다. 날씨 예보, 지역 이벤트, 공휴일, 프로모션 일정을 포함합니다.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "store_id": {
        "type": "string",
        "description": "매장 ID"
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

### 4. purchase_order (발주 실행)

```json
{
  "name": "purchase_order",
  "description": "분석 결과를 바탕으로 발주를 실행합니다. 금액이 500,000원을 초과하면 승인이 필요합니다.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "store_id": {
        "type": "string",
        "description": "매장 ID"
      },
      "items": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "product_id": { "type": "string" },
            "product_name": { "type": "string" },
            "quantity": { "type": "integer" },
            "unit_price": { "type": "number" }
          },
          "required": ["product_id", "quantity"]
        },
        "description": "발주 항목 리스트"
      },
      "priority": {
        "type": "string",
        "enum": ["normal", "urgent"],
        "description": "발주 긴급도"
      },
      "reason": {
        "type": "string",
        "description": "발주 사유"
      }
    },
    "required": ["store_id", "items", "reason"]
  }
}
```

---

## Gateway에 Target 등록

```bash
# 기존 Gateway ID 확인
GATEWAY_ID=$(agentcore gateway list --query 'gateways[0].gatewayId' --output text)

# 4개 Target 등록
for TOOL in inventory_status sales_trend external_factors purchase_order; do
  agentcore gateway add-target \
    --gateway-id $GATEWAY_ID \
    --name $TOOL \
    --type LAMBDA \
    --endpoint "arn:aws:lambda:us-east-1:${AWS_ACCOUNT_ID}:function:workshop-${TOOL//_/-}" \
    --schema-file "schemas/${TOOL}.json"
done
```

---

## Browser Tool 추가: 뉴스/날씨 실시간 조회

수요 예측의 정확도를 높이려면 **실시간 외부 정보**가 중요합니다.
Browser Tool을 사용하면 Agent가 뉴스/날씨 사이트를 직접 방문하여 최신 정보를 수집합니다:

```python title="Gateway Tools + Browser Tool 조합"
from strands import Agent
from strands.models import BedrockModel
from strands_tools.browser import AgentCoreBrowser
from mcp import ClientSession

from mcp.client.streamable_http import streamablehttp_client

# Browser Tool 초기화
browser_tool = AgentCoreBrowser(region="us-east-1")

# Gateway에서 수요예측 Tools 가져오기
mcp = MCPClient(lambda: streamablehttp_client(GATEWAY_URL, auth=auth))

with mcp:
    gateway_tools = mcp.list_tools_sync()

    # Gateway Tools + Browser Tool 합치기
    tools = gateway_tools + [browser_tool.browser]

    agent = Agent(
        model=model,
        system_prompt=DEMAND_SYSTEM_PROMPT,
        tools=tools
    )
    result = agent("store-001의 이번 주 음료 수요를 예측해줘. 날씨도 고려해서.")
```

!!! info "Mock 뉴스/날씨 사이트"
    워크샵에서는 Mock 사이트를 제공합니다:
    
    - 날씨 예보: `${MOCK_SITE_URL}/weather-forecast.html`
    - 지역 뉴스: `${MOCK_SITE_URL}/trend-news.html`
    
    Agent가 Browser Tool로 이 사이트를 방문하여 날씨 정보(폭염, 한파 등)와
    지역 이벤트(축제, 마라톤 등)를 파악합니다.

!!! tip "Browser가 수요 예측에 유용한 이유"
    `external_factors` Lambda는 사전 등록된 이벤트만 반환합니다.
    하지만 Browser Tool로 뉴스를 검색하면 **갑작스런 이슈**(단수, 정전, 유명인 방문 등)도
    실시간으로 캐치할 수 있습니다.

---

## 등록 확인

```bash
agentcore gateway list-targets --gateway-id $GATEWAY_ID
```

예상 출력 (Phase 1 + Phase 2B 합계 7개):
```
┌──────────────────┬──────────┬────────┐
│ Name             │ Type     │ Status │
├──────────────────┼──────────┼────────┤
│ customer_profile │ LAMBDA   │ ACTIVE │  ← Phase 1
│ product_search   │ LAMBDA   │ ACTIVE │  ← Phase 1
│ purchase_history │ LAMBDA   │ ACTIVE │  ← Phase 1
│ inventory_status │ LAMBDA   │ ACTIVE │  ← Phase 2B
│ sales_trend      │ LAMBDA   │ ACTIVE │  ← Phase 2B
│ external_factors │ LAMBDA   │ ACTIVE │  ← Phase 2B
│ purchase_order   │ LAMBDA   │ ACTIVE │  ← Phase 2B
└──────────────────┴──────────┴────────┘
```

!!! note "Browser Tool은 Gateway에 등록하지 않습니다"
    Browser Tool은 Agent 코드에서 직접 추가하는 방식입니다.
    Gateway Target은 Lambda 기반 Tool만 등록합니다.

---

!!! tip "Tool 설계 팁"
    `purchase_order`의 description에 "500,000원 초과 시 승인 필요"를 명시했습니다.
    Agent가 이 설명을 읽고 Policy 체크를 선제적으로 할 수 있습니다.

!!! success "다음 단계"
    Tool 준비 완료! [Step 3: Agent 코드 작성](step3-agent.md)으로 이동합니다.
