<template>
  <button
    type="button"
    class="cursor-pointer inline-flex h-10 w-10 items-center justify-center rounded-full border border-theme bg-theme-elevated text-theme transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--primary-ring)] hover-interactive-ghost"
    :aria-label="label"
    @click="themeStore.toggleTheme"
  >
    <svg
      v-if="themeStore.theme === 'dark'"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.8"
      class="h-5 w-5"
    >
      <path d="M12 4V2m0 20v-2m5.66-13.66 1.41-1.41M4.93 19.07l1.41-1.41M20 12h2M2 12h2m13.66 5.66 1.41 1.41M4.93 4.93l1.41 1.41" />
      <circle cx="12" cy="12" r="4" />
    </svg>
    <svg
      v-else
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      fill="currentColor"
      class="h-5 w-5"
    >
      <path d="M20.354 15.354A9 9 0 0 1 8.646 3.646 9 9 0 1 0 20.354 15.354z" />
    </svg>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import { useThemeStore } from '../stores/theme'

const themeStore = useThemeStore()
const label = computed(() =>
  themeStore.theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
)
</script>
