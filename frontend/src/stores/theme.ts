import { defineStore } from 'pinia'
import { ref } from 'vue'

export type Theme = 'dark' | 'light'

const STORAGE_KEY = 'ui-theme'
const TRANSITION_CLASS = 'theme-transition'

const isTheme = (value: string | null): value is Theme => value === 'dark' || value === 'light'

export const useThemeStore = defineStore('theme', () => {
  const theme = ref<Theme>('dark')
  const initialized = ref(false)

  const applyTheme = (value: Theme) => {
    document.documentElement.classList.add(TRANSITION_CLASS)
    document.documentElement.dataset.theme = value
    window.setTimeout(() => {
      document.documentElement.classList.remove(TRANSITION_CLASS)
    }, 260)
  }

  const setTheme = (value: Theme) => {
    theme.value = value
    localStorage.setItem(STORAGE_KEY, value)
    applyTheme(value)
  }

  const toggleTheme = () => {
    setTheme(theme.value === 'dark' ? 'light' : 'dark')
  }

  const initTheme = () => {
    if (initialized.value) {
      return
    }
    const stored = localStorage.getItem(STORAGE_KEY)
    const value: Theme = isTheme(stored) ? stored : 'dark'
    theme.value = value
    localStorage.setItem(STORAGE_KEY, value)
    applyTheme(value)
    initialized.value = true
  }

  return {
    theme,
    initialized,
    initTheme,
    setTheme,
    toggleTheme,
  }
})
