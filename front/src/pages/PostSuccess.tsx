import { Link, useSearch } from '@tanstack/react-router'

export function PostSuccess() {
  const search = useSearch({ from: '/success' }) as any
  const username = search?.username || 'Пользователь'
  const photoUrl = search?.photo_url as string | undefined
  return (
    <div className='min-h-dvh px-4 py-6 flex flex-col items-center gap-4'>
      <img src='/logo_pages.png' alt='' className='h-8 object-contain' />
      <div className='text-lg font-semibold mt-2'>{username}</div>
      {photoUrl && <img src={photoUrl} alt='' className='w-full max-w-sm rounded-xl' />}
      <div className='text-center text-sm italic opacity-80 text-white max-w-sm'>
        Пост отправлен на модерацию. После проверки он появится в ленте.
      </div>
      <div className='flex-1' />
      <Link to='/feed' className='w-full max-w-sm h-14 rounded-full bg-white text-black font-medium flex items-center justify-center'>
        В ленту
      </Link>
    </div>
  )
}


