import { useEffect, useRef, useState } from 'react'
import { CameraCapture } from '@features/camera/CameraCapture'
import { CreatePost } from '@features/posts/CreatePost'

export function Camera() {
  const [last, setLast] = useState<string | null>(null)
  const { onCaptured } = CreatePost()
  const shootRef = useRef<(() => void) | null>(null)

  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp
    tg?.MainButton?.setText?.('Сфоткать')
    tg?.MainButton?.show?.()
    const off = tg?.onEvent?.('mainButtonClicked', () => {})
    tg?.BackButton?.show?.()
    const offBack = tg?.onEvent?.('backButtonClicked', () => window.history.back())
    return () => {
      tg?.MainButton?.hide?.()
      tg?.BackButton?.hide?.()
      if (off && typeof off === 'function') off()
      if (offBack && typeof offBack === 'function') offBack()
    }
  }, [])

  return (
    <div className='p-4 flex flex-col gap-3'>
      <div className='text-xl font-semibold mb-1'>Сфоткать</div>
      <CameraCapture shootRef={shootRef} onCapture={(b, url) => { setLast(url); onCaptured(b, url) }} />
      {last && (
        <div className='flex items-center gap-3'>
          <img src={last} alt='' className='w-16 h-16 object-cover rounded-md' />
          <div className='text-sm text-neutral-400'>Снимок сохранен локально</div>
        </div>
      )}
      <button onClick={() => shootRef.current?.()} className='h-12 rounded-full bg-white text-black'>Сфоткать</button>
    </div>
  )
}

