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
    const ensure = async () => {
      await api.post('/auth/login', { telegram_id: id }).catch(() => {})
      try {
        const users = await api.get('/users')
        const found = Array.isArray(users.data) ? users.data.find((u: any) => u.telegram_id === id) : null
        if (found) {
          useAuth.setState({ ...useAuth.getState(), userId: found.id })
          return
        }
        const tg = (window as any).Telegram?.WebApp?.initDataUnsafe?.user
        const username = tg?.username ? String(tg.username) : `user_${id}`
        const name = [tg?.first_name, tg?.last_name].filter(Boolean).join(' ') || username
        const created = await api.post('/users', { username, telegram_id: id, name })
        useAuth.setState({ ...useAuth.getState(), userId: created.data.id })
      } catch {}
    }
    ensure()
  }, [telegramId])
  return null
}
