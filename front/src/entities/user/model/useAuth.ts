import { create } from 'zustand'
import { initTelegram } from '@app/telegram/initTelegram'

type AuthState = {
  telegramId: string | null
  userId: number | null
  showAuthOverlay: boolean
  manualToken: string | null
  setUserId: (id: number | null) => void
  setShowAuthOverlay: (show: boolean) => void
  setManualToken: (token: string | null) => void
}

const { telegramId } = initTelegram()

export const useAuth = create<AuthState>((set) => ({
  telegramId,
  userId: null,
  showAuthOverlay: false,
  manualToken: null,
  setUserId: (id) => set({ userId: id }),
  setShowAuthOverlay: (show) => set({ showAuthOverlay: show }),
  setManualToken: (token) => set({ manualToken: token })
}))

