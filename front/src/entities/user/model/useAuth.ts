import { create } from 'zustand'
import { initTelegram } from '@app/telegram/initTelegram'

type AuthState = {
  telegramId: string | null
  userId: number | null
  showAuthOverlay: boolean
  setUserId: (id: number | null) => void
  setShowAuthOverlay: (show: boolean) => void
}

const { telegramId } = initTelegram()

export const useAuth = create<AuthState>((set) => ({
  telegramId,
  userId: null,
  showAuthOverlay: false,
  setUserId: (id) => set({ userId: id }),
  setShowAuthOverlay: (show) => set({ showAuthOverlay: show })
}))

