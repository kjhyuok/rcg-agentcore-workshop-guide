# 워크샵 디자인 설계도 — MkDocs → VitePress "디자인만" 이식

> **목적**: 이미 작성된 워크샵 문서(주로 MkDocs Material `.md`)의 **콘텐츠는 한 글자도 바꾸지 않고**,
> 겉모습(디자인 프레임워크)만 VitePress + 시그니처 그라디언트 테마로 바꾸기 위한 재현 절차서.
> 이 리포(`rcg-agentcore-workshop-guide`)에 실제로 적용한 것을 그대로 정리했으므로,
> 다른 워크샵 리포에서도 **파일을 복붙 → 색만 교체 → 변환 스크립트 실행**하면 동일한 룩이 나온다.

이 문서는 원본 공유 가이드([`SHARE-vitepress-workshop-design-guide.md`](./SHARE-vitepress-workshop-design-guide.md))의
"처음부터 VitePress로 만들기"와 달리, **기존 MkDocs 문서를 이식**하는 시나리오에 특화되어 있다.

---

## 0. 이 설계의 핵심 원칙

1. **콘텐츠 불변**: `.md` 본문 텍스트는 절대 손대지 않는다. 바꾸는 건 (a) MkDocs 전용 마크업 문법과
   (b) 테마(색·레이아웃)뿐이다. 문법 변환은 사람이 손으로 하지 말고 **스크립트로** 한다(정확성·재현성).
2. **그라디언트 하나로 통일**: 브랜드 색 2~3개로 그라디언트 하나(`--ws-grad`)를 만들고, hero·버튼·h2 바·카드·테이블에
   전부 재사용한다. "예쁘다"는 인상의 8할이 여기서 나온다. 화려함보다 일관성.
3. **다크 기본 + 코너 글로우**: 순검정 대신 딥네이비/딥퍼플 배경에 모서리 방사형 빛 2~3개.
4. **한 곳만 고치면 전체가 바뀐다**: 색은 `:root` 변수 몇 개, 레이아웃은 `custom.css` 한 파일.

---

## 1. 산출물 한눈에 (이 4가지가 전부)

```
docs/
├── .vitepress/
│   ├── config.mts              # 설정: nav/sidebar/검색/mermaid/한국어화
│   └── theme/
│       ├── index.ts            # 기본 테마 상속 + 컴포넌트 등록
│       ├── custom.css          # ★ 디자인 전부 여기 (색만 바꾸면 리브랜딩 끝)
│       └── components/         # 반복 패턴용 소형 Vue 컴포넌트 (선택)
│           ├── SceneHeader.vue
│           ├── KeyPoints.vue
│           └── PhaseBadge.vue
├── index.md                    # 홈: frontmatter로 hero+features 얹기 (본문은 보존)
└── (기존 .md 그대로)
scripts/
└── mkdocs2vitepress.py         # ★ MkDocs 문법 → VitePress 문법 자동 변환기
```

기존 `mkdocs.yml`, `requirements.txt`, `docs/assets/`는 **지우지 않고 병행**해도 된다(언제든 롤백 가능).

---

## 2. 적용 절차 (다른 워크샵에 그대로)

### Step 1. 설치

```bash
cd <워크샵-리포>
npm init -y                                   # package.json 없으면
npm add -D vitepress vue vitepress-plugin-mermaid mermaid
```

`package.json`에 scripts 추가:

```json
{
  "scripts": {
    "docs:dev": "vitepress dev docs",
    "docs:build": "vitepress build docs",
    "docs:preview": "vitepress preview docs"
  }
}
```

### Step 2. 콘텐츠 문법 변환 (스크립트)

`scripts/mkdocs2vitepress.py`(→ [부록 A](#부록-a-변환-스크립트-전문))를 리포에 복사한 뒤:

```bash
# 안전: git이 clean한 상태에서 실행하면 언제든 되돌릴 수 있다
python3 scripts/mkdocs2vitepress.py docs
```

변환되는 것 (콘텐츠 텍스트는 그대로, 마크업만):

| MkDocs Material | VitePress | 비고 |
|---|---|---|
| `!!! tip "제목"` + 4칸 들여쓴 본문 | `::: tip 제목` … `:::` | admonition |
| `??? example "제목"` (접이식) | `::: details 제목` … `:::` | collapsible |
| `<figure markdown> ![](x){ width="600" } <figcaption>…` | `<figure><img …></figure>` | width 속성 |
| ` ```mermaid ` 코드펜스 | (그대로 둠) | 플러그인이 렌더 |
| 상대 `.md` 링크 | (그대로 둠) | VitePress가 지원 |

> **타입 매핑 주의**: VitePress 컨테이너는 `tip/info/warning/danger/note/details`만 유효하다.
> MkDocs의 `abstract/success/example/question/quote`는 유효 타입으로 매핑하되,
> 원래 의미를 잃지 않도록 **타이틀 앞에 이모지**(✅ 📌 🧪 ❓ 💬)를 붙여 보존한다. (스크립트가 처리)

**검증** (변환 누락·짝 안 맞음 확인):

```bash
# 남은 MkDocs 문법이 0이어야 함
grep -rn '!!!\|???\|{ width\|figure markdown' docs | wc -l
# ::: 열림/닫힘 개수가 같아야 함
grep -rnE '^::: (tip|info|warning|danger|note|details)' docs | wc -l
grep -rxn ':::' docs | wc -l
```

### Step 3. 설정 파일 (`docs/.vitepress/config.mts`)

→ [부록 B](#부록-b-configmts)를 복사하고, 기존 `mkdocs.yml`의 `nav:` 구조를 VitePress `nav`/`sidebar`로 옮긴다.
mermaid 옵션은 **반드시 포함**한다(안 그러면 노드 텍스트가 잘린다 — 4절 참고).

### Step 4. 테마 (`docs/.vitepress/theme/`)

- `index.ts` → [부록 C](#부록-c-themeindexts) 복사
- `custom.css` → [부록 D](#부록-d-themecustomcss) 복사 후 **§3의 색 변수만 교체**
- `components/*.vue` → [부록 E](#부록-e-컴포넌트) 복사 (선택; 안 써도 됨)

### Step 5. 홈 (`docs/index.md`)

기존 index.md **맨 위에** frontmatter만 얹는다. 본문(기존 h1/표/체크리스트 등)은 그대로 아래 남긴다.
`layout: home`이면 hero+features 카드 아래에 본문 마크다운도 이어서 렌더된다.

```yaml
---
layout: home
hero:
  name: <워크샵 이름>            # --ws-grad 로 그라디언트 텍스트가 적용됨
  text: <부제목 한 줄>
  tagline: <무엇을 경험하는 워크샵인지 한 문장>
  actions:
    - theme: brand
      text: 워크샵 시작하기
      link: /setup
    - theme: alt
      text: 첫 챕터 개요
      link: /phase1/
features:
  - title: <챕터 1 제목>
    details: <설명>
    link: /phase1/               # link 주면 카드 전체가 클릭됨
  # …챕터 수만큼
---

<!-- 여기부터 기존 index.md 본문 그대로 -->
```

### Step 6. 빌드 검증

```bash
npm run docs:build      # 깨진 내부 링크를 에러로 잡아준다 — 배포 전 필수
npm run docs:dev        # 로컬 확인
```

---

## 3. 리브랜딩 = 색 변수 6개만 교체

`custom.css` 최상단 `:root`에서 **이 부분만** 바꾸면 사이트 전체 톤이 바뀐다.
브랜드 색 2~3개를 골라 그라디언트 하나로 만드는 게 전부다.

```css
:root {
  /* (1) 브랜드 단색 3단계 — 링크·버튼·강조색 */
  --vp-c-brand-1: #e65100;   /* 진한 쪽 */
  --vp-c-brand-2: #f57c00;
  --vp-c-brand-3: #ff9800;   /* 밝은 쪽 */

  /* (2) 시그니처 그라디언트 — 사이트 전체가 이 하나를 재사용 */
  --ws-grad: linear-gradient(100deg, #bf360c 0%, #e65100 45%, #ff9800 100%);
  --ws-grad-soft: linear-gradient(135deg,
    rgba(191,54,12,.15), rgba(230,81,0,.13), rgba(255,152,0,.15));
}
```

그리고 다크 배경 글로우(`.dark body`의 `radial-gradient` 색)와 navbar 하단선 색만
같은 팔레트로 맞추면 리브랜딩 끝. **글로우 rgba와 그라디언트 색을 같은 계열로 유지**하는 게 포인트.

> 색 조합 팁: 채도 높은 브랜드색 1개 + 그보다 어두운 1개 + 밝은 1개. 세 개를 한 그라디언트에 순서대로.

---

## 4. 반드시 알아야 할 함정 3가지 (실제로 겪은 것)

이 세 가지는 "설정만으로 될 것 같지만 안 되는" 지점이다. 부록 CSS/config에 이미 반영돼 있으니
**빼먹지 말 것.**

### 함정 ① mermaid 노드/subgraph 텍스트가 박스 밖으로 잘린다

한국어 웹폰트(Noto Sans KR)가 늦게 로드되면 mermaid가 텍스트 높이를 잘못 계산해,
여러 줄 노드의 마지막 줄이나 subgraph 타이틀이 박스 경계에 잘린다.

**해결** (두 곳 다 필요):

- `config.mts`의 `mermaid.fontFamily`를 **시스템 폰트로 고정** + `flowchart.padding` 확보
- `custom.css`에서 `foreignObject { overflow: visible }` + `.nodeLabel { line-height:1.5 }`
  + `.cluster-label { transform: translateY(2px) }`

### 함정 ② 다크모드 navbar 우측 배경이 세로로 "잘려" 보인다

코너 글로우가 navbar 뒤로 비칠 때, navbar 우측 `.content`에만 `backdrop-filter`를 주면
사이드바/콘텐츠 경계에서 blur가 끊겨 세로 띠처럼 보인다.

**해결**: `backdrop-filter`를 `.content`가 아니라 **navbar 전체 폭(`.wrapper`)** 에 주고,
내부 `.content`/`.divider` 배경을 투명화.

### 함정 ③ navbar 하단선 색이 `border-bottom`으로 안 바뀐다

VitePress는 navbar 하단 경계를 `.VPNavBar`의 `border-bottom`이 아니라 **별도 `.divider-line` 요소**
(색은 `--vp-c-gutter`)로 그린다. 그래서 `.VPNavBar { border-bottom }`을 줘도 안 먹힌다.

**해결**: `.dark .VPNavBar .divider-line { background-color: <원하는 색> !important }`.
홈에서는 `.VPNavBar.home .divider-line`을 투명 처리(hero 방해 방지).

---

## 5. 새 콘텐츠가 원격에서 추가되면 (유지보수)

원본 저자가 MkDocs 문법으로 새 `.md`/새 문단(admonition 등)을 푸시하면, 머지 후
**변경된 파일에만 변환 스크립트를 다시 돌린다**. 스크립트는 멱등(이미 `:::`인 건 안 건드림)에
가깝지만, 안전하게 하려면 새로 추가/수정된 파일만 대상으로 실행:

```bash
git merge origin/main            # 또는 pull
python3 scripts/mkdocs2vitepress.py docs   # 새 admonition 등 재변환
npm run docs:build               # 링크·문법 검증
```

> 이 리포는 원본이 MkDocs로 계속 유지될 수 있으므로, `mkdocs.yml`을 지우지 않고 병행한다.
> VitePress는 `docs/.vitepress/`만 추가한 것이라, 이 디렉토리를 지우면 원상복구된다.

---

## 부록 A. 변환 스크립트 전문

`scripts/mkdocs2vitepress.py` — 이 리포에 있는 것을 그대로 복사해 쓴다.
(핵심 로직: admonition은 4칸 들여쓰기 블록을 감지해 dedent 후 `:::`로 감싸고,
figure/width HTML을 순수 `<img>`로, 접이식 `???`를 `::: details`로 바꾼다.)

> 실물은 리포의 [`scripts/mkdocs2vitepress.py`](./scripts/mkdocs2vitepress.py) 참조.
> 타입 매핑표(`TYPE_MAP`)의 이모지만 브랜드 톤에 맞게 조정 가능.

## 부록 B. `config.mts`

핵심만 발췌 (전문은 리포의 [`docs/.vitepress/config.mts`](./docs/.vitepress/config.mts)):

```ts
import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
  title: '<워크샵 제목>',
  lang: 'ko-KR',
  lastUpdated: true,
  cleanUrls: true,
  appearance: 'dark',                 // 다크 기본, 토글은 유지됨

  // ★ 함정① 방지: mermaid 텍스트 잘림
  mermaid: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", sans-serif',
    flowchart: { htmlLabels: true, padding: 12, nodeSpacing: 50, rankSpacing: 60, useMaxWidth: true },
  },

  themeConfig: {
    nav: [ /* mkdocs.yml 상단 메뉴 이식 */ ],
    sidebar: [ /* mkdocs.yml nav 트리 이식, collapsed 로 그룹 접기 */ ],
    search: { provider: 'local' },
    outline: { label: '이 페이지', level: [2, 3] },
    docFooter: { prev: '이전', next: '다음' },
    // 한국어화
    darkModeSwitchLabel: '다크 모드', sidebarMenuLabel: '메뉴',
    returnToTopLabel: '맨 위로', lastUpdated: { text: '마지막 수정' },
    footer: { message: '<워크샵 이름> · Self-Paced', copyright: '<부제>' },
  },
}))
```

## 부록 C. `theme/index.ts`

```ts
import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import './custom.css'
import SceneHeader from './components/SceneHeader.vue'
import KeyPoints from './components/KeyPoints.vue'
import PhaseBadge from './components/PhaseBadge.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('SceneHeader', SceneHeader)
    app.component('KeyPoints', KeyPoints)
    app.component('PhaseBadge', PhaseBadge)
  },
} satisfies Theme
```

## 부록 D. `theme/custom.css`

전문은 리포의 [`docs/.vitepress/theme/custom.css`](./docs/.vitepress/theme/custom.css)에 있다.
구조(주석 섹션)는 다음과 같으며, **`:root`의 색 변수만 교체**하면 리브랜딩된다:

| 섹션 | 역할 | 리브랜딩 시 손대는가 |
|---|---|---|
| `:root` 브랜드색·`--ws-grad` | 시그니처 그라디언트 정의 | **예 (여기만)** |
| `.dark body` 코너 글로우 | 다크 배경 방사형 빛 | 색 rgba만 팔레트 맞춤 |
| navbar (`.wrapper`/`.divider-line`) | 함정②③ 해결 | 하단선 색만 |
| `.VPButton.brand` | 버튼 그라디언트 + 호버 플로우 | 아니오 |
| `.VPFeature` | 카드 반투명 + 호버 리프트 | 아니오 |
| `.vp-doc h2::before` | h2 좌측 그라디언트 액센트 바 | 아니오 |
| `.vp-doc h1` border-image | h1 그라디언트 언더라인 | 아니오 |
| `word-break: keep-all` | 한국어 어절 줄바꿈 | 아니오 |
| `.mermaid foreignObject` 등 | 함정① 해결 | 아니오 |
| `@media prefers-reduced-motion` | 접근성 (모션 최소화) | 아니오 |

## 부록 E. 컴포넌트 (선택)

워크샵은 같은 구조(씬 도입부, 핵심 정리, 단계 배지)가 반복된다. props만 받는 10줄짜리
Vue 컴포넌트로 만들어 전역 등록하면 어느 `.md`에서든 import 없이 쓸 수 있고, 룩이 균일해진다.

- `SceneHeader.vue` — 씬 도입 배너 (그라디언트 소프트 배경 + 우상단 빛번짐)
- `KeyPoints.vue` — 핵심 정리 박스 (왼쪽 그라디언트 바)
- `PhaseBadge.vue` — 단계 배지 (Phase별 색)

전문은 리포의 [`docs/.vitepress/theme/components/`](./docs/.vitepress/theme/components/) 참조.
**기존 콘텐츠를 바꾸지 않는 게 원칙이므로, 이 컴포넌트들은 "새로 쓸 때 선택적으로" 쓴다.**
등록만 해두고 안 써도 무방하다.

---

## 체크리스트 (다른 워크샵 적용 시)

- [ ] `npm add -D vitepress vue vitepress-plugin-mermaid mermaid` + scripts 추가
- [ ] `scripts/mkdocs2vitepress.py` 복사 후 `docs`에 실행 → grep으로 변환 검증
- [ ] `config.mts` 복사 후 `mkdocs.yml`의 nav/sidebar 이식 (mermaid 옵션 포함)
- [ ] `theme/index.ts` + `custom.css` 복사
- [ ] **`custom.css :root`의 색 변수 6개를 새 브랜드로 교체**
- [ ] 코너 글로우 rgba + navbar 하단선 색을 같은 팔레트로 맞춤
- [ ] `index.md` 상단에 `layout: home` frontmatter 얹기 (본문 보존)
- [ ] `npm run docs:build` 로 깨진 링크·문법 검증 → `docs:dev` 로 육안 확인
- [ ] (함정 재확인) mermaid 텍스트 안 잘림 / navbar 배경 안 잘림 / 하단선 색 적용됨

이 순서대로면 **콘텐츠는 그대로, 디자인만** 바뀐 VitePress 워크샵 사이트가 나온다.
