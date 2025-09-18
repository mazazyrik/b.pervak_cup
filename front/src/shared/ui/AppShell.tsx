import { ReactNode } from 'react'

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className='min-h-dvh flex flex-col text-white relative'>
      <div className='fixed inset-0 -z-10 bg-black' style={{ backgroundImage: "url('/fon.png')", backgroundSize: 'cover', backgroundPosition: 'center' }} />
      <div className='flex-1'>{children}</div>
    </div>
  )
}

