import { useEffect, useState } from 'react'
import { CameraCapture } from '@features/camera/CameraCapture'
import { CreatePost } from '@features/posts/CreatePost'

export function Camera() {
  const [last, setLast] = useState<string | null>(null)
  const { onCaptured } = CreatePost()

  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp
    tg?.MainButton?.hide?.()
    tg?.BackButton?.show?.()
    const offBack = tg?.onEvent?.('backButtonClicked', () => window.history.back())
    return () => {
      tg?.BackButton?.hide?.()
      if (offBack && typeof offBack === 'function') offBack()
    }
  }, [])

  return (
    <div className='min-h-dvh px-4 py-6 flex flex-col items-center gap-4'>
      <img src='/logo_pages.png' alt='' className='h-8 object-contain fade-in' />
      <div className='flex-1' />
      <img src='https://raw.githubusercontent.com/mazazyrik/b.pervak_cup/refs/heads/main/front/public/photo.png' alt='' className='w-full max-w-sm rounded-xl slide-up' />
      <div className='text-center text-sm italic opacity-80 text-white max-w-sm slide-up' style={{ animationDelay: '80ms' }}>
        Запечатли свои лучшие моменты с Кубка Первокурсника, и они появятся в ленте!
      </div>
      <div className='flex-1' />
      <div className='w-full max-w-sm button-pop'>
        <CameraCapture onCapture={(b, url) => { setLast(url); onCaptured(b, url) }} />
      </div>
      {last && (
        <div className='flex items-center gap-3 fade-in'>
          <img src={last} alt='' className='w-16 h-16 object-cover rounded-md' />
          <div className='text-sm text-neutral-400'>Снимок сохранен локально</div>
        </div>
      )}
    </div>
  )
}

