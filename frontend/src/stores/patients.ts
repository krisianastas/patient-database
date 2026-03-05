import { defineStore } from 'pinia'
import { ref } from 'vue'

export type Service = {
  id: number
  name: string
}

export type PatientUser = {
  id: number
  username: string
}

export type ServiceEvent = {
  id: number
  service: Service
  service_date: string
  price: string | null
  created_at: string | null
  created_by: PatientUser | null
}

export type Patient = {
  id: number
  emri: string | null
  nr_cel: string | null
  email: string | null
  mjeku: string | null
  service_events: ServiceEvent[]
  service_summary: Service[]
  created_by: PatientUser | null
  updated_by: PatientUser | null
  data: string | null
}

type PatientPayload = {
  emri: string
  nr_cel: string
  email: string
  mjeku: string
}

type ServiceEventPayload = {
  service_id: number
  service_date: string
  price: string
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
    const message =
      response.status === 401
        ? 'Session expired. Please log in.'
        : data && data.error
          ? data.error
          : 'Request failed.'
    const error = new Error(message) as Error & { payload?: unknown; status?: number }
    error.payload = data as unknown
    error.status = response.status
    throw error
  }

  return data
}

export const usePatientsStore = defineStore('patients', () => {
  const patients = ref<Patient[]>([])
  const currentPatient = ref<Patient | null>(null)
  const services = ref<Service[]>([])
  const loading = ref(false)
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

  const fetchServices = async () => {
    setError('')

    try {
      const data = await request('/api/services/')
      services.value = data.results || []
      return services.value
    } catch (err) {
      setError(err)
      return []
    }
  }

  const fetchPatients = async (filters?: { service_ids?: number[] }) => {
    loading.value = true
    setError('')

    try {
      const params = new URLSearchParams()
      if (filters?.service_ids?.length) {
        params.set('service_ids', filters.service_ids.join(','))
      }
      const query = params.toString()
      const data = await request(`/api/patients/${query ? `?${query}` : ''}`)
      patients.value = data.results || []
    } catch (err) {
      setError(err)
    } finally {
      loading.value = false
    }
  }

  const fetchPatient = async (id: number | string) => {
    loading.value = true
    setError('')

    try {
      currentPatient.value = await request(`/api/patients/${id}/`)
      return currentPatient.value
    } catch (err) {
      setError(err)
      return null
    } finally {
      loading.value = false
    }
  }

  const createPatient = async (payload: PatientPayload) => {
    setError('')

    try {
      const created = await request('/api/patients/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(payload)
      })
      patients.value = [created, ...patients.value]
      return created
    } catch (err) {
      setError(err)
      return null
    }
  }

  const updatePatient = async (id: number | string, payload: PatientPayload) => {
    setError('')

    try {
      const updated = await request(`/api/patients/${id}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(payload)
      })
      patients.value = patients.value.map((item) => (item.id === updated.id ? updated : item))
      if (currentPatient.value && currentPatient.value.id === updated.id) {
        currentPatient.value = updated
      }
      return updated
    } catch (err) {
      setError(err)
      return null
    }
  }

  const deletePatient = async (id: number | string) => {
    setError('')

    try {
      await request(`/api/patients/${id}/`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
      })
      patients.value = patients.value.filter((item) => item.id !== id)
      if (currentPatient.value && currentPatient.value.id === id) {
        currentPatient.value = null
      }
      return true
    } catch (err) {
      setError(err)
      return false
    }
  }

  const addServiceEvent = async (patientId: number | string, payload: ServiceEventPayload) => {
    setError('')

    try {
      const created = await request(`/api/patients/${patientId}/service-events/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(payload)
      })

      const refreshed = await request(`/api/patients/${patientId}/`)
      patients.value = patients.value.map((item) => (String(item.id) === String(patientId) ? refreshed : item))
      if (currentPatient.value && String(currentPatient.value.id) === String(patientId)) {
        currentPatient.value = refreshed
      }
      return created
    } catch (err) {
      setError(err)
      return null
    }
  }

  const deleteServiceEvent = async (patientId: number | string, eventId: number | string) => {
    setError('')

    try {
      await request(`/api/patients/${patientId}/service-events/${eventId}/`, {
        method: 'DELETE',
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        }
      })

      const refreshed = await request(`/api/patients/${patientId}/`)
      patients.value = patients.value.map((item) => (String(item.id) === String(patientId) ? refreshed : item))
      if (currentPatient.value && String(currentPatient.value.id) === String(patientId)) {
        currentPatient.value = refreshed
      }
      return true
    } catch (err) {
      setError(err)
      return false
    }
  }

  return {
    patients,
    currentPatient,
    services,
    loading,
    error,
    fetchServices,
    fetchPatients,
    fetchPatient,
    createPatient,
    updatePatient,
    deletePatient,
    addServiceEvent,
    deleteServiceEvent
  }
})
