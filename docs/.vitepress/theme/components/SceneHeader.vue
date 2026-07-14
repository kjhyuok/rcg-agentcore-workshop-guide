<script setup>
defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' },
})
</script>

<template>
  <div class="scene-header">
    <h3 class="scene-title">{{ title }}</h3>
    <p v-if="description" class="scene-desc">{{ description }}</p>
  </div>
</template>

<style scoped>
.scene-header {
  position: relative;
  padding: 1.5rem 2rem;
  margin: 1.5rem 0;
  border-radius: 12px;
  background: var(--ws-grad-soft);
  overflow: hidden;
}

.scene-header::after {
  content: '';
  position: absolute;
  top: -30%;
  right: -10%;
  width: 200px;
  height: 200px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(255,152,0,.12) 0%, transparent 70%);
  pointer-events: none;
}

.scene-title {
  margin: 0;
  font-size: 1.2rem;
  font-weight: 700;
  background: var(--ws-grad);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.scene-desc {
  margin: .5rem 0 0;
  font-size: .95rem;
  opacity: .85;
}
</style>
