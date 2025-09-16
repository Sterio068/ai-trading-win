import { create } from "zustand"
import { fetchEnv, switchMode, updateEnv, type EnvSettings } from "../api/env"

interface SettingsState {
  env: EnvSettings
  loading: boolean
  mode: string
  load: () => Promise<void>
  save: (values: Partial<EnvSettings>) => Promise<void>
  toggleMode: (mode: "PAPER" | "REAL") => Promise<void>
}

export const useSettingsStore = create<SettingsState>((set, get) => ({
  env: {},
  loading: false,
  mode: "PAPER",
  load: async () => {
    set({ loading: true })
    const data = await fetchEnv()
    set({ env: data, loading: false, mode: (data.MODE as string) ?? "PAPER" })
  },
  save: async (values) => {
    set({ loading: true })
    const data = await updateEnv(values)
    set({ env: data, loading: false })
  },
  toggleMode: async (mode) => {
    await switchMode(mode)
    await get().load()
  },
}))
