# FAQ & 트러블슈팅

!!! warning "막혔을 때 여기를 먼저 확인하세요"
    대부분의 문제는 아래 10개 중 하나입니다. 3분 안에 해결되지 않으면 SA에게 손들어주세요!

---

## 자주 묻는 질문 (FAQ)

??? question "Q1. `ModuleNotFoundError: No module named 'strands'`"
    **원인**: Python 가상환경이 활성화되지 않음
    
    **해결**:
    ```bash
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

??? question "Q2. `AccessDeniedException` (Bedrock 모델 호출 시)"
    **원인**: IAM Role에 Bedrock 권한 없음 또는 Model Access 미승인
    
    **해결**: SA에게 요청하세요. Workshop Studio 계정 권한 이슈입니다.
    
    **확인 방법**:
    ```bash
    aws bedrock list-foundation-models --query 'modelSummaries[?modelId==`anthropic.claude-sonnet-4-6-20250514-v1:0`].modelId'
    ```

??? question "Q3. `AGENTCORE_GATEWAY_URL` 환경변수가 비어있다"
    **원인**: Phase 1 Step 1에서 `setup-gateway.py` 실행 후 export를 안 함
    
    **해결**:
    ```bash
    # 스크립트 다시 실행 (멱등성 있음)
    python3 scripts/setup-gateway.py
    # 출력된 URL을 복사해서:
    export AGENTCORE_GATEWAY_URL=<출력된 URL>
    ```

??? question "Q4. Gateway Target이 `CREATING` 상태에서 안 넘어감"
    **원인**: Lambda 함수가 배포되지 않았거나 리전이 다름
    
    **해결**: 30초~1분 기다린 후 다시 확인
    ```bash
    aws bedrock-agentcore-control list-gateway-targets \
      --gateway-identifier "$GATEWAY_ID" \
      --query 'items[].[name, status]' --output table
    ```
    
    여전히 CREATING이면 SA에게 문의하세요.

??? question "Q5. `playwright` 관련 에러 (Browser Tool)"
    **원인**: Chromium이 설치되지 않음
    
    **해결**:
    ```bash
    playwright install chromium
    # 또는 의존성 포함:
    playwright install chromium --with-deps
    ```

??? question "Q6. `nest_asyncio` 에러"
    **원인**: Python 버전 호환 이슈 또는 패키지 미설치
    
    **해결**:
    ```bash
    pip install nest-asyncio>=1.6
    ```

??? question "Q7. Memory 생성은 됐는데 retrieve가 안 됨"
    **원인**: Memory에 아직 데이터가 없음 (첫 호출)
    
    **해결**: 정상입니다! 첫 호출 시 빈 결과가 나오고, Agent 응답 후 `save_turn()`으로 저장됩니다. 두 번째 호출부터 맥락이 반환됩니다.

??? question "Q8. `agentcore deploy` 시 타임아웃"
    **원인**: 코드 패키징 & 업로드에 3~5분 소요
    
    **해결**: 기다리세요. `agentcore status --name <NAME>`으로 진행 상태 확인:
    ```bash
    agentcore status --name rcg-recommend-agent
    # CREATING → ACTIVE 되면 성공
    ```

??? question "Q9. Policy가 적용되지 않는 것 같다"
    **원인**: Policy는 `process_return` Lambda가 `needs_escalation: true`를 반환해야 트리거됨
    
    **해결**: 5만원 이하 환불은 정상적으로 ALLOW됩니다. 7만원 이상으로 테스트하세요:
    ```bash
    # 에스컬레이션 테스트 (69,000원 상품)
    agentcore invoke --agent rcg-cs-agent \
      '{"message": "ORD-2024-999 환불 요청합니다", "actor_id": "C003"}'
    ```

??? question "Q10. Observability Dashboard가 비어있다"
    **원인**: Agent가 한 번도 호출되지 않았거나, Dashboard 로딩에 1~2분 지연
    
    **해결**:
    1. 먼저 Agent를 한 번 호출하세요 (`agentcore invoke`)
    2. 1~2분 기다린 후 Dashboard 새로고침
    3. Region이 `us-east-1`인지 확인

---

## 환경변수 빠른 확인

모든 환경변수가 설정되어 있는지 한번에 확인:

```bash
echo "=== 환경변수 체크 ==="
echo "AWS_REGION:          ${AWS_REGION:-❌ 미설정}"
echo "ACCOUNT_ID:          ${ACCOUNT_ID:-❌ 미설정}"
echo "GATEWAY_URL:         ${AGENTCORE_GATEWAY_URL:-❌ 미설정}"
echo "GATEWAY_ID:          ${GATEWAY_ID:-❌ 미설정}"
echo "MEMORY_ID:           ${AGENTCORE_MEMORY_ID:-⏳ Phase 2에서 설정}"
echo "MOCK_SITE_URL:       ${MOCK_SITE_URL:-❌ 미설정}"
```

---

## 긴급 복구 명령어

```bash
# Gateway가 꼬였을 때 → 스크립트 재실행 (멱등성 있음)
python3 scripts/setup-gateway.py

# 배포된 Agent가 응답 안 할 때 → 로그 확인
agentcore logs --name <AGENT_NAME> --tail 50

# 처음부터 다시 하고 싶을 때 → 가상환경 재생성
deactivate
rm -rf .venv
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

!!! tip "그래도 안 되면?"
    손을 들어 SA에게 도움을 요청하세요. 디버깅하느라 시간을 쓰기보다 빠르게 도움받는 것이 워크샵에서는 더 효율적입니다! 🙋
