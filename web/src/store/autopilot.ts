import { create } from "zustand"
import { autopilotStatus, startAutopilot, stopAutopilot } from "../api/strategy"

interface AutopilotState {
  status: any
  loading: boolean
  load: () => Promise<void>
  start: (interval?: number) => Promise<void>
  stop: () => Promise<void>
}

export const useAutopilotStore = create<AutopilotState>((set) => ({
  status: {},
  loading: false,
  load: async () => {
    set({ loading: true })
    const data = await autopilotStatus()
    set({ status: data, loading: false })
  },
  start: async (interval?: number) => {
    set({ loading: true })
    const data = await startAutopilot(interval)
    set({ status: data, loading: false })
  },
  stop: async () => {
    set({ loading: true })
    const data = await stopAutopilot()
    set({ status: data, loading: false })
  },
}))
