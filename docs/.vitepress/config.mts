import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

export default withMermaid(defineConfig({
  title: 'Build! Deploy! Observe!',
  description: 'From PoC to Production: Strands Agents + AgentCore Hands-On',
  lang: 'ko-KR',
  lastUpdated: true,
  cleanUrls: true,
  appearance: 'dark',

  mermaid: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Noto Sans KR", sans-serif',
    flowchart: { htmlLabels: true, padding: 12, nodeSpacing: 50, rankSpacing: 60, useMaxWidth: true },
  },

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: '시작하기', link: '/setup' },
      {
        text: 'Phases',
        items: [
          { text: 'Phase 1: 첫 Agent', link: '/phase1/' },
          { text: 'Phase 2: CS Agent', link: '/phase2a/' },
          { text: 'Phase 3: 나만의 Agent', link: '/phase3/' },
        ],
      },
      { text: '부록', link: '/appendix/service-map' },
    ],

    sidebar: [
      {
        text: '시작하기 전에',
        items: [
          { text: '환경 세팅', link: '/setup' },
        ],
      },
      {
        text: 'Phase 1: 첫 Agent, 세상에 내보내기',
        collapsed: false,
        items: [
          { text: '개요', link: '/phase1/' },
          { text: 'Agent에게 도구를 쥐어주자', link: '/phase1/step1-gateway' },
          { text: '똑똑한 두뇌를 달아주자', link: '/phase1/step2-agent' },
          { text: '세상에 공개하기', link: '/phase1/step3-runtime' },
          { text: 'Agent의 생각을 들여다보기', link: '/phase1/step4-observability' },
        ],
      },
      {
        text: 'Phase 2: CS Agent',
        collapsed: true,
        items: [
          { text: '개요', link: '/phase2a/' },
          { text: '고객을 기억하게 만들자', link: '/phase2a/step1-memory' },
          { text: '경쟁사 가격도 조회하게 하자', link: '/phase2a/step2-gateway' },
          { text: '맥락을 이해하는 Agent 완성', link: '/phase2a/step3-agent' },
          { text: '규칙을 지키게 하자', link: '/phase2a/step4-policy' },
        ],
      },
      {
        text: 'Phase 3: 나만의 Agent 만들기',
        collapsed: true,
        items: [
          { text: '개요', link: '/phase3/' },
          { text: '데이터 재료 준비하기', link: '/phase3/step1-gateway' },
          { text: '나만의 Agent 설계하기', link: '/phase3/step2-design' },
          { text: '바이브코딩으로 구현하기', link: '/phase3/step3-vibecoding' },
          { text: 'Runtime 배포 & Playground 테스트', link: '/phase3/step4-deploy' },
          { text: '🏟️ 아레나 제출하기', link: '/phase3/step5-submit' },
        ],
      },
      {
        text: '부록',
        collapsed: true,
        items: [
          { text: 'AgentCore 서비스 한눈에 보기', link: '/appendix/service-map' },
          { text: '우리 회사에서 이어가기', link: '/appendix/next-steps' },
          { text: 'FAQ & 트러블슈팅', link: '/appendix/faq' },
        ],
      },
    ],

    search: { provider: 'local' },
    outline: { label: '이 페이지', level: [2, 3] },
    docFooter: { prev: '이전', next: '다음' },
    darkModeSwitchLabel: '다크 모드',
    sidebarMenuLabel: '메뉴',
    returnToTopLabel: '맨 위로',
    lastUpdated: { text: '마지막 수정' },
    footer: {
      message: 'RCG AI Platform Day #2 · Self-Paced Workshop',
      copyright: 'From PoC to Production: Strands Agents + AgentCore',
    },
  },
}))
