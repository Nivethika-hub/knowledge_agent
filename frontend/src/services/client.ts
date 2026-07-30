import axios from 'axios'

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000',
  headers: {
    Accept: 'application/json',
  },
  timeout: 60_000,
})

export function getApiErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail
    if (typeof detail === 'string') return detail
    if (detail && typeof detail === 'object') return JSON.stringify(detail)
    if (error.code === 'ECONNABORTED') return 'The request took too long. Please try again.'
    return 'Unable to reach the backend. Verify that FastAPI is running.'
  }

  return 'Something went wrong. Please try again.'
}
