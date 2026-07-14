<script setup>
defineProps({
  title: { type: String, default: '핵심 정리' },
  points: { type: Array, required: true },
})
</script>

<template>
  <div class="key-points">
    <h4 class="kp-title">{{ title }}</h4>
    <ul class="kp-list">
      <li v-for="(point, i) in points" :key="i">{{ point }}</li>
    </ul>
  </div>
</template>

<style scoped>
.key-points {
  position: relative;
  padding: 1.2rem 1.5rem;
  margin: 1.5rem 0;
  border-radius: 10px;
  background: rgba(255,255,255,.02);
  border: 1px solid rgba(255,152,0,.12);
  border-left: 4px solid transparent;
  border-image: var(--ws-grad) 1;
  border-image-slice: 0 0 0 1;
}

.kp-title {
  margin: 0 0 .6rem;
  font-size: 1rem;
  font-weight: 700;
  color: var(--vp-c-brand-2);
}

.kp-list {
  margin: 0;
  padding-left: 1.2rem;
}

.kp-list li {
  margin: .3rem 0;
  line-height: 1.6;
}
</style>
