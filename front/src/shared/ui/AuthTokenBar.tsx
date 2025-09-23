import { useState } from 'react'
import { useAuth } from '@entities/user/model/useAuth'

export function AuthTokenBar() {
  const { manualToken, setManualToken } = useAuth()
  const [value, setValue] = useState(manualToken || '')
  const apply = () => setManualToken(value.trim() || null)
  const clear = () => {
    setValue('')
    setManualToken(null)
  }
  return (
    <div className='p-3 border-b border-white/10 bg-black/40 flex items-center gap-2'>
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder='Enter token'
        className='flex-1 px-3 py-2 rounded bg-neutral-900 text-sm outline-none'
      />
      <button onClick={apply} className='px-3 py-2 rounded bg-white text-black text-sm'>Authorize</button>
      <button onClick={clear} className='px-3 py-2 rounded bg-neutral-800 text-white text-sm'>Clear</button>
    </div>
  )
}


