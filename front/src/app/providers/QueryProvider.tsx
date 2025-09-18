import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactNode, useMemo } from 'react'

export function QueryProvider({ children }: { children: ReactNode }) {
  const client = useMemo(() => new QueryClient(), [])
  return <QueryClientProvider client={client}>{children}</QueryClientProvider>
}

