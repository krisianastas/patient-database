<template>
  <header class="border-b border-white/10">
    <div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-6">
      <div>
        <p class="text-xs uppercase tracking-[0.3em] text-slate-400">Patient database</p>
        <h1 class="text-2xl font-semibold text-white">{{ title }}</h1>
      </div>
      <nav class="flex items-center gap-3 text-sm">
        <slot />
      </nav>
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps({
  title: {
    type: String,
    default: 'Dashboard'
  }
})
</script>
