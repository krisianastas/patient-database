<template>
  <AppShell>
    <AppHeader title="Patient Dashboard">
      <template v-if="authStore.isAuthenticated">
        <p class="text-xs uppercase tracking-[0.2em] text-slate-400">
          {{ authStore.user?.username }}
        </p>
        <AppButton variant="ghost" type="button" :disabled="authStore.loading" @click="handleLogout">
          Logout
        </AppButton>
      </template>
      <AppButton v-else variant="ghost" to="/login">Login</AppButton>
    </AppHeader>
    <main class="mx-auto max-w-6xl px-6 py-10">
      <p v-if="!authStore.initialized" class="text-sm text-slate-400">Checking session...</p>
      <router-view v-else />
    </main>
  </AppShell>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

import AppButton from './components/AppButton.vue'
import AppHeader from './components/AppHeader.vue'
import AppShell from './components/AppShell.vue'
import { useAuthStore } from './stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  const success = await authStore.logout()
  if (success) {
    router.push('/login')
  }
}
</script>
