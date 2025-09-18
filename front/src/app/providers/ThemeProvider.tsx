import { ReactNode, useEffect } from 'react'

type ThemeParams = Record<string, string | undefined>

export function ThemeProvider({ children }: { children: ReactNode }) {
  useEffect(() => {
    const tg = (window as any).Telegram?.WebApp
    if (!tg) return
    const apply = (p: ThemeParams) => {
      const root = document.documentElement
      if (p.bg_color) root.style.setProperty('--tg-bg', p.bg_color)
      if (p.text_color) root.style.setProperty('--tg-text', p.text_color)
    }
    apply(tg.themeParams || {})
    const off = tg.onEvent?.('themeChanged', () => apply(tg.themeParams || {}))
    return () => {
      if (off && typeof off === 'function') off()
    }
  }, [])
  return <>{children}</>
}

