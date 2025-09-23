import { Link } from '@tanstack/react-router'
import { useAuth } from '@entities/user/model/useAuth'

export function Home() {
  useAuth()
  return (
    <div className='min-h-dvh px-4 flex flex-col justify-center gap-6' style={{ transform: 'translateY(-10px)' }}>
      <div className='flex justify-center' style={{ transform: 'translateY(-10px)' }}>
        <img src='/cp.png' alt='' className='max-w-full h-12 object-contain drop-shadow-[0_2px_8px_rgba(0,0,0,0.6)] fade-in' />
      </div>
      <div className='flex flex-col gap-3'>
        <Link to='/camera' className='h-14 rounded-2xl bg-white text-black font-medium flex items-center justify-center button-pop'>Сфоткать</Link>
        <Link to='/feed' className='h-14 rounded-2xl bg-neutral-900 font-medium flex items-center justify-center button-pop' style={{ animationDelay: '80ms' }}>Лента</Link>
        <Link to='/guess' className='h-14 rounded-2xl bg-neutral-900 font-medium flex items-center justify-center button-pop' style={{ animationDelay: '160ms' }}>Угадай исход</Link>
      </div>
    </div>
  )
}

