<script setup>
const props = defineProps({
  phase: { type: [String, Number], required: true },
  label: { type: String, default: '' },
})

const colors = {
  '1': { bg: 'rgba(230,81,0,.15)', text: '#ff9800' },
  '2a': { bg: 'rgba(21,101,192,.15)', text: '#64b5f6' },
  '2b': { bg: 'rgba(21,101,192,.15)', text: '#90caf9' },
  '3': { bg: 'rgba(106,27,154,.15)', text: '#ce93d8' },
}

const style = colors[String(props.phase).toLowerCase()] || colors['1']
</script>

<template>
  <span class="phase-badge" :style="{ background: style.bg, color: style.text }">
    Phase {{ phase }}{{ label ? ': ' + label : '' }}
  </span>
</template>

<style scoped>
.phase-badge {
  display: inline-block;
  padding: .2em .7em;
  border-radius: 6px;
  font-size: .85rem;
  font-weight: 600;
  letter-spacing: .02em;
}
</style>
