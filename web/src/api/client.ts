import ky from "ky"

const API_BASE = import.meta.env.VITE_API_BASE ?? "http://localhost:8000"

export const api = ky.create({
  prefixUrl: API_BASE,
  hooks: {
    afterResponse: [
      async (_request, _options, response) => {
        if (!response.ok) {
          const data = await response.json().catch(() => null)
          throw new Error(data?.error?.message ?? "API request failed")
        }
      },
    ],
  },
})

export type ApiResponse<T> = {
  ok: boolean
  data: T
  request_id: string
  meta: { ts: string }
  error?: { code: string; message: string; hint?: string }
}
