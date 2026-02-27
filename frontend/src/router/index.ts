import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '../stores/auth'
import LoginView from '../views/LoginView.vue'
import PatientDetail from '../views/PatientDetail.vue'
import PatientForm from '../views/PatientForm.vue'
import PatientsList from '../views/PatientsList.vue'

const routes = [
  { path: '/login', name: 'login', component: LoginView },
  { path: '/', name: 'patients', component: PatientsList, meta: { requiresAuth: true } },
  { path: '/patients/new', name: 'patient-new', component: PatientForm, meta: { requiresAuth: true } },
  { path: '/patients/:id', name: 'patient-detail', component: PatientDetail, props: true, meta: { requiresAuth: true } },
  { path: '/patients/:id/edit', name: 'patient-edit', component: PatientForm, props: true, meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()

  if (!authStore.initialized) {
    await authStore.fetchSession()
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return {
      path: '/login',
      query: {
        next: to.fullPath
      }
    }
  }

  if (to.path === '/login' && authStore.isAuthenticated) {
    return { path: '/' }
  }

  return true
})

export default router
