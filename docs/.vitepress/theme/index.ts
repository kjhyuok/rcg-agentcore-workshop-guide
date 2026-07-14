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
