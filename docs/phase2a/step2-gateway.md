# Step 2: CS 도구 연결하기 (Gateway 확장) <span class="badge-time">⏱️ 15분</span> <span class="badge-difficulty">★★☆</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 Memory</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 2 Gateway+Browser</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 3 Agent</span>
  <span class="step-connector"></span>
  <span class="step">○ Step 4 Policy</span>
</div>

!!! info "이 Step의 목표"
    Phase 1에서 만든 Gateway에 **CS Tool 4개**를 추가 등록하고,
    **Browser Tool**을 연결하여 경쟁사 사이트 실시간 조회를 가능하게 합니다.
    
    기존 3개 + CS 4개 + Browser = 총 8개 Tool이 Agent에서 사용 가능합니다.

<div class="file-target">scripts/add-cs-targets.py</div>
---

## Phase 1 Gateway에 추가하기

Phase 1에서 이미 Gateway를 생성했습니다. 같은 Gateway에 Target을 추가합니다:

```
Phase 1: customer-profile, product-search, purchase-history (3개)
Phase 2A: lookup-order, return-policy, process-return, delivery-status (4개 추가)
Browser: 경쟁사/외부 사이트 실시간 조회 (1개 추가)
```

!!! tip "Gateway + Browser의 조합"
    Gateway에 등록된 Tool은 정형화된 데이터를 제공하고,
    Browser Tool은 외부 웹사이트에서 실시간 정보를 가져옵니다.
    
    예: 고객이 "다른 곳에서 더 싸게 파는데?" → Browser로 경쟁사 가격 확인 → 정확한 비교 응답

---

## 2-1. CS Target 추가 스크립트 실행

```bash
python3 scripts/add-cs-targets.py
```

??? example "스크립트가 하는 일 (내부)"
    ```python
    import json
    import boto3

    client = boto3.client("bedrock-agentcore-control", region_name="us-east-1")
    gateway_id = os.environ["GATEWAY_ID"]

    # CS Tool 4개 정의
    cs_tools = [
        {
            "name": "lookup-order",
            "lambda_arn": LOOKUP_ORDER_ARN,
            "schema": {
                "name": "lookup_order",
                "description": "주문번호로 주문 상세 조회. 주문 상태, 상품목록, 결제금액, 배송정보를 반환한다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "주문번호 (예: ORD-2024-001)"
                        }
                    },
                    "required": ["order_id"]
                }
            }
        },
        {
            "name": "return-policy",
            "lambda_arn": RETURN_POLICY_ARN,
            "schema": {
                "name": "return_policy",
                "description": "상품 카테고리별 반품/교환 정책 조회. 반품 가능 기한, 조건, 환불 방식을 반환한다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "상품 카테고리 (예: 식품, 화장품, 전자기기)"
                        }
                    },
                    "required": ["category"]
                }
            }
        },
        {
            "name": "process-return",
            "lambda_arn": PROCESS_RETURN_ARN,
            "schema": {
                "name": "process_return",
                "description": "반품/환불 처리 요청. 사유와 금액을 기반으로 처리하며, 5만원 초과 시 needs_escalation=true를 반환한다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "주문번호"
                        },
                        "reason": {
                            "type": "string",
                            "description": "반품 사유 (예: 상품불량, 단순변심, 오배송)"
                        },
                        "refund_amount": {
                            "type": "number",
                            "description": "환불 요청 금액 (원)"
                        }
                    },
                    "required": ["order_id", "reason", "refund_amount"]
                }
            }
        },
        {
            "name": "delivery-status",
            "lambda_arn": DELIVERY_STATUS_ARN,
            "schema": {
                "name": "delivery_status",
                "description": "주문의 배송 추적 정보 조회. 현재 위치, 예상 도착일, 배송 단계를 반환한다.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "order_id": {
                            "type": "string",
                            "description": "주문번호"
                        }
                    },
                    "required": ["order_id"]
                }
            }
        },
    ]

    # Gateway Target 등록
    for tool in cs_tools:
        client.create_gateway_target(
            gatewayIdentifier=gateway_id,
            name=tool["name"],
            targetConfiguration={
                "mcp": {
                    "lambda": {
                        "lambdaArn": tool["lambda_arn"],
                        "toolSchema": {
                            "inlinePayload": json.dumps(tool["schema"])
                        }
                    }
                }
            },
        )
        print(f"  ✅ {tool['name']} 등록 완료")
    ```

---

## 2-2. Browser Tool 추가

경쟁사 가격 비교, 리뷰 확인 등 외부 웹 데이터가 필요할 때 **Browser Tool**을 사용합니다:

```python title="Browser Tool 설정"
from strands import Agent
from strands.models import BedrockModel
from strands_tools.browser import AgentCoreBrowser
from mcp import ClientSession

from mcp.client.streamable_http import streamablehttp_client

# Browser Tool 초기화
browser_tool = AgentCoreBrowser(region="us-east-1")

# Gateway에서 CS Tools 가져오기
mcp = MCPClient(lambda: streamablehttp_client(GATEWAY_URL, auth=auth))

with mcp:
    gateway_tools = mcp.list_tools_sync()

    # Gateway Tools + Browser Tool 합치기
    tools = gateway_tools + [browser_tool.browser]

    agent = Agent(
        model=model,
        system_prompt=CS_SYSTEM_PROMPT,
        tools=tools
    )
    result = agent("ORD-2024-003 주문한 상품이 다른 사이트에서 더 싸요. 가격 확인해주세요.")
```

!!! info "Mock 경쟁사 사이트"
    워크샵에서는 Mock 사이트를 제공합니다:
    
    - 경쟁사 가격 비교: `${MOCK_SITE_URL}/competitor-prices.html`
    - 리뷰 조회: `${MOCK_SITE_URL}/competitor-prices.html`
    
    Browser Tool이 이 사이트를 방문하여 가격, 리뷰 정보를 가져옵니다.

---

## 2-3. 등록된 Tool Schema 정리

| Tool 이름 | 설명 (Agent가 읽는 것) | 파라미터 |
|-----------|----------------------|---------|
| `lookup_order` | 주문번호로 주문 상세 조회 (상태, 상품, 결제금액, 배송정보) | `order_id` (string) |
| `return_policy` | 상품 카테고리별 반품/교환 정책 조회 | `category` (string) |
| `process_return` | 반품/환불 처리. 5만원 초과 시 `needs_escalation=true` 반환 | `order_id`, `reason`, `refund_amount` |
| `delivery_status` | 배송 추적 정보 조회 (현재 위치, 예상 도착일) | `order_id` (string) |
| `browser` | 외부 웹사이트 방문 및 정보 추출 | URL, action 등 |

!!! warning "`process_return`의 특별한 점"
    이 Tool은 단순 조회가 아니라 **상태를 변경**합니다.
    
    또한 `refund_amount > 50,000`이면 `needs_escalation: true`를 반환합니다.
    Step 4(Policy)에서 이를 활용합니다.

---

## 2-4. 결과 확인

```bash
aws bedrock-agentcore-control list-gateway-targets \
  --gateway-identifier "$GATEWAY_ID" \
  --query 'items[].[name, status]' --output table
```

??? success "정상 출력 (7개 Target)"
    ```
    ---------------------------------
    |      ListGatewayTargets       |
    +-------------------+-----------+
    |  customer-profile  |  ACTIVE  |
    |  product-search    |  ACTIVE  |
    |  purchase-history  |  ACTIVE  |
    |  lookup-order      |  ACTIVE  |
    |  return-policy     |  ACTIVE  |
    |  process-return    |  ACTIVE  |
    |  delivery-status   |  ACTIVE  |
    +-------------------+-----------+
    ```

!!! info "7개 모두 ACTIVE 확인"
    Status가 `CREATING`이면 30초 정도 기다린 후 다시 확인하세요.
    Browser Tool은 Gateway Target이 아니라 Agent 코드에서 직접 추가하므로 여기에 표시되지 않습니다.

---

## 2-5. Agent가 인식하는지 빠르게 확인

```bash
python3 -c "
from strands_tools.browser import AgentCoreBrowser
from mcp import ClientSession

from mcp.client.streamable_http import streamablehttp_client
import os

url = os.environ['AGENTCORE_GATEWAY_URL']
mcp = MCPClient(lambda: streamablehttp_client(url, auth=auth))

# Browser Tool 초기화
browser_tool = AgentCoreBrowser(region='us-east-1')

with mcp:
    gateway_tools = mcp.list_tools_sync()
    all_tools = gateway_tools + [browser_tool.browser]
    print(f'총 {len(all_tools)} 개 Tool 인식됨:')
    for t in gateway_tools:
        print(f'  - {t.name} (Gateway)')
    print(f'  - browser (AgentCore Browser)')
"
```

??? success "정상 출력"
    ```
    총 8 개 Tool 인식됨:
      - customer_profile (Gateway)
      - product_search (Gateway)
      - purchase_history (Gateway)
      - lookup_order (Gateway)
      - return_policy (Gateway)
      - process_return (Gateway)
      - delivery_status (Gateway)
      - browser (AgentCore Browser)
    ```

---

## 이해 체크

- [x] 같은 Gateway에 Target을 **추가**만 하면 Agent가 자동 인식
- [x] Agent 코드 수정 없이 Gateway Tool 확장 가능 (Gateway의 핵심 가치)
- [x] Browser Tool은 Gateway와 별개로 Agent 코드에서 직접 추가
- [x] `tools = gateway_tools + [browser_tool.browser]` 패턴으로 조합
- [x] `process_return`은 에스컬레이션 판단을 위한 `needs_escalation` 필드를 반환

---

!!! success "다음"
    CS Tool + Browser 등록 완료! → [Step 3: Agent + Memory 연동](step3-agent.md)
