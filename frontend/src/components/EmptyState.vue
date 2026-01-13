<template>
  <div class="rounded-2xl border border-dashed border-white/15 bg-white/5 p-8 text-center">
    <p class="text-lg font-semibold text-white">{{ title }}</p>
    <p class="mt-2 text-sm text-slate-400">{{ description }}</p>
    <div class="mt-4 flex justify-center">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  title: {
    type: String,
    default: 'No data yet'
  },
  description: {
    type: String,
    default: ''
  }
})
</script>
