import { ReactNode } from 'react'

export function AppShell({ children }: { children: ReactNode }) {
  return <div className='min-h-dvh flex flex-col bg-black text-white'>{children}</div>
}

