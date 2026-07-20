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

---

::: tip 🎉 수고하셨습니다!
제출이 완료되면 아레나 평가 시간에 각 팀의 Agent를 함께 살펴봅니다.
[부록: 다음 단계](../appendix/next-steps.md)에서 워크샵 이후의 학습 경로를 확인하세요.
:::
