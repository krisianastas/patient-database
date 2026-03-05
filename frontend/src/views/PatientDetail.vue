<template>
  <section class="space-y-6 fade-in">
    <SectionHeader title="Patient profile" eyebrow="Details">
      <AppButton variant="ghost" to="/">Back to list</AppButton>
      <AppButton v-if="patient" :to="`/patients/${patient.id}/edit`">Edit Patient</AppButton>
    </SectionHeader>

    <AppCard v-if="patientsStore.loading">
      <p class="text-sm text-theme-muted">Loading patient profile...</p>
    </AppCard>
    <AppCard v-else-if="patientsStore.error">
      <p class="text-sm text-theme-error">{{ patientsStore.error }}</p>
    </AppCard>

    <AppCard v-else-if="patient">
      <div class="grid gap-6 md:grid-cols-2">
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-theme-subtle">Name</p>
          <p class="mt-2 text-xl font-semibold text-theme">{{ patient.emri }}</p>
        </div>
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-theme-subtle">Assigned doctor</p>
          <p class="mt-2 text-lg text-theme">{{ patient.mjeku || 'Not assigned' }}</p>
        </div>
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-theme-subtle">Phone</p>
          <p class="mt-2 text-theme">{{ patient.nr_cel || 'Not provided' }}</p>
        </div>
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-theme-subtle">Email</p>
          <p class="mt-2 text-theme">{{ patient.email || 'Not provided' }}</p>
        </div>
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-theme-subtle">Created</p>
          <p class="mt-2 text-theme">{{ formattedDate || 'Unknown' }} by {{ patient.created_by?.username || 'Unknown' }}</p>
        </div>
        <div>
          <p class="text-xs uppercase tracking-[0.2em] text-theme-subtle">Last updated by</p>
          <p class="mt-2 text-theme">{{ patient.updated_by?.username || 'Unknown' }}</p>
        </div>
        <div class="md:col-span-2">
          <p class="text-xs uppercase tracking-[0.2em] text-theme-subtle">Service history</p>
          <div class="mt-3 space-y-4 rounded-2xl border border-theme bg-theme-soft p-4">
            <form class="grid gap-3 sm:grid-cols-2 lg:grid-cols-[1fr_180px_140px_auto]" @submit.prevent="handleAddServiceEvent">
              <select
                v-model="serviceEventForm.service_id"
                class="w-full rounded-xl border border-theme bg-theme-elevated px-3 py-2 text-sm text-theme focus:border-theme-strong focus:outline-none focus:ring-2 focus:ring-[var(--primary-ring)]"
              >
                <option value="" disabled>Select service</option>
                <option v-for="service in patientsStore.services" :key="service.id" :value="String(service.id)">
                  {{ service.name }}
                </option>
              </select>
              <input
                v-model="serviceEventForm.service_date"
                type="date"
                :max="today"
                class="w-full rounded-xl border border-theme bg-theme-elevated px-3 py-2 text-sm text-theme focus:border-theme-strong focus:outline-none focus:ring-2 focus:ring-[var(--primary-ring)]"
              />
              <input
                v-model="serviceEventForm.price"
                type="text"
                placeholder="Price (optional)"
                class="w-full rounded-xl border border-theme bg-theme-elevated px-3 py-2 text-sm text-theme placeholder:text-theme-muted focus:border-theme-strong focus:outline-none focus:ring-2 focus:ring-[var(--primary-ring)]"
              />
              <AppButton type="submit" :disabled="addingServiceEvent" class="w-full sm:col-span-2 lg:col-span-1">
                Add service date
              </AppButton>
            </form>
            <p v-if="serviceEventError" class="text-sm text-theme-error">{{ serviceEventError }}</p>

            <div v-if="patient.service_events.length" class="space-y-3 md:hidden">
              <div
                v-for="event in patient.service_events"
                :key="event.id"
                class="rounded-xl border border-theme bg-theme-elevated p-3"
              >
                <p class="text-sm font-semibold text-theme">{{ event.service.name }}</p>
                <p class="mt-1 text-xs text-theme-muted">
                  {{ formatServiceDate(event.service_date) }} • {{ event.price || 'No price' }}
                </p>
                <p class="mt-2 text-xs text-theme-muted">
                  Added by {{ event.created_by?.username || 'Unknown' }} at {{ formatCreatedAt(event.created_at) }}
                </p>
                <div class="mt-3">
                  <AppButton
                    type="button"
                    variant="ghost"
                    :disabled="deletingEventId === event.id"
                    class="w-full"
                    @click="requestDeleteServiceEvent(event.id, event.service.name)"
                  >
                    Delete
                  </AppButton>
                </div>
              </div>
            </div>

            <div v-if="patient.service_events.length" class="hidden overflow-x-auto md:block">
              <table class="min-w-full text-left text-sm text-theme">
                <thead class="text-xs uppercase tracking-[0.15em] text-theme-muted">
                  <tr>
                    <th class="py-2 pr-4">Service</th>
                    <th class="py-2 pr-4">Date</th>
                    <th class="py-2 pr-4">Price</th>
                    <th class="py-2 pr-4">Added by</th>
                    <th class="py-2 pr-4">Added at</th>
                    <th class="py-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="event in patient.service_events" :key="event.id" class="border-t border-theme">
                    <td class="py-3 pr-4">{{ event.service.name }}</td>
                    <td class="py-3 pr-4">{{ formatServiceDate(event.service_date) }}</td>
                    <td class="py-3 pr-4">{{ event.price || 'Not set' }}</td>
                    <td class="py-3 pr-4">{{ event.created_by?.username || 'Unknown' }}</td>
                    <td class="py-3 pr-4">{{ formatCreatedAt(event.created_at) }}</td>
                    <td class="py-3">
                      <AppButton
                        type="button"
                        variant="ghost"
                        :disabled="deletingEventId === event.id"
                        @click="requestDeleteServiceEvent(event.id, event.service.name)"
                      >
                        Delete
                      </AppButton>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p v-else class="text-sm text-theme-muted">No service events logged yet.</p>
          </div>
        </div>
      </div>
    </AppCard>
    <AppCard v-else>
      <p class="text-sm text-theme-muted">Patient not found.</p>
    </AppCard>

    <ModalConfirm
      :open="showDeleteConfirm"
      title="Delete service entry"
      :message="deleteConfirmMessage"
      @cancel="closeDeleteConfirm"
      @confirm="handleDeleteServiceEvent"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute } from 'vue-router'

import AppButton from '../components/AppButton.vue'
import AppCard from '../components/AppCard.vue'
import ModalConfirm from '../components/ModalConfirm.vue'
import SectionHeader from '../components/SectionHeader.vue'
import { usePatientsStore } from '../stores/patients'
import type { Patient } from '../stores/patients'

const route = useRoute()
const patientsStore = usePatientsStore()
const patient = ref<Patient | null>(null)
const addingServiceEvent = ref(false)
const deletingEventId = ref<number | null>(null)
const showDeleteConfirm = ref(false)
const pendingDeleteEvent = ref<{ id: number; serviceName: string } | null>(null)
const serviceEventError = ref('')
const today = new Date().toISOString().slice(0, 10)
const serviceEventForm = reactive({
  service_id: '',
  service_date: today,
  price: ''
})

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
  await patientsStore.fetchServices()
  patient.value = await patientsStore.fetchPatient(routeId.value)
}

const formatServiceDate = (value: string) => {
  if (!value) {
    return ''
  }
  return new Date(`${value}T00:00:00`).toLocaleDateString()
}

const formatCreatedAt = (value: string | null) => {
  if (!value) {
    return 'Unknown'
  }
  return new Date(value).toLocaleString()
}

const requestDeleteServiceEvent = (eventId: number, serviceName: string) => {
  pendingDeleteEvent.value = {
    id: eventId,
    serviceName
  }
  showDeleteConfirm.value = true
}

const closeDeleteConfirm = () => {
  showDeleteConfirm.value = false
  pendingDeleteEvent.value = null
}

const handleAddServiceEvent = async () => {
  serviceEventError.value = ''
  if (!patient.value) {
    return
  }
  if (!serviceEventForm.service_id) {
    serviceEventError.value = 'Please select a service.'
    return
  }
  if (!serviceEventForm.service_date) {
    serviceEventError.value = 'Please choose a date.'
    return
  }

  addingServiceEvent.value = true
  try {
    const created = await patientsStore.addServiceEvent(patient.value.id, {
      service_id: Number(serviceEventForm.service_id),
      service_date: serviceEventForm.service_date,
      price: serviceEventForm.price
    })
    if (!created) {
      serviceEventError.value = patientsStore.error || 'Unable to add service date.'
      return
    }
    patient.value = patientsStore.currentPatient
    serviceEventForm.service_id = ''
    serviceEventForm.service_date = today
    serviceEventForm.price = ''
  } finally {
    addingServiceEvent.value = false
  }
}

const handleDeleteServiceEvent = async () => {
  const pending = pendingDeleteEvent.value
  if (!pending) {
    closeDeleteConfirm()
    return
  }

  serviceEventError.value = ''
  if (!patient.value) {
    closeDeleteConfirm()
    return
  }

  deletingEventId.value = pending.id
  try {
    const ok = await patientsStore.deleteServiceEvent(patient.value.id, pending.id)
    if (!ok) {
      serviceEventError.value = patientsStore.error || 'Unable to delete service event.'
      return
    }
    patient.value = patientsStore.currentPatient
    closeDeleteConfirm()
  } finally {
    deletingEventId.value = null
  }
}

const deleteConfirmMessage = computed(() => {
  if (!pendingDeleteEvent.value) {
    return 'This action cannot be undone.'
  }
  return `Delete ${pendingDeleteEvent.value.serviceName} service entry? This action cannot be undone.`
})

onMounted(loadPatient)
</script>
