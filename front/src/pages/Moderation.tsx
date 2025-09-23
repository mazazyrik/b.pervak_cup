import { useEffect, useMemo, useState } from 'react'
import { AuthTokenBar } from '@shared/ui/AuthTokenBar'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@shared/api/http'
import type { Post } from '@entities/post/model/types'

export function Moderation() {
  const qc = useQueryClient()
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['posts', 'unchecked'],
    queryFn: async () => (await api.get<Post[]>('/posts/unchecked')).data,
    refetchOnWindowFocus: true,
    refetchInterval: 15000
  })

  const approve = useMutation({
    mutationFn: async (id: number) => (await api.put(`/posts/${id}`, { checked: true })).data,
    onSuccess: (_, id) => {
      qc.setQueryData<Post[] | undefined>(['posts', 'unchecked'], (old) => old ? old.filter((p) => p.id !== id) : old)
      qc.invalidateQueries({ queryKey: ['posts'] })
    }
  })

  const remove = useMutation({
    mutationFn: async (id: number) => api.delete(`/posts/${id}`),
    onSuccess: (_, id) => {
      qc.setQueryData<Post[] | undefined>(['posts', 'unchecked'], (old) => old ? old.filter((p) => p.id !== id) : old)
    }
  })

  const items = useMemo(() => data || [], [data])
  const [preview, setPreview] = useState<string | null>(null)

  useEffect(() => {
    const t = setTimeout(() => refetch(), 0)
    return () => clearTimeout(t)
  }, [refetch])

  return (
    <div className='p-0'>
      <AuthTokenBar />
      <div className='p-4'>
      <div className='text-xl font-semibold mb-3 slide-up'>Модерация</div>
      {isLoading && (
        <div className='columns-2 gap-2 sm:columns-3'>
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className='w-full h-40 bg-neutral-900 animate-pulse rounded-xl mb-2' />
          ))}
        </div>
      )}
      {isError && (
        <div className='text-sm text-red-400 mb-3'>Ошибка загрузки <button onClick={() => refetch()} className='underline'>повторить</button></div>
      )}
      {!!items && items.length > 0 && (
        <div className='columns-1 sm:columns-2 gap-3'>
          {items.map((p, idx) => (
            <div key={p.id} className='break-inside-avoid mb-3 rounded-xl overflow-hidden border border-white/10 bg-black/30 card-appear' style={{ animationDelay: `${idx * 30}ms` }}>
              <button onClick={() => setPreview(p.photo_url)} className='block w-full group'>
                <img src={p.photo_url} alt='' className='w-full object-cover block transition-transform duration-300 group-hover:scale-[1.02]' />
              </button>
              <div className='p-3 flex items-center justify-between gap-2'>
                <div className='text-xs opacity-70'>#{p.id} · user {p.user_id}</div>
                <div className='flex items-center gap-2'>
                  <button disabled={approve.isPending} onClick={() => approve.mutate(p.id)} className='px-3 py-1 rounded-full bg-white text-black text-sm button-pop disabled:opacity-60'>Одобрить</button>
                  <button disabled={remove.isPending} onClick={() => remove.mutate(p.id)} className='px-3 py-1 rounded-full bg-neutral-800 text-white text-sm button-pop disabled:opacity-60' style={{ animationDelay: '60ms' }}>Удалить</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      {!!items && items.length === 0 && !isLoading && (
        <div className='text-center text-sm text-neutral-400 py-10'>Нет непроверенных постов</div>
      )}

      {preview && (
        <div className='fixed inset-0 z-50 bg-black/60 flex items-center justify-center fade-in' onClick={() => setPreview(null)}>
          <img src={preview} alt='' className='max-w-[92vw] max-h-[80vh] rounded-xl shadow-2xl' />
        </div>
      )}
      </div>
    </div>
  )
}


