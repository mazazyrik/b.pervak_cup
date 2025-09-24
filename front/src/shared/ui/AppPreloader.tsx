import { useEffect, useState } from 'react'
import { useRouterState } from '@tanstack/react-router'
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
  const [fading, setFading] = useState(false)
  const qc = useQueryClient()
  const pathname = useRouterState({ select: (s) => s.location.pathname })

  useEffect(() => {
    const run = async () => {
      await wait(1000)
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
      setFading(true)
    }
    run()
  }, [qc])

  const onTransitionEnd = () => setReady(true)
  if (ready || pathname.startsWith('/moderation')) return null
  return (
    <div
      className={'fixed inset-0 z-[9999] bg-black transition-opacity duration-700 ' + (fading ? 'opacity-0 pointer-events-none' : 'opacity-100')}
      style={{ backgroundImage: 'url(https://raw.githubusercontent.com/mazazyrik/b.pervak_cup/refs/heads/main/front/public/loading.gif)', backgroundSize: 'cover', backgroundPosition: 'center calc(50% - 80px)', backgroundRepeat: 'no-repeat' }}
      onTransitionEnd={onTransitionEnd}
    >
    </div>
  )
}


