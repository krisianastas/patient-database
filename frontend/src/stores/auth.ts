import { defineStore } from 'pinia'
import { ref } from 'vue'

export type AuthUser = {
  id: number
  username: string
}

type SessionPayload = {
  authenticated: boolean
  user: AuthUser | null
}

function getCookie(name: string) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) {
    const last = parts.pop()
    if (!last) {
      return ''
    }
    return last.split(';').shift() ?? ''
  }
  return ''
}

async function request(path: string, options: RequestInit = {}) {
  const response = await fetch(path, {
    credentials: 'same-origin',
    ...options
  })
  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const message = data && data.error ? data.error : 'Request failed.'
    const error = new Error(message) as Error & { payload?: unknown; status?: number }
    error.payload = data as unknown
    error.status = response.status
    throw error
  }

  return data
}

export const useAuthStore = defineStore('auth', () => {
  const initialized = ref(false)
  const loading = ref(false)
  const isAuthenticated = ref(false)
  const user = ref<AuthUser | null>(null)
  const error = ref('')

  const setError = (err: unknown) => {
    if (!err) {
      error.value = ''
      return
    }
    if (err instanceof Error) {
      error.value = err.message
      return
    }
    error.value = String(err)
  }

  const applySession = (payload: SessionPayload) => {
    isAuthenticated.value = payload.authenticated
    user.value = payload.user
  }

  const clearSession = () => {
    isAuthenticated.value = false
    user.value = null
  }

  const fetchSession = async () => {
    loading.value = true
    setError('')

    try {
      const payload = (await request('/api/auth/session/')) as SessionPayload
      applySession(payload)
      return payload
    } catch (err) {
      clearSession()
      setError(err)
      return null
    } finally {
      initialized.value = true
      loading.value = false
    }
  }

  const login = async (username: string, password: string) => {
    loading.value = true
    setError('')

    try {
      const payload = (await request('/api/auth/login/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ username, password })
      })) as SessionPayload
      applySession(payload)
      initialized.value = true
      return true
    } catch (err) {
      clearSession()
      setError(err)
      return false
    } finally {
      loading.value = false
    }
  }

  const logout = async () => {
    loading.value = true
    setError('')

    try {
      await request('/api/auth/logout/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
      })
      clearSession()
      initialized.value = true
      return true
    } catch (err) {
      setError(err)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    initialized,
    loading,
    isAuthenticated,
    user,
    error,
    fetchSession,
    login,
    logout
  }
})
