import axios from 'axios'
import { useAuthStore } from '../stores/auth'

export const api = axios.create({
  baseURL: '',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const auth = useAuthStore()
  if (auth.accessToken) {
    config.headers.Authorization = `Bearer ${auth.accessToken}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const auth = useAuthStore()
      const newToken = await auth.refreshAccessToken()
      if (newToken) {
        error.config.headers.Authorization = `Bearer ${newToken}`
        return api.request(error.config)
      }
    }
    return Promise.reject(error)
  }
)
