import { useState } from 'react'
import { toast } from 'sonner'
import { api } from '@shared/api/http'
import { router } from '@app/router'
import { useAuth } from '@entities/user/model/useAuth'

export function CreatePost() {
  const [lastShot, setLastShot] = useState<string | null>(null)
  const { userId, telegramId } = useAuth()

  const ensureUser = async (): Promise<number> => {
    if (useAuth.getState().userId) return useAuth.getState().userId as number
    const effectiveTgId = telegramId
    try {
      const list = await api.get('/users')
      const found = Array.isArray(list.data)
        ? list.data.find((u: any) => String(u.telegram_id) === String(effectiveTgId))
        : null
      if (found) {
        useAuth.setState({ ...useAuth.getState(), userId: found.id })
        return found.id
      }
    } catch {}
    const username = `user_${effectiveTgId}`
    const name = username
    const created = await api.post('/users', { username, telegram_id: effectiveTgId, name })
    const id = created.data.id as number
    useAuth.setState({ ...useAuth.getState(), userId: id })
    return id
  }

  const onCaptured = async (blob: Blob, url: string) => {
    setLastShot(url)
    try {
      const uid = userId || await ensureUser()
      const f = new FormData()
      f.append('user_id', String(uid))
      f.append('checked', 'false')
      f.append('file', new File([blob], 'photo.jpg', { type: 'image/jpeg' }))
      const r = await api.post('/posts', f, { headers: { 'Content-Type': 'multipart/form-data' } })
      const publicUrl: string = r.data?.photo_url
      const username = `user_${(useAuth.getState().telegramId)}`
      router.navigate({ to: '/success', search: { photo_url: publicUrl, username } })
    } catch (e) {
      if (import.meta.env.DEV) console.warn('save_failed', e)
      toast.error('Не удалось сохранить')
    }
  }

  return { onCaptured, lastShot }
}

