import { Gallery } from '@features/posts/Gallery'
import { BackButton } from '@shared/ui/BackButton'

export function Feed() {
  return (
    <div className='pt-3'>
      <div className='relative px-4 mb-2 h-10 flex items-center justify-center'>
        <BackButton inline />
        <img src='/logo_pages.png' alt='' className='h-8 object-contain' />
      </div>
      <Gallery />
    </div>
  )
}

