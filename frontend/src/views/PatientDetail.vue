<template>
  <section class="space-y-6 fade-in">
    <SectionHeader title="Patient profile" eyebrow="Details">
      <AppButton variant="ghost" to="/">Back to list</AppButton>
      <AppButton v-if="patient" :to="`/patients/${patient.id}/edit`">Edit</AppButton>
    </SectionHeader>

    <AppCard v-if="patientsStore.loading">
      <p class="text-sm text-slate-400">Loading patient profile...</p>
    </AppCard>
    <AppCard v-else-if="patientsStore.error">
      <p class="text-sm text-rose-300">{{ patientsStore.error }}</p>
    </AppCard>

    <AppCard v-else-if="patient">
      <div class="grid gap-6 md:grid-cols-2">
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Name</p>
          <p class="mt-2 text-xl font-semibold text-white">{{ patient.emri }}</p>
        </div>
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Assigned doctor</p>
          <p class="mt-2 text-lg text-white">{{ patient.mjeku || 'Not assigned' }}</p>
        </div>
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Phone</p>
          <p class="mt-2 text-white">{{ patient.nr_cel || 'Not provided' }}</p>
        </div>
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Email</p>
          <p class="mt-2 text-white">{{ patient.email || 'Not provided' }}</p>
        </div>
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Price</p>
          <p class="mt-2 text-white">{{ patient.cmimi || 'Not set' }}</p>
        </div>
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Created</p>
          <p class="mt-2 text-white">{{ formattedDate || 'Unknown' }}</p>
        </div>
        <div class="md:col-span-2">
          <p class="text-xs uppercase tracking-[0.2em] text-slate-500">Services</p>
          <p class="mt-2 text-white">{{ patient.sherbimet || 'No services listed.' }}</p>
        </div>
      </div>
    </AppCard>
    <AppCard v-else>
      <p class="text-sm text-slate-400">Patient not found.</p>
    </AppCard>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import AppButton from '../components/AppButton.vue'
import AppCard from '../components/AppCard.vue'
import SectionHeader from '../components/SectionHeader.vue'
import { usePatientsStore } from '../stores/patients'
import type { Patient } from '../stores/patients'

const route = useRoute()
const patientsStore = usePatientsStore()
const patient = ref<Patient | null>(null)

const routeId = computed(() => {
  const param = route.params.id
  return Array.isArray(param) ? param[0] : param
})

const formattedDate = computed(() => {
  if (!patient.value || !patient.value.data) {
    return ''
  }
  return new Date(patient.value.data).toLocaleString()
})

const loadPatient = async () => {
  if (!routeId.value) {
    patient.value = null
    return
  }
  patient.value = await patientsStore.fetchPatient(routeId.value)
}

onMounted(loadPatient)
</script>
