<template>
  <div class="rounded-2xl border border-white/10 bg-white/5 p-5">
    <p class="text-xs uppercase tracking-[0.2em] text-slate-500">{{ label }}</p>
    <div class="mt-3 flex items-baseline gap-2">
      <p class="text-3xl font-semibold text-white">{{ value }}</p>
      <p v-if="subtitle" class="text-sm text-slate-400">{{ subtitle }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  label: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  }
})
</script>
