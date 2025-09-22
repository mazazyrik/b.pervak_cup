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
      className={(inline ? 'absolute left-3 top-1/2 -translate-y-1/2 z-10 ' : 'fixed top-4 left-4 z-50 ') + 'inline-flex items-center justify-center h-20 w-20 rounded-full bg-red-700'}
    >
      <svg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' strokeWidth={2} stroke='currentColor' className='w-10 h-10'>
        <path strokeLinecap='round' strokeLinejoin='round' d='M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18' />
      </svg>
    </button>
  )
}


