import { useQuery } from '@tanstack/react-query'
import { api } from '@shared/api/http'
import type { Post } from '@entities/post/model/types'
import { Link } from '@tanstack/react-router'

export function Gallery() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['posts'],
    queryFn: async () => {
      const r = await api.get<Post[]>('/posts')
      return r.data
    }
  })

  return (
    <div className='p-4'>
      {isLoading && (
        <div className='columns-2 gap-2 sm:columns-3'>
          {Array.from({ length: 9 }).map((_, i) => (
            <div key={i} className='w-full h-40 bg-neutral-900 animate-pulse rounded-xl mb-2' />
          ))}
        </div>
      )}
      {!!data && data.length > 0 && (
        <div className='columns-2 gap-2 sm:columns-3'>
          {data.map((p, idx) => {
            const src = p.photo_url.startsWith('blob:') ? p.photo_url.slice(5) : p.photo_url
            const h = 140 + (idx % 3) * 40
            return (
              <Link key={p.id} to={`/post/${p.id}`} className='no-underline'>
                <img
                  src={src}
                  alt=''
                  loading='lazy'
                  className='w-full object-cover rounded-xl mb-2 block'
                  style={{ height: h }}
                />
              </Link>
            )
          })}
        </div>
      )}
      {!!data && data.length === 0 && (
        <div className='text-center text-sm text-neutral-400 py-10'>Пока постов нет</div>
      )}
    </div>
  )
}

