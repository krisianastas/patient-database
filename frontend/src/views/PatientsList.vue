<template>
  <section class="space-y-6 fade-in">
    <SectionHeader
      title="All patients"
      eyebrow="Records"
      subtitle="Manage contact details, assigned doctor, and services."
    >
      <AppButton to="/patients/new">New patient</AppButton>
    </SectionHeader>

    <div class="flex flex-wrap items-center justify-between gap-4">
      <div class="w-full md:max-w-sm">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by name, doctor, email, or phone"
          class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-indigo-400/60 focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
        />
      </div>
      <p class="text-xs uppercase tracking-[0.2em] text-slate-500">
        Showing {{ paginatedRows.length }} of {{ filteredRows.length }}
      </p>
    </div>

    <div class="grid gap-4 md:grid-cols-3">
      <StatTile label="Total patients" :value="patientsStore.patients.length" subtitle="Active records" />
      <StatTile label="With doctor" :value="patientsWithDoctor" subtitle="Assigned today" />
      <StatTile label="With email" :value="patientsWithEmail" subtitle="Reachable" />
    </div>

    <AppCard v-if="patientsStore.loading">
      <p class="text-sm text-slate-400">Loading patients...</p>
    </AppCard>
    <AppCard v-else-if="patientsStore.error">
      <p class="text-sm text-rose-300">{{ patientsStore.error }}</p>
    </AppCard>

    <EmptyState
      v-else-if="patientsStore.patients.length === 0"
      title="No patients yet"
      description="Start by adding your first patient record."
    >
      <AppButton to="/patients/new">Add the first patient</AppButton>
    </EmptyState>

    <DataTable v-else :columns="columns" :rows="paginatedRows">
      <template #cell-name="{ row }">
        <div>
          <p class="font-semibold text-white">{{ row.name }}</p>
        </div>
      </template>
      <template #cell-actions="{ row }">
        <div class="flex flex-wrap items-center gap-2">
          <AppButton variant="ghost" :to="`/patients/${row.id}`">View</AppButton>
          <AppButton variant="danger" type="button" @click="confirmDelete(row)">Delete</AppButton>
        </div>
      </template>
    </DataTable>

    <div v-if="totalPages > 1" class="flex flex-wrap items-center justify-between gap-4">
      <p class="text-xs uppercase tracking-[0.2em] text-slate-500">
        Page {{ currentPage }} of {{ totalPages }}
      </p>
      <div class="flex items-center gap-2">
        <AppButton variant="ghost" type="button" :disabled="currentPage === 1" @click="goToPage(1)">
          First
        </AppButton>
        <AppButton variant="ghost" type="button" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
          Previous
        </AppButton>
        <AppButton
          v-for="page in pageNumbers"
          :key="page"
          :variant="page === currentPage ? 'primary' : 'ghost'"
          type="button"
          @click="goToPage(page)"
        >
          {{ page }}
        </AppButton>
        <AppButton variant="ghost" type="button" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">
          Next
        </AppButton>
        <AppButton variant="ghost" type="button" :disabled="currentPage === totalPages" @click="goToPage(totalPages)">
          Last
        </AppButton>
      </div>
    </div>

    <ModalConfirm
      :open="showConfirm"
      title="Delete patient"
      :message="confirmMessage"
      @cancel="closeConfirm"
      @confirm="handleDelete"
    />
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'

import AppButton from '../components/AppButton.vue'
import AppCard from '../components/AppCard.vue'
import DataTable from '../components/DataTable.vue'
import EmptyState from '../components/EmptyState.vue'
import ModalConfirm from '../components/ModalConfirm.vue'
import SectionHeader from '../components/SectionHeader.vue'
import StatTile from '../components/StatTile.vue'
import { usePatientsStore } from '../stores/patients'

const patientsStore = usePatientsStore()
const searchQuery = ref('')
const showConfirm = ref(false)
const patientToDelete = ref<PatientRow | null>(null)
const currentPage = ref(1)
const pageSize = 10

const loadPatients = async () => {
  await patientsStore.fetchPatients()
}

const confirmDelete = (patient: PatientRow) => {
  patientToDelete.value = patient
  showConfirm.value = true
}

const closeConfirm = () => {
  showConfirm.value = false
  patientToDelete.value = null
}

const handleDelete = async () => {
  const patient = patientToDelete.value
  if (!patient) {
    closeConfirm()
    return
  }

  await patientsStore.deletePatient(patient.id)
  closeConfirm()
}

type PatientRow = {
  id: number
  name: string
  doctor: string
  phone: string
  email: string
  actions?: string
}

type Column = {
  key: keyof PatientRow | 'actions'
  label: string
}

const columns: Column[] = [
  { key: 'name', label: 'Patient' },
  { key: 'doctor', label: 'Doctor' },
  { key: 'phone', label: 'Phone' },
  { key: 'actions', label: 'Actions' }
]

const rows = computed<PatientRow[]>(() =>
  patientsStore.patients.map((patient) => ({
    id: patient.id,
    name: patient.emri || 'Unnamed patient',
    doctor: patient.mjeku || 'Not assigned',
    phone: patient.nr_cel || 'Not provided',
    email: patient.email || ''
  }))
)

const filteredRows = computed(() => {
  const query = searchQuery.value.trim().toLowerCase()
  if (!query) {
    return rows.value
  }

  return rows.value.filter((row) => {
    return [row.name, row.doctor, row.phone, row.email]
      .join(' ')
      .toLowerCase()
      .includes(query)
  })
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredRows.value.length / pageSize)))

const paginatedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return filteredRows.value.slice(start, start + pageSize)
})

const pageNumbers = computed(() => Array.from({ length: totalPages.value }, (_, index) => index + 1))

const goToPage = (page: number) => {
  const safePage = Math.min(Math.max(1, page), totalPages.value)
  currentPage.value = safePage
}

watch([filteredRows, totalPages], () => {
  if (currentPage.value > totalPages.value) {
    currentPage.value = 1
  }
})

const patientsWithDoctor = computed(
  () => patientsStore.patients.filter((patient) => patient.mjeku && patient.mjeku.trim()).length
)
const patientsWithEmail = computed(
  () => patientsStore.patients.filter((patient) => patient.email && patient.email.trim()).length
)

const confirmMessage = computed(() => {
  if (!patientToDelete.value) {
    return 'This action cannot be undone.'
  }
  return `Delete ${patientToDelete.value.name || 'this patient'}? This action cannot be undone.`
})

onMounted(loadPatients)
</script>
