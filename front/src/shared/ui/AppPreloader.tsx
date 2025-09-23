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

      await Promise.all([assetsPreload, feedPreload, wait(4000)])
      setReady(true)
    }
    run()
  }, [qc])

  const onFadeOut = () => {
    const root = document.getElementById('root')
    if (root) root.style.opacity = '1'
  }
  if (ready) return <div className='pointer-events-none fixed inset-0 z-[9999] bg-black opacity-0 transition-opacity duration-700' onTransitionEnd={onFadeOut} />
  return (
    <div className='fixed inset-0 z-[9999] bg-black opacity-100 transition-opacity duration-700' style={{ backgroundImage: 'url(https://raw.githubusercontent.com/mazazyrik/b.pervak_cup/refs/heads/main/front/public/loading.gif)', backgroundSize: 'cover', backgroundPosition: 'center', backgroundRepeat: 'no-repeat' }}>
    </div>
  )
}


