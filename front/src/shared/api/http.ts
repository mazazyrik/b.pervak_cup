import axios from 'axios'
import { useAuth } from '@entities/user/model/useAuth'
import { toast } from 'sonner'

function resolveBaseUrl() {
  if (import.meta.env.VITE_API_URL) return import.meta.env.VITE_API_URL as string
  const { protocol, hostname } = window.location
  return `${protocol}//${hostname}:8000`
}

const api = axios.create({
  baseURL: resolveBaseUrl(),
  withCredentials: true
})

api.interceptors.request.use((config) => {
  const state = useAuth.getState()
  const token = state.telegramId || null
  if (token) {
    config.headers = config.headers || {}
    ;(config.headers as any)['Authorization'] = `Bearer ${token}`
  }
  return config
})

let isLoggingIn = false

api.interceptors.response.use(
  (r) => r,
  async (error) => {
    const cfg = error.config
    const status = error?.response?.status
    const isNetwork = !error.response
    const retries = (cfg as any)._retries || 0
    if ((isNetwork || status >= 500) && retries < 3) {
      ;(cfg as any)._retries = retries + 1
      await new Promise((res) => setTimeout(res, 300 * Math.pow(2, retries)))
      return api(cfg)
    }
    if (status === 401 && !cfg._retriedAuth) {
      if (!isLoggingIn) {
        isLoggingIn = true
        try {
          const state = useAuth.getState()
            const token = state.telegramId || null
          if (token) await api.post('/auth/login', { telegram_id: token })
        } catch {}
        isLoggingIn = false
      }
      cfg._retriedAuth = true
      return api(cfg)
    }
    if (import.meta.env.DEV) console.warn('api_error', error)
    toast.error('Ошибка запроса')
    return Promise.reject(error)
  }
)

export { api }

