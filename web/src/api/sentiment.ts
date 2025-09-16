import { api, unwrap } from "./client";

export async function aggregateSentiment(texts: string[]) {
  return unwrap(api.post("api/sentiment/aggregate", { json: { texts } }).json());
}
