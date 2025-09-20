import { useQuery } from '@tanstack/react-query'
import { createFileRoute, useParams } from '@tanstack/react-router'
import { api } from '@shared/api/http'
import type { Post as PostType } from '@entities/post/model/types'
import { useEffect, useRef, useState } from 'react'

export function Post() {
  const { postId } = useParams({ strict: false }) as { postId: string }
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['post', postId],
    queryFn: async () => (await api.get<PostType>(`/posts/${postId}`)).data
  })
  const imgRef = useRef<HTMLImageElement | null>(null)
  const [scale, setScale] = useState(1)
  const [origin, setOrigin] = useState<'center' | 'top-left'>('center')
  const [visible, setVisible] = useState(false)
  const [tx, setTx] = useState(0)
  const [ty, setTy] = useState(0)
  const [imgLoaded, setImgLoaded] = useState(false)
  const [imgError, setImgError] = useState(false)
  const touch = useRef({ mode: 'none' as 'none' | 'pan' | 'pinch', sx: 0, sy: 0, stx: 0, sty: 0, sScale: 1, sDist: 0, ex: 0, ey: 0 })

  const onDoubleClick = () => setScale((s) => (s === 1 ? 2 : 1))
  const onWheel: React.WheelEventHandler = (e) => {
    e.preventDefault()
    const next = Math.min(4, Math.max(1, scale + (e.deltaY < 0 ? 0.1 : -0.1)))
    setScale(Number(next.toFixed(2)))
  }

  const onTouchStart: React.TouchEventHandler = (e) => {
    if (e.touches.length === 1) {
      const t = e.touches[0]
      touch.current = { ...touch.current, mode: 'pan', sx: t.clientX, sy: t.clientY, stx: tx, sty: ty, sScale: scale, sDist: 0, ex: t.clientX, ey: t.clientY }
    } else if (e.touches.length === 2) {
      const a = e.touches[0]
      const b = e.touches[1]
      const dx = a.clientX - b.clientX
      const dy = a.clientY - b.clientY
      const dist = Math.hypot(dx, dy)
      touch.current = { ...touch.current, mode: 'pinch', sDist: dist, sScale: scale }
    }
  }
  const onTouchMove: React.TouchEventHandler = (e) => {
    if (touch.current.mode === 'pan' && e.touches.length === 1) {
      const t = e.touches[0]
      touch.current.ex = t.clientX
      touch.current.ey = t.clientY
      if (scale > 1) {
        setTx(touch.current.stx + (t.clientX - touch.current.sx))
        setTy(touch.current.sty + (t.clientY - touch.current.sy))
      }
    }
    if (touch.current.mode === 'pinch' && e.touches.length === 2) {
      const a = e.touches[0]
      const b = e.touches[1]
      const dx = a.clientX - b.clientX
      const dy = a.clientY - b.clientY
      const dist = Math.hypot(dx, dy)
      const next = Math.min(4, Math.max(1, (dist / (touch.current.sDist || 1)) * touch.current.sScale))
      setScale(Number(next.toFixed(2)))
    }
  }
  const onTouchEnd: React.TouchEventHandler = () => {
    if (touch.current.mode === 'pan' && scale === 1) {
      const dx = touch.current.ex - touch.current.sx
      const dy = touch.current.ey - touch.current.sy
      if (dx > 100 && Math.abs(dy) < 80) {
        if (window.history.length > 1) window.history.back()
      }
    }
    touch.current.mode = 'none'
  }

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 0)
    return () => clearTimeout(t)
  }, [])

  if (isLoading) return (
    <div className='w-full h-[calc(100dvh-56px)] flex items-center justify-center bg-black/60'>
      <div className='w-64 h-64 bg-neutral-900 animate-pulse rounded-xl' />
    </div>
  )
  if (isError || imgError) return (
    <div className='w-full h-[calc(100dvh-56px)] flex flex-col items-center justify-center gap-3'>
      <div className='text-sm text-red-400'>Не удалось загрузить</div>
      <button onClick={() => { setImgError(false); refetch() }} className='px-4 py-2 rounded-full bg-white text-black text-sm'>Повторить</button>
    </div>
  )
  if (!data) return null
  const src = data.photo_url.startsWith('blob:') ? data.photo_url.slice(5) : data.photo_url
  return (
    <div className='w-full h-[calc(100dvh-56px)] flex items-center justify-center bg-black/60' onTouchStart={onTouchStart} onTouchMove={onTouchMove} onTouchEnd={onTouchEnd}>
      <img
        ref={imgRef}
        src={src}
        alt=''
        onDoubleClick={onDoubleClick}
        onWheel={onWheel}
        onLoad={() => { setImgLoaded(true) }}
        onError={() => { setImgError(true) }}
        className='max-w-full max-h-full select-none transition-all duration-300 ease-out'
        style={{ opacity: visible && imgLoaded ? 1 : 0, transform: `translate(${tx}px, ${ty}px) scale(${visible ? scale : 0.95})`, transformOrigin: origin === 'center' ? 'center' : '0 0', borderRadius: 16 }}
      />
    </div>
  )
}


