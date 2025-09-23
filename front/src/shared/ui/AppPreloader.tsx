import { useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { api } from '@shared/api/http'
import type { Post } from '@entities/post/model/types'

function preloadImage(src: string) {
  return new Promise<void>((resolve) => {
    const img = new Image()
    img.onload = () => resolve()
    img.onerror = () => resolve()
    img.src = src
  })
}

function wait(ms: number) {
  return new Promise<void>((r) => setTimeout(r, ms))
}

export function AppPreloader() {
  const [ready, setReady] = useState(false)
  const qc = useQueryClient()

  useEffect(() => {
    const run = async () => {
      const assets = [
        '/zalip%20b.gif',
        '/logo_pages.png',
        '/cp.png',
        'https://raw.githubusercontent.com/mazazyrik/b.pervak_cup/refs/heads/main/front/public/photo.png',
        'https://raw.githubusercontent.com/mazazyrik/b.pervak_cup/refs/heads/main/front/public/loading.gif'
      ]

      const assetsPreload = Promise.all(assets.map(preloadImage))

      const feedPreload = api
        .get<Post[]>('/posts')
        .then((r) => {
          qc.setQueryData(['posts'], r.data)
          const urls = r.data
            .map((p) => (p.photo_url.startsWith('blob:') ? p.photo_url.slice(5) : p.photo_url))
            .slice(0, 50)
          return Promise.all(urls.map(preloadImage))
        })
        .catch(() => undefined)

      await Promise.all([assetsPreload, feedPreload, wait(1500)])
      setReady(true)
    }
    run()
  }, [qc])

  if (ready) return null
  return (
    <div className='fixed inset-0 z-[9999] flex items-center justify-center bg-black'>
      <img
        src='https://raw.githubusercontent.com/mazazyrik/b.pervak_cup/refs/heads/main/front/public/loading.gif'
        alt=''
        className='w-40 h-40 object-contain'
      />
    </div>
  )
}


