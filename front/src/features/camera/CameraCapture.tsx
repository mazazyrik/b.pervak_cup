import { useEffect, useRef, useState } from 'react'
import { useCamera } from './useCamera'
import { toast } from 'sonner'

type Props = {
  onCapture: (blob: Blob, url: string) => void
  shootRef?: React.MutableRefObject<(() => void) | null>
}

export function CameraCapture({ onCapture, shootRef }: Props) {
  const { videoRef, isActive, error, fallbackEnabled, start, stop, capture } = useCamera()
  const [busy, setBusy] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    start()
    return () => stop()
  }, [start, stop])

  useEffect(() => {
    if (error) toast.error('Проблема с камерой')
  }, [error])

  const onShoot = async () => {
    if (busy) return
    setBusy(true)
    try {
      const { blob, url } = await capture()
      onCapture(blob, url)
      const tg = (window as any).Telegram?.WebApp
      tg?.HapticFeedback?.impactOccurred?.('light')
    } catch {
      toast.error('Не удалось сделать снимок')
    } finally {
      setBusy(false)
    }
  }

  useEffect(() => {
    if (shootRef) shootRef.current = onShoot
  }, [shootRef, onShoot])

  const onPickFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (!f) return
    const url = URL.createObjectURL(f)
    onCapture(f, url)
  }

  return (
    <div className='flex flex-col gap-3'>
      <div className='relative w-full aspect-[3/4] bg-black rounded-xl overflow-hidden'>
        <video ref={videoRef} autoPlay muted playsInline className='w-full h-full object-cover' />
        <div className='pointer-events-none absolute inset-0 grid grid-cols-3 grid-rows-3'>
          <div className='border border-white/10' />
          <div className='border border-white/10' />
          <div className='border border-white/10' />
          <div className='border border-white/10' />
          <div className='border border-white/10' />
          <div className='border border-white/10' />
          <div className='border border-white/10' />
          <div className='border border-white/10' />
          <div className='border border-white/10' />
        </div>
      </div>

      <button onClick={onShoot} disabled={!isActive || busy} className='h-14 rounded-full bg-white text-black font-medium'>
        Сфоткать
      </button>

      {fallbackEnabled && (
        <div className='flex flex-col gap-2'>
          <input ref={inputRef} type='file' accept='image/*' capture='environment' onChange={onPickFile} className='hidden' />
          <button onClick={() => inputRef.current?.click()} className='h-12 rounded-md bg-neutral-800'>
            Выбрать файл
          </button>
        </div>
      )}
    </div>
  )
}

