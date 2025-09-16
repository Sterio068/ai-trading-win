import { create } from "zustand";
import { startAutopilot, stopAutopilot } from "../api/strategy";

interface AutopilotState {
  state: Record<string, unknown> | null;
  loading: boolean;
  error?: string;
  start: (payload: { instId?: string; base_interval_s?: number }) => Promise<void>;
  stop: () => Promise<void>;
  updateFromWs: (payload: Record<string, unknown>) => void;
}

export const useAutopilotStore = create<AutopilotState>((set) => ({
  state: null,
  loading: false,
  async start(payload) {
    set({ loading: true, error: undefined });
    try {
      const data = await startAutopilot(payload);
      set({ state: data, loading: false });
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  },
  async stop() {
    set({ loading: true, error: undefined });
    try {
      const data = await stopAutopilot();
      set({ state: data, loading: false });
    } catch (err) {
      set({ loading: false, error: (err as Error).message });
    }
  },
  updateFromWs(payload) {
    set({ state: payload });
  }
}));
