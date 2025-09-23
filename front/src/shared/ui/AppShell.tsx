import { ReactNode } from 'react'
import { BackButton } from '@shared/ui/BackButton'
import { useRouterState } from '@tanstack/react-router'
import { useAuth } from '@entities/user/model/useAuth'
import { AuthRequiredOverlay } from '@shared/ui/AuthRequiredOverlay'

export function AppShell({ children }: { children: ReactNode }) {
  const { showAuthOverlay } = useAuth()
  const pathname = useRouterState({ select: (s) => s.location.pathname })
  const hideOverlay = pathname.startsWith('/moderation') || pathname.startsWith('/metrics')

  return (
    <div className='min-h-dvh flex flex-col text-white relative'>
      <div className='fixed inset-0 -z-10 bg-black' style={{ backgroundImage: 'url(/zalip%20b.gif)', backgroundSize: 'cover', backgroundPosition: 'center', backgroundRepeat: 'no-repeat', filter: 'brightness(0.35)' }} />
      <BackButton />
      <div className='flex-1'>{children}</div>
      {showAuthOverlay && <AuthRequiredOverlay hidden={hideOverlay} />}
    </div>
  )
}

