import { ReactNode } from 'react'

type Props = {
  bg: string
  children?: ReactNode
}

export function Screen({ bg, children }: Props) {
  return (
    <div className='min-h-dvh w-full relative overflow-hidden' style={{ paddingTop: 'env(safe-area-inset-top)', paddingBottom: 'env(safe-area-inset-bottom)' }}>
      <img src={bg} alt='' className='absolute inset-0 w-full h-full object-cover select-none pointer-events-none' />
      <div className='relative z-10'>{children}</div>
    </div>
  )
}

