<template>
  <AppShell>
    <AppHeader title="Patient Dashboard">
    </AppHeader>
    <main class="mx-auto max-w-6xl px-6 py-10">
      <router-view />
    </main>
  </AppShell>
</template>

<script setup lang="ts">
import AppHeader from './components/AppHeader.vue'
import AppShell from './components/AppShell.vue'
</script>
