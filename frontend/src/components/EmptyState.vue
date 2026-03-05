<template>
  <div class="rounded-2xl border border-dashed border-theme bg-theme-surface p-8 text-center">
    <p class="text-lg font-semibold text-theme">{{ title }}</p>
    <p class="mt-2 text-sm text-theme-muted">{{ description }}</p>
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
