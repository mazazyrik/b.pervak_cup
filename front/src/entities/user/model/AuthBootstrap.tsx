import { useEffect } from 'react'
import { initTelegram } from '@app/telegram/initTelegram'
import { useAuth } from './useAuth'
import { api } from '@shared/api/http'

export function AuthBootstrap() {
  const { telegramId } = useAuth()
  useEffect(() => {
    const { telegramId: id } = initTelegram()
    if (!id) return
    const s = useAuth.getState()
    if (s.telegramId !== id) useAuth.setState({ ...s, telegramId: id })
    api.post('/auth/login', { telegram_id: id }).catch(() => {})
  }, [telegramId])
  return null
}
