import { ReactNode } from 'react'
import { BackButton } from '@shared/ui/BackButton'
import { useAuth } from '@entities/user/model/useAuth'
import { AuthRequiredOverlay } from '@shared/ui/AuthRequiredOverlay'

export function AppShell({ children }: { children: ReactNode }) {
  const { showAuthOverlay } = useAuth()

  return (
    <div className='min-h-dvh flex flex-col text-white relative'>
      <div className='fixed inset-0 -z-10 bg-black' style={{ backgroundImage: 'url(/fon.png)', backgroundSize: 'cover', backgroundPosition: 'center' }} />
      <BackButton />
      <div className='flex-1'>{children}</div>
      {showAuthOverlay && <AuthRequiredOverlay />}
    </div>
  )
}

