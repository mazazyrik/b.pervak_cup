import { useState } from 'react'
import { toast } from 'sonner'
import { api } from '@shared/api/http'
import { useAuth } from '@entities/user/model/useAuth'
import { chooseUploader } from '@shared/lib/uploader'

export function CreatePost() {
  const [lastShot, setLastShot] = useState<string | null>(null)
  const { userId } = useAuth()

  const onCaptured = async (blob: Blob, url: string) => {
    setLastShot(url)
    try {
      const { url: publicUrl } = await chooseUploader().upload(blob)
      if (!userId) throw new Error('no_user')
      await api.post('/posts', { user_id: userId, photo_url: publicUrl, checked: false })
      toast.success('Сохранено на модерацию')
    } catch {
      toast.error('Не удалось сохранить')
    }
  }

  return { onCaptured, lastShot }
}

