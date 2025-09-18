import { useAuth } from '@entities/user/model/useAuth'
import { initTelegram } from '@app/telegram/initTelegram'
import { ThemeProvider } from '@app/providers/ThemeProvider'
import { QueryProvider } from '@app/providers/QueryProvider'
import { createRootRouteWithContext } from '@tanstack/react-router'

const { telegramId } = initTelegram()
if (telegramId) {
  const { telegramId: _, ...s } = useAuth.getState()
  useAuth.setState({ ...s, telegramId })
}

export const Route = createRootRouteWithContext<{ }>()({
  component: () => (
    <ThemeProvider>
      <QueryProvider>
        <div />
      </QueryProvider>
    </ThemeProvider>
  )
})

