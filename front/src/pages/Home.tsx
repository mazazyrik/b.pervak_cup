import { Link } from '@tanstack/react-router'
import { useAuth } from '@entities/user/model/useAuth'

export function Home() {
  const { telegramId } = useAuth()
  return (
    <div className='p-4 flex flex-col gap-6'>
      <div className='mt-2'>
        <div className='text-2xl font-semibold mb-1'>Меню</div>
        <div className='text-sm text-neutral-400'>ID: {telegramId || '—'}</div>
      </div>
      <div className='grid grid-cols-2 gap-3'>
        <Link to='/camera' className='rounded-2xl bg-white text-black p-4 h-28 flex items-end font-medium'>
          Сфоткать
        </Link>
        <Link to='/feed' className='rounded-2xl bg-neutral-900 p-4 h-28 flex items-end font-medium'>
          Лента
        </Link>
        <Link to='/guess' className='rounded-2xl bg-neutral-900 p-4 h-28 flex items-end font-medium col-span-2'>
          Угадай исход
        </Link>
      </div>
    </div>
  )
}

