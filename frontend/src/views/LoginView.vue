<template>
  <section class="mx-auto max-w-md space-y-6 fade-in">
    <SectionHeader
      title="Sign in"
      eyebrow="Authentication"
      subtitle="Log in before accessing patient records."
    />

    <AppCard>
      <form class="space-y-5" @submit.prevent="handleLogin">
        <FormField label="Username" for-id="username">
          <input
            id="username"
            v-model="form.username"
            type="text"
            autocomplete="username"
            class="ui-input"
            placeholder="Enter your username"
          />
        </FormField>

        <FormField label="Password" for-id="password">
          <input
            id="password"
            v-model="form.password"
            type="password"
            autocomplete="current-password"
            class="ui-input"
            placeholder="Enter your password"
          />
        </FormField>

        <p v-if="localError" class="text-sm text-theme-error">{{ localError }}</p>
        <p v-else-if="authStore.error" class="text-sm text-theme-error">{{ authStore.error }}</p>

        <AppButton type="submit" :disabled="authStore.loading" class="w-full">
          {{ authStore.loading ? 'Signing in...' : 'Sign in' }}
        </AppButton>
      </form>
    </AppCard>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppButton from '../components/AppButton.vue'
import AppCard from '../components/AppCard.vue'
import FormField from '../components/FormField.vue'
import SectionHeader from '../components/SectionHeader.vue'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const form = reactive({
  username: '',
  password: ''
})
const localError = ref('')

const nextPath = computed(() => {
  const next = route.query.next
  if (typeof next !== 'string' || !next.startsWith('/')) {
    return '/'
  }
  return next
})

const handleLogin = async () => {
  localError.value = ''

  const username = form.username.trim()
  const password = form.password

  if (!username || !password) {
    localError.value = 'Username and password are required.'
    return
  }

  const success = await authStore.login(username, password)
  if (!success) {
    return
  }

  router.push(nextPath.value)
}
</script>
