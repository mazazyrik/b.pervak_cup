import { useEffect, useMemo, useState } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { api } from '@shared/api/http'
import { useAuth } from '@entities/user/model/useAuth'
import { toast } from 'sonner'

type Match = { id: number; team1_id: number; team2_id: number; date: string; result: string; stage_name: string }
type Team = { id: number; name: string; logo_url?: string }
type Bet = { id: number; user_id: number; match_id: number; result: string }

function slugify(s: string) {
  return s.toLowerCase().replace(/\s+/g, '_')
}

function isValidScore(v: string) {
  if (typeof v !== 'string') return false
  if (!/^\d{1,2}:\d{1,2}$/.test(v)) return false
  const [a, b] = v.split(':').map((x) => Number(x))
  if (Number.isNaN(a) || Number.isNaN(b)) return false
  return a >= 0 && a <= 99 && b >= 0 && b <= 99
}

export function Guess() {
  const { telegramId } = useAuth()
  const effectiveTgId = telegramId
  const qc = useQueryClient()
  const teamsQ = useQuery({
    queryKey: ['teams'],
    queryFn: async () => (await api.get<Team[]>('/teams')).data
  })
  const matchesQ = useQuery({
    queryKey: ['matches', 'byUser', effectiveTgId],
    queryFn: async () => (await api.get<Match[]>(`/matches/user/${effectiveTgId}`)).data,
    enabled: !!effectiveTgId
  })
  const recentQ = useQuery({
    queryKey: ['matches', 'recent', effectiveTgId],
    queryFn: async () => (await api.get<Match[]>(`/matches/user/${effectiveTgId}/recent`)).data,
    enabled: !!effectiveTgId
  })
  const betsQ = useQuery({
    queryKey: ['bets', 'byUser', effectiveTgId],
    queryFn: async () => {
      const uid = useAuth.getState().userId || (await ensureUser())
      const r = await api.get<Bet[]>('/bets')
      return r.data.filter((b) => b.user_id === uid)
    },
    enabled: !!effectiveTgId,
    refetchOnWindowFocus: true,
    refetchInterval: 15000
  })

  const [scores, setScores] = useState<Record<number, string>>({})
  const [pending, setPending] = useState<Record<number, boolean>>({})
  const [locked, setLocked] = useState<Record<number, boolean>>({})

  const teamsMap = useMemo(() => {
    const map: Record<number, Team> = {}
    const arr = teamsQ.data || []
    for (const t of arr) map[t.id] = t
    return map
  }, [teamsQ.data])

  const getLogo = (t?: Team) => {
    if (!t) return undefined
    const base = (import.meta.env as any).VITE_LOGO_BASE || 'https://raw.githubusercontent.com/mazazyrik/b.pervak_cup/refs/heads/main/.logos/'
    const filename = encodeURIComponent(t.name.toLowerCase()) + '.png'
    return base + filename
  }

  const ensureUser = async (): Promise<number> => {
    if (useAuth.getState().userId) return useAuth.getState().userId as number
    const tgId = effectiveTgId
    try {
      const list = await api.get<any[]>('/users')
      const found = Array.isArray(list.data) ? list.data.find((u: any) => String(u.telegram_id) === String(tgId)) : null
      if (found) {
        useAuth.setState({ ...useAuth.getState(), userId: found.id })
        return found.id
      }
    } catch {}
    const username = `user_${tgId}`
    const name = username
    const created = await api.post('/users', { username, telegram_id: tgId, name })
    const id = created.data.id as number
    useAuth.setState({ ...useAuth.getState(), userId: id })
    return id
  }

  useEffect(() => {
    const list = betsQ.data || []
    if (list.length === 0) return
    setScores((s) => {
      const next = { ...s }
      for (const b of list) next[b.match_id] = b.result
      return next
    })
    setLocked((l) => {
      const next = { ...l }
      for (const b of list) next[b.match_id] = true
      return next
    })
  }, [betsQ.data])

  const submit = async (m: Match) => {
    const val = scores[m.id]
    if (!isValidScore(val || '')) {
      toast.error('Введите счёт формата 1:0, 0..99')
      return
    }
    try {
      setPending((p) => ({ ...p, [m.id]: true }))
      const uid = useAuth.getState().userId || (await ensureUser())
      const res = await api.post<Bet>('/bets', { user_id: uid, match_id: m.id, result: val })
      setScores((s) => ({ ...s, [m.id]: res.data.result }))
      setLocked((l) => ({ ...l, [m.id]: true }))
      qc.invalidateQueries({ queryKey: ['bets', 'byUser', effectiveTgId] })
      toast.success('Ставка принята')
    } catch (e: any) {
      toast.error('Не удалось отправить ставку')
    } finally {
      setPending((p) => ({ ...p, [m.id]: false }))
    }
  }

  const onChangeLeft = (m: Match, v: string) => {
    const clean = v.replace(/[^0-9]/g, '').slice(0, 2)
    const right = (scores[m.id]?.split(':')[1] || '').replace(/[^0-9]/g, '').slice(0, 2)
    setScores((s) => ({ ...s, [m.id]: `${clean}:${right}` }))
  }
  const onChangeRight = (m: Match, v: string) => {
    const clean = v.replace(/[^0-9]/g, '').slice(0, 2)
    const left = (scores[m.id]?.split(':')[0] || '').replace(/[^0-9]/g, '').slice(0, 2)
    setScores((s) => ({ ...s, [m.id]: `${left}:${clean}` }))
  }

  const renderMatch = (m: Match) => {
    const t1 = teamsMap[m.team1_id]
    const t2 = teamsMap[m.team2_id]
    const v = scores[m.id] || ''
    const [l, r] = v.split(':')
    const ok = isValidScore(v)
    const isLocked = !!locked[m.id]
    return (
      <div key={m.id} className='rounded-2xl p-3 bg-black/40 border border-white/10 mb-3 card-appear'>
        <div className='flex items-center justify-between gap-3'>
          <div className='flex-1 flex flex-col items-center gap-1'>
            <img src={getLogo(t1)} onError={(e) => ((e.target as HTMLImageElement).style.display = 'none')} alt='' className='h-10 object-contain fade-in' />
            <div className='text-sm font-medium text-center'>{t1?.name || `Команда ${m.team1_id}`}</div>
          </div>
          <div className='flex items-center gap-2'>
            <input value={l || ''} onChange={(e) => onChangeLeft(m, e.target.value)} inputMode='numeric' pattern='[0-9]*' disabled={isLocked} className='w-12 h-12 text-center text-lg rounded-lg bg-neutral-900 border border-white/10 disabled:opacity-60' />
            <div className='w-4 text-center'>:</div>
            <input value={r || ''} onChange={(e) => onChangeRight(m, e.target.value)} inputMode='numeric' pattern='[0-9]*' disabled={isLocked} className='w-12 h-12 text-center text-lg rounded-lg bg-neutral-900 border border-white/10 disabled:opacity-60' />
          </div>
          <div className='flex-1 flex flex-col items-center gap-1'>
            <img src={getLogo(t2)} onError={(e) => ((e.target as HTMLImageElement).style.display = 'none')} alt='' className='h-10 object-contain fade-in' />
            <div className='text-sm font-medium text-center'>{t2?.name || `Команда ${m.team2_id}`}</div>
          </div>
        </div>
        <div className='mt-3 flex justify-center'>
          <button disabled={isLocked || !ok || !!pending[m.id]} onClick={() => submit(m)} className={'px-4 py-2 rounded-full text-sm button-pop ' + (isLocked ? 'bg-neutral-800 text-neutral-400' : ok ? 'bg-white text-black' : 'bg-neutral-800 text-neutral-400')}>{isLocked ? 'Ставка принята' : pending[m.id] ? '...' : 'Поставить'}</button>
        </div>
      </div>
    )
  }

  const recent = recentQ.data || []
  const list = matchesQ.data || []

  return (
    <div className='min-h-dvh px-4 py-6 flex flex-col items-center gap-4'>
      <img src='/logo_pages.png' alt='' className='h-8 object-contain fade-in' />
      <div className='w-full max-w-sm text-center'>
        <div className='text-xl font-semibold mb-3 slide-up'>Угадай исход</div>
        <div className='mb-4'>
          <div className='text-sm mb-2 opacity-80 slide-up'>Недавние матчи</div>
          <div className='flex gap-3 overflow-x-auto no-scrollbar pb-1'>
            {recent.map((m) => {
              const t1 = teamsMap[m.team1_id]
              const t2 = teamsMap[m.team2_id]
              return (
                <div key={m.id} className='min-w-[260px] rounded-xl p-3 bg-black/40 border border-white/10 card-appear'>
                  <div className='flex items-center justify-between gap-3'>
                    <div className='flex items-center gap-2'>
                      <img src={getLogo(t1)} onError={(e) => ((e.target as HTMLImageElement).style.display = 'none')} alt='' className='h-8 object-contain fade-in' />
                      <div className='text-sm'>{t1?.name || `Команда ${m.team1_id}`}</div>
                    </div>
                    <div className='opacity-90 text-sm px-2 py-1 rounded-md bg-neutral-900 border border-white/10'>{m.result}</div>
                    <div className='flex items-center gap-2'>
                      <img src={getLogo(t2)} onError={(e) => ((e.target as HTMLImageElement).style.display = 'none')} alt='' className='h-8 object-contain fade-in' />
                      <div className='text-sm'>{t2?.name || `Команда ${m.team2_id}`}</div>
                    </div>
                  </div>
                </div>
              )
            })}
            {recent.length === 0 && (
              <div className='w-full flex justify-center'>
                <div className='text-sm text-neutral-400'>Нет недавних матчей</div>
              </div>
            )}
          </div>
        </div>
        <div className='text-sm mb-2 opacity-80 slide-up'>Матчи для ставки</div>
        {matchesQ.isLoading || teamsQ.isLoading ? (
          <div className='space-y-3'>
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className='h-24 bg-neutral-900 animate-pulse rounded-xl' />
            ))}
          </div>
        ) : (
          <div>
            {list.map((m) => renderMatch(m))}
            {list.length === 0 && <div className='text-sm text-neutral-400'>Нет доступных матчей</div>}
          </div>
        )}
      </div>
    </div>
  )
}

