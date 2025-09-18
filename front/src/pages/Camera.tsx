import { useEffect, useRef, useState } from 'react'
import { CameraCapture } from '@features/camera/CameraCapture'
import { CreatePost } from '@features/posts/CreatePost'
import { Screen } from '@shared/ui/Screen'
import bg from '../../макет б/сфоткать.svg'

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
    <Screen bg={bg}>
      <div className='p-4 pt-[72px]'>
        <CameraCapture shootRef={shootRef} onCapture={(b, url) => { setLast(url); onCaptured(b, url) }} />
        {last && (
          <div className='flex items-center gap-3 mt-2'>
            <img src={last} alt='' className='w-16 h-16 object-cover rounded-md' />
            <div className='text-sm text-neutral-400'>Снимок сохранен локально</div>
          </div>
        )}
      </div>
      <button onClick={() => shootRef.current?.()} className='absolute left-[156px] top-[618px] w-[90px] h-[90px] rounded-full bg-transparent' aria-label='shoot' />
    </Screen>
  )
}

