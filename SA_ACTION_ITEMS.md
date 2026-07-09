# RCG 2차 AgentCore Workshop — SA Action Items

---

**워크샵**: Build! Deploy! Observe! 리테일 Agent 실전 구축하기

**SA 구성**: Sr. SA 2명 (A, B) + Associate SA 3명 (C, D, E)

**기준일**: D-Day 기준 역산 (일정 확정 후 날짜 기입)

---

## 역할 분배 요약

| 역할 | 담당 | 핵심 책임 |
|------|------|----------|
| **SA-A (Sr.)** | 총괄 & 인프라 | Workshop Studio, IAM, Bedrock Limit, Orchestrator |
| **SA-B (Sr.)** | 콘텐츠 & 검증 | 가이드 최종 검수, 코드 E2E 검증, 리허설 설계 |
| **SA-C (Assoc.)** | Lambda & Gateway | Lambda 11개 배포, Gateway 테스트, Mock 사이트 |
| **SA-D (Assoc.)** | 환경 & 도구 | bootstrap.sh 검증, agentcore CLI, Code Editor 세팅 |
| **SA-E (Assoc.)** | 당일 운영 & 지원 | 시상, 참가자 지원, Evaluation 실행, 발표 진행 |

---

## SA-A (Sr. SA) — 총괄 & 인프라 리드

### 책임 범위
- 전체 일정 조율 및 의사결정
- AWS 계정/인프라 레벨 작업 (IAM, Quota, Workshop Studio)
- Orchestrator Agent 사전 배포
- 고객 커뮤니케이션 (일정, 참가자 안내)

### Action Items

| # | Task | 마감 | 산출물 | 비고 |
|---|------|------|--------|------|
| A-1 | 일정 확정 & 고객 확인 | D-28 | 확정 일정 공유 | 100명 규모, 장소 |
| A-2 | Workshop Studio 100석 예약 | D-21 | 예약 확인서 | `ml.t3.medium`, 5시간 |
| A-3 | Bedrock Model Access 100명 동시 limit increase 요청 | D-21 | Service Quota 승인 | `us-east-1`, Claude Sonnet 4.6 |
| A-4 | Browser 세션 동시 100명 quota 확인 | D-21 | quota 확인 결과 | AgentCore Browser |
| A-5 | Code Interpreter 동시 quota 확인 | D-21 | quota 확인 결과 | |
| A-6 | IAM Role 3종 생성 (참가자/Lambda/Gateway) | D-14 | CloudFormation 스택 | SA-C와 협업 |
| A-7 | Orchestrator Agent 사전 배포 (`phase3_orchestrator.py`) | D-7 | Endpoint ARN | SA-B 검증 |
| A-8 | 참가자 안내 메일 발송 | D-3 | 메일 발송 완료 | URL, 준비물 없음 안내 |
| A-9 | D-Day 전체 진행 (Keynote, 시간 관리) | D-Day | | |
| A-10 | Workshop Studio 종료 & 비용 정산 | D+1 | 비용 리포트 | |

### 의사결정 필요 사항
- [ ] Git Repo 위치 (CodeCommit vs GitHub)
- [ ] 시상품 예산 (4개 카테고리)
- [ ] Keynote 발표자 (SA-A 본인 or 고객 임원)

---

## SA-B (Sr. SA) — 콘텐츠 & 검증 리드

### 책임 범위
- MkDocs 가이드 최종 검수 & QA
- starter-code 전체 E2E 실행 검증
- 리허설 시나리오 설계 & 진행
- 가이드 배포 (S3 + CloudFront)

### Action Items

| # | Task | 마감 | 산출물 | 비고 |
|---|------|------|--------|------|
| B-1 | MkDocs 가이드 전체 리뷰 (오탈자, 링크, 코드) | D-14 | 리뷰 피드백 | 19페이지 전체 |
| B-2 | `bedrock-agentcore` 패키지 최신 버전 import 경로 확인 | D-14 | 확인 결과 | pip show bedrock-agentcore |
| B-3 | `agentcore` CLI 설치 방법 & 명령어 형식 확정 | D-14 | CLI 가이드 | deploy, invoke, status |
| B-4 | Phase 1 E2E 실행 (Gateway → Agent → Runtime → Trace) | D-10 | 성공 스크린샷 | 실제 계정에서 실행 |
| B-5 | Phase 2A E2E 실행 (Memory → Browser → Policy) | D-10 | 성공 스크린샷 | |
| B-6 | Phase 2B E2E 실행 | D-10 | 성공 스크린샷 | |
| B-7 | Phase 3 E2E 실행 (Orchestrator 연결 → Evaluation) | D-10 | 성공 스크린샷 | SA-A의 Orchestrator 사용 |
| B-8 | 실행 중 발견된 이슈 → 가이드/코드 수정 | D-7 | 수정 커밋 | |
| B-9 | MkDocs → S3 + CloudFront 배포 | D-7 | 가이드 URL | |
| B-10 | SA 5명 리허설 설계 & 진행 (전 Phase 90분) | D-7 | 리허설 완료 | 이슈 0건 목표 |
| B-11 | Evaluation 스크립트 실제 Agent로 테스트 | D-7 | 점수 리포트 예시 | |
| B-12 | FAQ 페이지 보완 (리허설 중 발견된 이슈 추가) | D-5 | FAQ 업데이트 | |

### 검증 체크리스트
- [ ] 모든 코드 블록이 복붙 시 동작하는가?
- [ ] 환경변수 누락 시 명확한 에러 메시지가 나오는가?
- [ ] Mermaid 다이어그램이 모두 렌더링되는가?
- [ ] AWS 아이콘 이미지가 모두 로딩되는가?

---

## SA-C (Associate SA) — Lambda & Gateway 담당

### 책임 범위
- Lambda 11개 AWS 배포 & 테스트
- Mock 사이트 3개 S3 배포
- Gateway 생성 & Target 등록 테스트
- CFn/CDK 배포 자동화

### Action Items

| # | Task | 마감 | 산출물 | 비고 |
|---|------|------|--------|------|
| C-1 | Lambda 11개 로컬 테스트 (각 handler 직접 호출) | D-14 | 테스트 결과 | Mock 데이터 응답 확인 |
| C-2 | `deploy-lambdas.sh` 실행하여 11개 배포 | D-14 | Lambda ARN 목록 | `us-east-1` |
| C-3 | 각 Lambda 개별 invoke 테스트 | D-14 | 11개 정상 응답 | 404/200 케이스 모두 |
| C-4 | Mock 사이트 3개 S3 배포 (`deploy-mock-sites.sh`) | D-14 | Mock URL 3개 | CloudFront 선택 |
| C-5 | Mock 사이트 브라우저 접속 확인 | D-14 | 스크린샷 | 3개 모두 |
| C-6 | Gateway 생성 테스트 (`setup-gateway.py` 실행) | D-10 | Gateway ID + URL | |
| C-7 | Gateway Target 11개 등록 & ACTIVE 확인 | D-10 | list-targets 출력 | |
| C-8 | Memory 생성 테스트 (`setup-memory.py` 실행) | D-10 | Memory ID | |
| C-9 | CloudFormation 템플릿 작성 (IAM + Lambda 일괄) | D-7 | `cfn-workshop-base.yaml` | SA-A와 협업 |
| C-10 | D-Day Lambda warm-up 스크립트 준비 | D-3 | `warmup.sh` | 각 Lambda 1회 호출 |

### 배포 확인 체크리스트
```bash
# 이 명령어로 전체 확인
aws lambda list-functions \
  --query "Functions[?starts_with(FunctionName, 'rcg-workshop')].{Name:FunctionName,Runtime:Runtime}" \
  --output table --region us-east-1
```

---

## SA-D (Associate SA) — 환경 & 도구 담당

### 책임 범위
- SageMaker Code Editor / Workshop Studio 환경 검증
- bootstrap.sh 스크립트 완성 & 테스트
- 참가자 경험 시뮬레이션 (처음부터 끝까지)
- 네트워크/방화벽 이슈 사전 확인

### Action Items

| # | Task | 마감 | 산출물 | 비고 |
|---|------|------|--------|------|
| D-1 | Workshop Studio 테스트 계정 1개로 Code Editor 접속 | D-14 | 접속 스크린샷 | |
| D-2 | `bootstrap.sh` Code Editor에서 실행 & 디버깅 | D-14 | 수정된 스크립트 | 패키지 설치 시간 측정 |
| D-3 | Playwright Chromium 설치 가능 여부 확인 | D-14 | 결과 문서 | Code Editor 환경 제약 |
| D-4 | `agentcore` CLI 설치 방법 확인 & bootstrap에 반영 | D-14 | CLI 설치 가이드 | pip? binary? |
| D-5 | Git Repo clone 테스트 (Code Editor에서) | D-10 | 클론 성공 확인 | 인증 방법 확인 |
| D-6 | 참가자 시뮬레이션: bootstrap → Phase 1 완료까지 | D-10 | 소요 시간 측정 | 30분 이내 목표 |
| D-7 | 참가자 시뮬레이션: Phase 2A 또는 2B 완료 | D-10 | 소요 시간 측정 | 60분 이내 목표 |
| D-8 | 네트워크: AgentCore API, Bedrock, S3 접근 테스트 | D-7 | 테스트 결과 | VPC 엔드포인트 필요? |
| D-9 | 포트 포워딩 확인 (Streamlit 등 로컬 서비스) | D-7 | 접근 방법 정리 | presigned URL? |
| D-10 | Workshop Studio 100명 동시 접속 시 Cold Start 시간 | D-7 | 측정 결과 | 리허설 시 확인 |
| D-11 | 최종 `requirements.txt` 버전 핀닝 | D-5 | 고정 버전 파일 | 당일 pip 에러 방지 |

### 환경 검증 매트릭스

| 항목 | 확인 결과 | 비고 |
|------|----------|------|
| Python 버전 | | 3.10+ 필요 |
| pip install 시간 | | 5분 이내 목표 |
| playwright install | | chromium 설치 가능? |
| agentcore CLI | | 어떻게 설치? |
| Git clone | | SSH? HTTPS? |
| Bedrock 호출 | | IAM Role 연결 |
| 포트 접근 | | 8501 등 |

---

## SA-E (Associate SA) — 당일 운영 & 참가자 지원

### 책임 범위
- D-Day 현장 운영 (등록, 시간, 시상)
- 참가자 실시간 지원 (Floor 돌며 도움)
- Evaluation 실행 & 점수 집계
- 발표 진행 & 시상

### Action Items

| # | Task | 마감 | 산출물 | 비고 |
|---|------|------|--------|------|
| E-1 | 시상 카테고리 & 상품 준비 | D-7 | 시상품 4개 | Best Agent, Creative, Architecture, Speed |
| E-2 | FAQ 숙지 (Top 10 에러 + 해결법) | D-7 | | 당일 즉시 대응용 |
| E-3 | 참가자 지원 스크립트 준비 (환경변수 체크 원라이너) | D-5 | cheat-sheet | 참가자 PC에서 바로 실행 |
| E-4 | Evaluation 실행 연습 (`run-evaluation.py`) | D-5 | 점수 산출 연습 | 시나리오별 5문제 |
| E-5 | 점수 집계 스프레드시트 준비 | D-3 | Google Sheet | 실시간 점수 입력 |
| E-6 | 발표 타이머 (팀당 2분) 준비 | D-3 | 타이머 도구 | 화면 공유용 |
| E-7 | 참가자 등록 & Workshop Studio 계정 배포 | D-Day AM | 계정 매핑 | 이름↔계정 |
| E-8 | Floor 지원 (Phase 1 시간대 집중) | D-Day | | 환경 이슈 집중 시간 |
| E-9 | Phase 3 Evaluation 일괄 실행 | D-Day PM | 점수 리포트 | 참가자별 Agent ARN 수집 |
| E-10 | 시상식 진행 & 사진 촬영 | D-Day PM | 사진 | |

### 당일 참가자 지원 Cheat Sheet

```bash
# 환경변수 전체 체크 (참가자 PC에서 실행)
echo "AWS_REGION: ${AWS_REGION:-❌}"
echo "GATEWAY_URL: ${AGENTCORE_GATEWAY_URL:-❌}"
echo "MEMORY_ID: ${AGENTCORE_MEMORY_ID:-⏳}"

# venv 활성화 안 됐을 때
source ~/workshop/starter-code/.venv/bin/activate

# Gateway 재생성 (멱등성 있음)
python3 scripts/setup-gateway.py

# Agent 재배포
agentcore deploy --auto-update-on-conflict
```

---

## 공통 마일스톤 타임라인

```
D-28 ┃ SA-A: 일정 확정
     ┃
D-21 ┃ SA-A: Workshop Studio 예약 + Quota 요청
     ┃ SA-B: bedrock-agentcore 패키지 확인
     ┃ SA-C: Lambda 로컬 테스트 시작
     ┃ SA-D: Code Editor 접속 테스트
     ┃
D-14 ┃ SA-A: IAM Role 생성
     ┃ SA-B: 가이드 전체 리뷰 완료
     ┃ SA-C: Lambda 11개 + Mock 사이트 배포 완료
     ┃ SA-D: bootstrap.sh 완성 + 환경 검증 완료
     ┃
D-10 ┃ SA-B: Phase 1~3 E2E 검증 완료
     ┃ SA-C: Gateway + Memory 테스트 완료
     ┃ SA-D: 참가자 시뮬레이션 완료
     ┃
D-7  ┃ ★ SA 5명 전원 리허설 (90분, 전 Phase 실행)
     ┃ SA-A: Orchestrator 배포
     ┃ SA-B: 가이드 CloudFront 배포
     ┃ SA-C: CFn 스택 완성
     ┃ SA-D: requirements.txt 핀닝
     ┃ SA-E: 시상품 준비 + FAQ 숙지
     ┃
D-3  ┃ SA-A: 참가자 안내 메일
     ┃ SA-E: 점수 집계표 + 타이머 준비
     ┃
D-1  ┃ SA-C: Lambda warm-up
     ┃ SA-D: Workshop Studio 최종 확인
     ┃
D-Day┃ 전원 현장 (09:30 도착)
```

---

## 주간 싱크업 안건

| 주차 | 핵심 안건 |
|------|----------|
| D-28~21 | 일정/장소 확정, Quota 요청 결과, Repo 위치 결정 |
| D-21~14 | Lambda 배포 상태, Code Editor 환경 이슈, 가이드 리뷰 |
| D-14~7 | E2E 검증 결과, 블로커 해결, 리허설 준비 |
| D-7 | **리허설** (전원 필수 참석) |
| D-3~1 | 최종 점검, 참가자 안내, warm-up |

---

## 리스크 & 대응

| 리스크 | 확률 | 영향 | 대응 | 담당 |
|--------|------|------|------|------|
| Bedrock Quota 부족 (100명 동시) | 중 | 치명 | D-21에 미리 요청, 안 되면 그룹 분할 | SA-A |
| agentcore CLI 미공개 | 중 | 높음 | boto3 직접 호출 대안 코드 준비 | SA-B |
| Browser/CI quota 부족 | 중 | 중 | Phase 2에서 Browser 선택적으로 변경 | SA-A |
| Workshop Studio 네트워크 제약 | 낮 | 높음 | VPC Endpoint 또는 NAT Gateway | SA-D |
| 참가자 90% 이상 막힘 (Phase 1) | 낮 | 치명 | SA-E Floor 지원 + 라이브 코딩 전환 | SA-E |
