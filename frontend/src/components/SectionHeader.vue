<template>
  <div class="flex flex-wrap items-center justify-between gap-4">
    <div>
      <p v-if="eyebrow" class="text-xs uppercase tracking-[0.3em] text-slate-500">{{ eyebrow }}</p>
      <h2 class="text-2xl font-semibold text-white">{{ title }}</h2>
      <p v-if="subtitle" class="mt-1 text-sm text-slate-400">{{ subtitle }}</p>
    </div>
    <div class="flex items-center gap-2">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  title: {
    type: String,
    required: true
  },
  eyebrow: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  }
})
</script>
