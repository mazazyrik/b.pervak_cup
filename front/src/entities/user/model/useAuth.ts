import { create } from 'zustand'
import { initTelegram } from '@app/telegram/initTelegram'

type AuthState = {
  telegramId: string | null
  userId: number | null
  setUserId: (id: number | null) => void
}

const { telegramId } = initTelegram()

export const useAuth = create<AuthState>((set) => ({
  telegramId,
  userId: null,
  setUserId: (id) => set({ userId: id })
}))

