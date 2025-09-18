export function initTelegram() {
  const tg = (window as any).Telegram?.WebApp
  if (!tg) return { telegramId: null as string | null }
  try {
    tg.ready?.()
    tg.expand?.()
  } catch {}
  const id = tg.initDataUnsafe?.user?.id ? String(tg.initDataUnsafe.user.id) : null
  return { telegramId: id }
}

