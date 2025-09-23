import { useRef } from 'react'
import { router } from '@app/router'
import { toast } from 'sonner'

type Props = {
  onCapture: (blob: Blob, url: string) => void
}

export function CameraCapture({ onCapture }: Props) {
  const inputRef = useRef<HTMLInputElement>(null)

  const onPickFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    try {
      const url = URL.createObjectURL(f)
      onCapture(f, url)
      router.navigate({ to: '/success', search: { photo_url: url, username: 'user' } })
    } catch {
      toast.error('Не удалось обработать файл')
    }
  }

  return (
    <div className='flex flex-col gap-3'>
      <input ref={inputRef} type='file' accept='image/*' capture='environment' onChange={onPickFile} className='hidden' />
      <button onClick={() => inputRef.current?.click()} className='h-14 rounded-full bg-white text-black font-medium'>
        Сделать фото
      </button>
    </div>
  )
}

