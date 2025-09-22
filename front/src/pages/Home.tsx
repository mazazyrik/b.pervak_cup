import { Link } from '@tanstack/react-router'
import { useAuth } from '@entities/user/model/useAuth'

export function Home() {
  useAuth()
  return (
    <div className='min-h-dvh px-4 flex flex-col justify-center gap-6'>
      <div className='flex justify-center'>
        <img src='/cp.png' alt='' className='max-w-full h-12 object-contain drop-shadow-[0_2px_8px_rgba(0,0,0,0.6)]' />
      </div>
      <div className='flex flex-col gap-3'>
        <Link to='/camera' className='h-14 rounded-2xl bg-white text-black font-medium flex items-center justify-center'>Сфоткать</Link>
        <Link to='/feed' className='h-14 rounded-2xl bg-neutral-900 font-medium flex items-center justify-center'>Лента</Link>
        <Link to='/guess' className='h-14 rounded-2xl bg-neutral-900 font-medium flex items-center justify-center'>Угадай исход</Link>
      </div>
    </div>
  )
}

