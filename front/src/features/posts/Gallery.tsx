import { useQuery } from '@tanstack/react-query'
import { api } from '@shared/api/http'
import type { Post } from '@entities/post/model/types'

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
      <div className='flex items-center justify-between mb-3'>
        <div className='text-sm text-neutral-400'>Лента</div>
        <button onClick={() => refetch()} className='text-sm underline'>Обновить</button>
      </div>
      {isLoading && <div className='grid grid-cols-3 gap-2'>{Array.from({ length: 9 }).map((_, i) => (<div key={i} className='aspect-square bg-neutral-900 animate-pulse rounded-md' />))}</div>}
      {!!data && (
        <div className='grid grid-cols-3 gap-2'>
          {data.map((p) => (
            <img key={p.id} src={p.photo_url} alt='' className='aspect-square object-cover rounded-md' />
          ))}
        </div>
      )}
    </div>
  )
}

