import { create } from "zustand";
import { EnvValues, fetchEnv, saveEnv, switchMode } from "../api/env";

interface SettingsState {
  values: EnvValues;
  loading: boolean;
  error?: string;
  fetch: () => Promise<void>;
  save: (values: EnvValues, updatedBy?: string) => Promise<void>;
  setValue: (key: string, value: string) => void;
  switchMode: (mode: "paper" | "real") => Promise<void>;
}

const defaultValues: EnvValues = {
  MODE: "paper",
  EXCHANGE_ACTIVE: "okx"
};

export const useSettingsStore = create<SettingsState>((set, get) => ({
  values: defaultValues,
  loading: false,
  async fetch() {
    set({ loading: true, error: undefined });
    try {
      const data = await fetchEnv();
      set({ values: data.values, loading: false });
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  },
  async save(values, updatedBy) {
    set({ loading: true, error: undefined });
    try {
      await saveEnv(values, updatedBy);
      set({ values, loading: false });
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  },
  setValue(key, value) {
    const values = { ...get().values, [key]: value };
    set({ values });
  },
  async switchMode(mode) {
    set({ loading: true, error: undefined });
    try {
      await switchMode(mode);
      const values = { ...get().values, MODE: mode };
      set({ values, loading: false });
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  }
}));
