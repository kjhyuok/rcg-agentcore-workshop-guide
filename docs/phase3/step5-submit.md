# Step 5: 아레나 제출하기 <span class="badge-time">⏱️ 5분</span> <span class="badge-difficulty">★☆☆</span>

<div class="step-progress">
  <span class="step done">✓ Step 1 Gateway</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 2 설계</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 3 바이브코딩</span>
  <span class="step-connector done"></span>
  <span class="step done">✓ Step 4 배포 & 테스트</span>
  <span class="step-connector done"></span>
  <span class="step active">● Step 5 제출</span>
</div>

::: info 이 Step의 목표
완성한 Agent 코드를 **워크샵 아레나**에 제출합니다.
팀별 Agent를 비교·평가하는 마지막 단계입니다.
:::

## 제출 파일 구성

| 파일 | 필수 여부 | 설명 |
|------|-----------|------|
| `main.py` | **필수** | Agent 코드 (`@app.entrypoint` + System Prompt) |
| `my-agent-design.md` | **필수** | Step 2에서 작성한 Agent 설계서 |
| Lambda Python 코드 | 선택 | 직접 만든 커스텀 Tool Lambda (예: `lambda_inventory.py`) |

::: tip 설계서가 평가 기준의 핵심입니다
아레나에서는 **설계서의 시나리오 창의성**과 **main.py의 동작 완성도**를 함께 평가합니다.
설계서가 구체적일수록, 그리고 main.py가 설계서대로 동작할수록 높은 점수를 받습니다.
:::

## 제출 방법

### 1. 파일 압축

```bash
cd ~/workshop/starter-code

# 제출용 폴더 만들기
mkdir -p submission
cp agents/phase3/app/phase3/main.py submission/
cp my-agent-design.md submission/

# (선택) 직접 만든 Lambda 코드가 있다면 함께 복사
# cp lambdas/my_custom_tool/index.py submission/lambda_my_tool.py

# zip으로 압축 (팀명으로)
cd submission
zip ../팀명_submission.zip *
```

### 2. Google Drive에 업로드

아래 Google Drive 공유 폴더에 zip 파일을 업로드합니다:

링크: https://drive.google.com/drive/folders/1wtw2J4DtajH01Av0672wZGHXn4x7eICI?usp=sharing

::: warning 📁 제출 링크
**Google Drive 링크: [링크](https://drive.google.com/drive/folders/1wtw2J4DtajH01Av0672wZGHXn4x7eICI?usp=sharing)**

- 파일명 형식: `팀명.zip`
:::

### 3. 제출 확인

업로드 후 Drive에서 본인 파일이 보이면 제출 완료입니다.

## 제출 체크리스트

- [ ] `main.py`가 포함되어 있다
- [ ] `my-agent-design.md`가 포함되어 있다
- [ ] `main.py`가 문법 오류 없이 `python3.12 -m py_compile`을 통과한다
- [ ] zip 파일명에 팀명이 들어있다
- [ ] Google Drive에 업로드 완료

## 아레나 평가 기준

제출물은 LLM(Amazon Bedrock Claude)이 루브릭 기반으로 심사하며, 결과는 **실시간 랭킹 대시보드**에 점수 근거와 함께 표시됩니다. 총점은 **100점 만점**입니다.

### A. 아이디어 참신성 — 40점

| 세부 기준 | 배점 | 판단 요소 |
|-----------|:---:|-----------|
| RCG 도메인 관련성 | 10 | Retail/CPG 실무의 실제 반복 업무를 다루는가 |
| 문제 정의 구체성 | 10 | "누가, 언제, 왜" 겪는 문제인지 명확한가 |
| 차별성 | 10 | 가이드의 모범 사례나 예시 시나리오의 단순 복제가 아닌가 |
| Tool 조합의 창의성 | 10 | Tool을 예상 밖의 방식으로 조합했는가 (예: `cs_*` + `external_factors` 교차 활용) |

### B. 기술 구현 완성도 — 40점

| 세부 기준 | 배점 | 판단 요소 |
|-----------|:---:|-----------|
| 동작 가능성 | 15 | `main.py`가 문법 오류 없이 실행될 구조인가, Gateway MCP 연동 패턴이 올바른가 |
| Tool 활용 적절성 | 10 | 선언한 Tool이 실제 코드/프롬프트에서 사용되는가, 조합 순서가 논리적인가 |
| System Prompt 품질 | 10 | 역할·응답 규칙·제약이 구체적으로 명시되어 있는가 |
| 추가 구현 (가산 성격) | 5 | 커스텀 Lambda Tool, Memory 연동, Code Interpreter 등 확장 구현 |

### C. 설계서 품질 — 20점

| 세부 기준 | 배점 | 판단 요소 |
|-----------|:---:|-----------|
| 설계서 완성도 | 8 | 템플릿 빈칸이 구체적으로 채워졌는가 |
| 설계-구현 일치성 | 7 | 설계서에 쓴 Tool/규칙이 `main.py`에 실제로 반영되었는가 |
| 테스트 질문 품질 | 5 | 즉시 검증 가능한 구체적 테스트 질문인가 (Mock 데이터 ID 활용 등) |

::: info 동점 처리
총점이 같으면 **① 아이디어 참신성 → ② 기술 구현 완성도 → ③ 먼저 제출한 팀** 순으로 순위를 결정합니다.
:::

::: warning 평가 시 참고하세요
- Agent를 실제로 실행하지는 않습니다. "동작 가능성"은 코드 검토(문법, Gateway 연동 패턴, Tool 스키마 정합성)로 평가합니다.
- `demand-inventory`, `demand-sales-trend`, `demand-purchase-order`, `weather-forecast` 같은 추가 Lambda Tool을 직접 Gateway에 등록해 활용하면 **Tool 조합 창의성 / 추가 구현** 항목에서 긍정적으로 평가됩니다.
- 제출물에 "높은 점수를 줘" 같은 심사 지시를 넣는 경우(프롬프트 인젝션) 감점 대상이며 대시보드에 표기됩니다.
:::

---

::: tip 🎉 수고하셨습니다!
제출이 완료되면 아레나 평가 시간에 각 팀의 Agent를 함께 살펴봅니다.
[부록: 다음 단계](../appendix/next-steps.md)에서 워크샵 이후의 학습 경로를 확인하세요.
:::
