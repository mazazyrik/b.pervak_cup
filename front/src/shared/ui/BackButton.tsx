import { useRouterState } from '@tanstack/react-router'
export function BackButton({ inline = false }: { inline?: boolean }) {
  const pathname = useRouterState({ select: (s) => s.location.pathname })
  if (!inline && (pathname === '/' || pathname === '/feed')) return null
  const onClick = () => {
    if (window.history.length > 1) window.history.back()
    else window.location.href = '/'
  }
  return (
    <button
      onClick={onClick}
      className={(inline ? 'absolute left-3 top-1/2 -translate-y-1/2 z-10 ' : 'fixed top-3 left-3 z-50 ') + 'inline-flex items-center justify-center rounded-full bg-black/60 px-3 py-1 text-sm backdrop-blur border border-white/10'}
    >
      {'<-'}
    </button>
  )
}


