import { useQuery } from '@tanstack/react-query'
import { createFileRoute, useParams } from '@tanstack/react-router'
import { api } from '@shared/api/http'
import type { Post as PostType } from '@entities/post/model/types'
import { useEffect, useRef, useState } from 'react'

export function Post() {
  const { postId } = useParams({ strict: false }) as { postId: string }
  const { data } = useQuery({
    queryKey: ['post', postId],
    queryFn: async () => (await api.get<PostType>(`/posts/${postId}`)).data
  })
  const imgRef = useRef<HTMLImageElement | null>(null)
  const [scale, setScale] = useState(1)
  const [origin, setOrigin] = useState<'center' | 'top-left'>('center')
  const [visible, setVisible] = useState(false)

  const onDoubleClick = () => setScale((s) => (s === 1 ? 2 : 1))
  const onWheel: React.WheelEventHandler = (e) => {
    e.preventDefault()
    const next = Math.min(4, Math.max(1, scale + (e.deltaY < 0 ? 0.1 : -0.1)))
    setScale(Number(next.toFixed(2)))
  }

  useEffect(() => {
    const t = setTimeout(() => setVisible(true), 0)
    return () => clearTimeout(t)
  }, [])

  if (!data) return <div className='p-4'>Загрузка...</div>
  const src = data.photo_url.startsWith('blob:') ? data.photo_url.slice(5) : data.photo_url
  return (
    <div className='w-full h-[calc(100dvh-56px)] flex items-center justify-center bg-black/60'>
      <img
        ref={imgRef}
        src={src}
        alt=''
        onDoubleClick={onDoubleClick}
        onWheel={onWheel}
        className='max-w-full max-h-full select-none transition-all duration-300 ease-out'
        style={{ opacity: visible ? 1 : 0, transform: `scale(${visible ? scale : 0.95})`, transformOrigin: origin === 'center' ? 'center' : '0 0', borderRadius: 16 }}
      />
    </div>
  )
}


