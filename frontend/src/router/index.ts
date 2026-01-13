import { createRouter, createWebHistory } from 'vue-router'

import PatientDetail from '../views/PatientDetail.vue'
import PatientForm from '../views/PatientForm.vue'
import PatientsList from '../views/PatientsList.vue'

const routes = [
  { path: '/', name: 'patients', component: PatientsList },
  { path: '/patients/new', name: 'patient-new', component: PatientForm },
  { path: '/patients/:id', name: 'patient-detail', component: PatientDetail, props: true },
  { path: '/patients/:id/edit', name: 'patient-edit', component: PatientForm, props: true }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
