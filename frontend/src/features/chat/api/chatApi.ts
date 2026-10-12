import { API_BASE_URL } from '../../../app/config/env'
import type { ChatMessage } from '../types'

type ChatResponse = {
  reply: string
}

export async function sendChatMessage(
  message: string,
  history: ChatMessage[],
): Promise<string> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      message,
      history: history.map((item) => ({
        role: item.role,
        content: item.content,
      })),
    }),
  })

  if (!response.ok) {
    throw new Error(`Chat request failed with status ${response.status}`)
  }

  const data = (await response.json()) as ChatResponse
  return data.reply
}
