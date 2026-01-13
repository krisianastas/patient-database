<template>
  <div class="space-y-2">
    <label v-if="label" :for="forId" class="text-xs uppercase tracking-[0.2em] text-slate-400">
      {{ label }}
    </label>
    <slot />
    <p v-if="hint" class="text-xs text-slate-500">{{ hint }}</p>
    <p v-if="error" class="text-xs text-rose-300">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
defineProps({
  label: {
    type: String,
    default: ''
  },
  forId: {
    type: String,
    default: ''
  },
  hint: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: ''
  }
})
</script>
