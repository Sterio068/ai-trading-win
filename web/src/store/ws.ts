import { create } from "zustand";
import { getApiBase } from "../api/client";

type WsMessage = {
  topic: string;
  payload: unknown;
};

interface WsState {
  connected: boolean;
  messages: WsMessage[];
  connect: () => void;
}

export const useWsStore = create<WsState>((set, get) => ({
  connected: false,
  messages: [],
  connect() {
    if (get().connected) return;
    const url = new URL(getApiBase());
    const wsUrl = `${url.protocol === "https:" ? "wss" : "ws"}://${url.host}/ws`;
    const socket = new WebSocket(wsUrl);
    socket.onopen = () => set({ connected: true });
    socket.onclose = () => set({ connected: false });
    socket.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        set((state) => ({ messages: [...state.messages.slice(-50), data] }));
      } catch (err) {
        console.error("WS parse error", err);
      }
    };
  }
}));
