<template>
  <section class="space-y-6 fade-in">
    <SectionHeader
      :title="isEdit ? 'Edit patient' : 'New patient'"
      eyebrow="Record"
      subtitle="Capture contact details, assigned doctor, and services."
    >
      <AppButton variant="ghost" to="/">Cancel</AppButton>
    </SectionHeader>

    <AppCard v-if="loading">
      <p class="text-sm text-slate-400">Loading patient record...</p>
    </AppCard>
    <AppCard v-else-if="patientsStore.error">
      <p class="text-sm text-rose-300">{{ patientsStore.error }}</p>
    </AppCard>

    <AppCard v-else>
      <form class="grid gap-6 md:grid-cols-2" @submit.prevent="handleSubmit">
        <FormField label="Name" for-id="emri" :error="errors.emri">
          <input
            id="emri"
            v-model="form.emri"
            type="text"
            class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-indigo-400/60 focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
            placeholder="Patient name"
          />
        </FormField>
        <FormField label="Phone" for-id="nr_cel" :error="errors.nr_cel">
          <input
            id="nr_cel"
            v-model="form.nr_cel"
            type="text"
            class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-indigo-400/60 focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
            placeholder="+355..."
          />
        </FormField>
        <FormField label="Email" for-id="email" :error="errors.email">
          <input
            id="email"
            v-model="form.email"
            type="email"
            class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-indigo-400/60 focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
            placeholder="name@email.com"
          />
        </FormField>
        <FormField label="Doctor" for-id="mjeku" :error="errors.mjeku">
          <input
            id="mjeku"
            v-model="form.mjeku"
            type="text"
            class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-indigo-400/60 focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
            placeholder="Assigned doctor"
          />
        </FormField>
        <FormField label="Price" for-id="cmimi" :error="errors.cmimi">
          <input
            id="cmimi"
            v-model="form.cmimi"
            type="text"
            class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-indigo-400/60 focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
            placeholder="100 EUR"
          />
        </FormField>
        <FormField label="Services" for-id="sherbimet" class="md:col-span-2" :error="errors.sherbimet">
          <textarea
            id="sherbimet"
            v-model="form.sherbimet"
            rows="4"
            class="w-full rounded-2xl border border-white/10 bg-slate-950/80 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-indigo-400/60 focus:outline-none focus:ring-2 focus:ring-indigo-400/30"
            placeholder="Notes on treatments or services"
          ></textarea>
        </FormField>

        <div class="flex flex-wrap gap-3 md:col-span-2">
          <AppButton type="submit" :disabled="submitting">
            {{ isEdit ? 'Save changes' : 'Create patient' }}
          </AppButton>
          <AppButton variant="ghost" type="button" @click="router.push('/')">Back</AppButton>
        </div>
      </form>
    </AppCard>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppButton from '../components/AppButton.vue'
import AppCard from '../components/AppCard.vue'
import FormField from '../components/FormField.vue'
import SectionHeader from '../components/SectionHeader.vue'
import { usePatientsStore } from '../stores/patients'

const route = useRoute()
const router = useRouter()
const patientsStore = usePatientsStore()

const routeId = computed(() => {
  const param = route.params.id
  return Array.isArray(param) ? param[0] : param
})

const loading = ref(false)
const submitting = ref(false)
const errors = ref<Record<string, string>>({})

const form = reactive({
  emri: '',
  nr_cel: '',
  email: '',
  mjeku: '',
  cmimi: '',
  sherbimet: ''
})

const isEdit = computed(() => Boolean(routeId.value))

const loadPatient = async () => {
  if (!isEdit.value) {
    return
  }

  loading.value = true

  try {
    if (!routeId.value) {
      loading.value = false
      return
    }
    const patient = await patientsStore.fetchPatient(routeId.value)
    if (!patient) {
      return
    }
    form.emri = patient.emri || ''
    form.nr_cel = patient.nr_cel || ''
    form.email = patient.email || ''
    form.mjeku = patient.mjeku || ''
    form.cmimi = patient.cmimi || ''
    form.sherbimet = patient.sherbimet || ''
  } finally {
    loading.value = false
  }
}

const validate = () => {
  const nextErrors: Record<string, string> = {}

  if (!form.emri.trim()) {
    nextErrors.emri = 'Name is required.'
  }

  if (form.cmimi && form.cmimi.length > 50) {
    nextErrors.cmimi = 'Price is too long.'
  }

  errors.value = nextErrors
  return Object.keys(nextErrors).length === 0
}

const handleSubmit = async () => {
  errors.value = {}
  if (!validate()) {
    return
  }

  submitting.value = true

  try {
    if (isEdit.value) {
      if (!routeId.value) {
        return
      }
      const updated = await patientsStore.updatePatient(routeId.value, { ...form })
      if (!updated) {
        return
      }
      router.push(`/patients/${routeId.value}`)
      return
    }

    const created = await patientsStore.createPatient({ ...form })
    if (!created) {
      return
    }
    router.push(`/patients/${created.id}`)
  } finally {
    submitting.value = false
  }
}

onMounted(loadPatient)
</script>
