import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '../composables/useApi'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const accessToken = ref(localStorage.getItem('access_token'))
  const refreshToken = ref(localStorage.getItem('refresh_token'))

  const isLoggedIn = computed(() => !!accessToken.value)

  async function login(email, password) {
    const res = await api.post('/api/auth/login', { email, password })
    accessToken.value = res.data.access_token
    refreshToken.value = res.data.refresh_token
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    await fetchUser()
    return res.data
  }

  async function register(email, username, password) {
    const res = await api.post('/api/auth/register', { email, username, password })
    accessToken.value = res.data.access_token
    refreshToken.value = res.data.refresh_token
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    await fetchUser()
    return res.data
  }

  async function fetchUser() {
    try {
      const res = await api.get('/api/auth/me')
      user.value = res.data
    } catch {
      logout()
    }
  }

  async function refreshAccessToken() {
    try {
      const res = await api.post('/api/auth/refresh', { refresh_token: refreshToken.value })
      accessToken.value = res.data.access_token
      refreshToken.value = res.data.refresh_token
      localStorage.setItem('access_token', res.data.access_token)
      localStorage.setItem('refresh_token', res.data.refresh_token)
      return res.data.access_token
    } catch {
      logout()
      return null
    }
  }

  function logout() {
    user.value = null
    accessToken.value = null
    refreshToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  if (accessToken.value) {
    fetchUser()
  }

  return { user, accessToken, refreshToken, isLoggedIn, login, register, fetchUser, refreshAccessToken, logout }
})
