import { useMemo } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@shared/api/http'
import type { Post } from '@entities/post/model/types'

export function Moderation() {
  const qc = useQueryClient()
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['posts', 'unchecked'],
    queryFn: async () => (await api.get<Post[]>('/posts/unchecked')).data
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

  return (
    <div className='p-4'>
      <div className='text-xl font-semibold mb-3'>Модерация</div>
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
          {items.map((p) => (
            <div key={p.id} className='break-inside-avoid mb-3 rounded-xl overflow-hidden border border-white/10 bg-black/30'>
              <img src={p.photo_url} alt='' className='w-full object-cover block' />
              <div className='p-3 flex items-center justify-between gap-2'>
                <div className='text-xs opacity-70'>#{p.id} · user {p.user_id}</div>
                <div className='flex items-center gap-2'>
                  <button disabled={approve.isPending} onClick={() => approve.mutate(p.id)} className='px-3 py-1 rounded-full bg-emerald-500 text-black text-sm disabled:opacity-60'>Одобрить</button>
                  <button disabled={remove.isPending} onClick={() => remove.mutate(p.id)} className='px-3 py-1 rounded-full bg-red-500 text-black text-sm disabled:opacity-60'>Удалить</button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      {!!items && items.length === 0 && !isLoading && (
        <div className='text-center text-sm text-neutral-400 py-10'>Нет непроверенных постов</div>
      )}
    </div>
  )
}


