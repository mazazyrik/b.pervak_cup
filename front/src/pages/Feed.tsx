import { Gallery } from '@features/posts/Gallery'

export function Feed() {
  return (
    <div className='pt-3'>
      <div className='px-4 mb-2 text-xl font-semibold'>Лента</div>
      <Gallery />
    </div>
  )
}

