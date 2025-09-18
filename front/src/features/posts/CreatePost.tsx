import { useState } from 'react'
import { toast } from 'sonner'
import { api } from '@shared/api/http'
import { router } from '@app/router'
import { useAuth } from '@entities/user/model/useAuth'
import { chooseUploader } from '@shared/lib/uploader'

export function CreatePost() {
  const [lastShot, setLastShot] = useState<string | null>(null)
  const { userId, telegramId } = useAuth()

  const ensureUser = async (): Promise<number> => {
    if (useAuth.getState().userId) return useAuth.getState().userId as number
    const effectiveTgId = telegramId || (import.meta.env as any).VITE_DEV_TG_ID || '123'
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
      const { url: publicUrl } = await chooseUploader().upload(blob)
      const uid = userId || await ensureUser()
      await api.post('/posts', { user_id: uid, photo_url: publicUrl, checked: false })
      const username = `user_${(useAuth.getState().telegramId || (import.meta.env as any).VITE_DEV_TG_ID || '123')}`
      router.navigate({ to: '/success', search: { photo_url: publicUrl, username } })
    } catch (e) {
      if (import.meta.env.DEV) console.warn('save_failed', e)
      toast.error('Не удалось сохранить')
    }
  }

  return { onCaptured, lastShot }
}

