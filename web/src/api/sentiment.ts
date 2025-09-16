import { api, type ApiResponse } from "./client"

export type SentimentResponse = {
  label: string
  score: number
  tokens: number
}

export const aggregateSentiment = async (text: string) => {
  const res = await api
    .post("api/sentiment/aggregate", { json: { text } })
    .json<ApiResponse<SentimentResponse>>()
  return res.data
}
