import { create } from "zustand"

interface WebSocketState {
  socket?: WebSocket
  channel: string
  messages: any[]
  connect: (channel: string) => void
  disconnect: () => void
}

export const useWsStore = create<WebSocketState>((set, get) => ({
  socket: undefined,
  channel: "orders",
  messages: [],
  connect: (channel: string) => {
    const wsUrl = (import.meta.env.VITE_WS_BASE ?? "ws://localhost:8000") + `/ws?channel=${channel}`
    const socket = new WebSocket(wsUrl)
    socket.onmessage = (event) => {
      const payload = JSON.parse(event.data)
      set((state) => ({ messages: [...state.messages.slice(-49), payload] }))
    }
    socket.onopen = () => set({ channel, socket })
    socket.onclose = () => set({ socket: undefined })
  },
  disconnect: () => {
    const current = get().socket
    current?.close()
    set({ socket: undefined })
  },
}))
