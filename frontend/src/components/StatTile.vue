<template>
  <div class="rounded-2xl border border-theme bg-theme-surface p-5">
    <p class="text-xs uppercase tracking-[0.2em] text-theme-subtle">{{ label }}</p>
    <div class="mt-3 flex items-baseline gap-2">
      <p class="text-3xl font-semibold text-theme">{{ value }}</p>
      <p v-if="subtitle" class="text-sm text-theme-muted">{{ subtitle }}</p>
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
