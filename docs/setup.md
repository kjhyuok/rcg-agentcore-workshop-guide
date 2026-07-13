# 환경 세팅

!!! warning "시작 전 반드시 완료"
    이 페이지의 모든 단계를 완료해야 Phase 1을 시작할 수 있습니다.

---

## 워크샵 환경 개요

이 워크샵은 **사전 구성된 EC2 인스턴스**에서 진행됩니다. CloudFormation으로 배포된 환경에 다음이 이미 준비되어 있습니다:

- VS Code Server (브라우저 기반 IDE)
- Python 3.12 + 필수 라이브러리 (strands-agents, bedrock-agentcore, boto3 등)
- Node.js 22 + AgentCore CLI (`@aws/agentcore`)
- 워크샵 코드 (`~/workshop`)
- Lambda 11개 + IAM Role + Mock 사이트 (모두 배포 완료)

---

## Step 1. Event Outputs 확인

Workshop Studio 이벤트 페이지에서 **Event outputs**를 확인합니다:

| Key | 설명 |
|-----|------|
| **AccountId** | AWS 계정 ID |
| **CodeServerUrl** | VS Code Server 접속 URL |
| **CodeServerPassword** | VS Code Server 비밀번호 |
| **GatewayRoleArn** | AgentCore Gateway용 IAM Role ARN |
| **RuntimeRoleArn** | AgentCore Runtime용 IAM Role ARN |
| **MockSiteUrl** | Browser Tool용 Mock 사이트 URL |
| **PlaygroundUrl** | Agent Playground 접속 URL |

![Event Outputs](assets/images/setup/event-output-example.png)

---

## Step 2. Code Server 접속

**Event outputs**에서 **CodeServerUrl**을 클릭하여 VS Code Server에 접속합니다.

- 비밀번호: **CodeServerPassword** 값 입력 (기본값: `workshop123!`)
- 접속하면 `~/workshop` 폴더가 자동으로 열려 있습니다

---

## Step 3. 환경 확인

Code Server 하단의 터미널(`ec2-user@ip-xxx:~$`)에서 확인합니다.

### 3-1. 환경변수 확인

터미널을 열면 `.env.w001`이 자동 로드됩니다:

```bash
echo $AWS_REGION    # us-west-2
echo $ACCOUNT_ID   # 계정 ID
```

!!! tip "환경변수가 비어 있으면"
    새 터미널을 열었거나 세션이 끊겼을 때:
    ```bash
    source ~/workshop/.env.w001
    ```

### 3-2. AgentCore CLI 확인

```bash
agentcore --help
```

### 3-3. Bedrock 모델 접근 확인

```bash
python -c "
from strands import Agent
from strands.models.bedrock import BedrockModel
model = BedrockModel(model_id='us.anthropic.claude-sonnet-4-20250514', region_name='us-west-2')
agent = Agent(model=model, system_prompt='테스트')
print(agent('안녕? 한 줄로 답해.'))
print('✅ Bedrock 모델 접근 OK')
"
```

### 3-4. Lambda 배포 확인

```bash
aws lambda list-functions \
  --query "Functions[?starts_with(FunctionName, 'rcg-workshop')].FunctionName" \
  --output table
```

??? success "정상 출력 (11개 Lambda)"
    ```
    +---------------------------------------+
    |  rcg-workshop-customer-profile        |
    |  rcg-workshop-product-search          |
    |  rcg-workshop-purchase-history        |
    |  rcg-workshop-cs-lookup-order         |
    |  rcg-workshop-cs-return-policy        |
    |  rcg-workshop-cs-process-return       |
    |  rcg-workshop-cs-delivery-status      |
    |  rcg-workshop-demand-inventory        |
    |  rcg-workshop-demand-sales-trend      |
    |  rcg-workshop-demand-external-factors |
    |  rcg-workshop-demand-purchase-order   |
    +---------------------------------------+
    ```

---

## 📋 환경변수 한눈에 보기 (워크샵 전체)

!!! tip "이 블록을 참고하세요"
    아래 환경변수는 워크샵 진행하며 채워집니다. Phase 시작 전에 이 값들이 설정되어 있는지 확인하세요.

<div class="env-block">
<span class="env-label"># --- 사전 설정됨 (.env.w001 — 자동 로드) ---</span><br>
export AWS_REGION=us-west-2<br>
export ACCOUNT_ID=&lt;계정 ID&gt;<br>
export PARTICIPANT_ID=w001<br>
export GATEWAY_ROLE_ARN=arn:aws:iam::${ACCOUNT_ID}:role/rcg-workshop-gateway-role<br>
export RUNTIME_ROLE_ARN=arn:aws:iam::${ACCOUNT_ID}:role/rcg-workshop-runtime-role<br>
<br>
<span class="env-label"># --- Phase 1 (Gateway 생성 후 채워짐) ---</span><br>
export AGENTCORE_GATEWAY_URL=&lt;setup-gateway.py 출력값&gt;<br>
export GATEWAY_ID=&lt;Gateway ID&gt;<br>
<br>
<span class="env-label"># --- Phase 2 (Memory 생성 후 채워짐) ---</span><br>
export AGENTCORE_MEMORY_ID=&lt;setup-memory.py 출력값&gt;<br>
<br>
<span class="env-label"># --- Phase 3 (배포 후 채워짐) ---</span><br>
export MY_AGENT_ARN=&lt;agentcore deploy 출력값&gt;<br>
</div>

---

## 🔍 환경변수 체크 (Phase 시작 전 확인용)

```bash
echo "=== 기본 설정 ==="
echo "AWS_REGION: $AWS_REGION"
echo "ACCOUNT_ID: $ACCOUNT_ID"
echo "GATEWAY_ROLE_ARN: $GATEWAY_ROLE_ARN"
echo "RUNTIME_ROLE_ARN: $RUNTIME_ROLE_ARN"
echo ""
echo "=== Phase 1 (Gateway 생성 후) ==="
echo "AGENTCORE_GATEWAY_URL: $AGENTCORE_GATEWAY_URL"
echo "GATEWAY_ID: $GATEWAY_ID"
echo ""
echo "=== Phase 2 (Memory 생성 후) ==="
echo "AGENTCORE_MEMORY_ID: $AGENTCORE_MEMORY_ID"
echo ""
echo "=== Phase 3 (배포 후) ==="
echo "MY_AGENT_ARN: $MY_AGENT_ARN"
```

!!! tip "값이 비어 있으면"
    - 기본 설정이 비었으면: `source ~/workshop/.env.w001`
    - Phase 1~3 값이 비었으면: 해당 Phase의 setup 스크립트를 아직 실행하지 않은 것 (정상)

---

!!! success "준비 완료!"
    모든 체크가 통과했으면 [Phase 1: Gateway + Runtime + Observability](phase1/index.md)로 이동하세요.
