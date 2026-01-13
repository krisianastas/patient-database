import { defineStore } from 'pinia'
import { ref } from 'vue'

export type Patient = {
  id: number
  emri: string | null
  nr_cel: string | null
  email: string | null
  mjeku: string | null
  cmimi: string | null
  sherbimet: string | null
  data: string | null
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
  const response = await fetch(path, options)
  const data = await response.json().catch(() => null)

  if (!response.ok) {
    const message = data && data.error ? data.error : 'Request failed.'
    const error = new Error(message) as Error & { payload?: unknown }
    error.payload = data as unknown
    throw error
  }

  return data
}

export const usePatientsStore = defineStore('patients', () => {
  const patients = ref<Patient[]>([])
  const currentPatient = ref<Patient | null>(null)
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

  const fetchPatients = async () => {
    loading.value = true
    setError('')

    try {
      const data = await request('/api/patients/')
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

  const createPatient = async (payload: Partial<Patient>) => {
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

  const updatePatient = async (id: number | string, payload: Partial<Patient>) => {
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

  return {
    patients,
    currentPatient,
    loading,
    error,
    fetchPatients,
    fetchPatient,
    createPatient,
    updatePatient,
    deletePatient
  }
})
