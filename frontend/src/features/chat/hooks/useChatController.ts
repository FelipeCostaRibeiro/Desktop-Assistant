import { useCallback, useEffect, useState } from 'react'
import { readJson, writeJson } from '../../../shared/lib/storage'
import { sendChatMessage } from '../api/chatApi'
import type { ChatMessage } from '../types'

const STORAGE_KEY = 'desktop-assistant:chat-history'

const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: 'seed',
    role: 'assistant',
    content: 'Oi! Sou seu assistente. Pergunte alguma coisa para começar.',
    createdAt: Date.now(),
  },
]

const ERROR_REPLY =
  'Não consegui falar com o assistente agora. Verifique a conexão e tente novamente.'

function isChatMessage(value: unknown): value is ChatMessage {
  if (typeof value !== 'object' || value === null) return false
  const candidate = value as Record<string, unknown>
  return (
    typeof candidate.id === 'string' &&
    (candidate.role === 'user' || candidate.role === 'assistant') &&
    typeof candidate.content === 'string' &&
    typeof candidate.createdAt === 'number'
  )
}

function loadMessages(): ChatMessage[] {
  const stored = readJson<unknown>(STORAGE_KEY, null)
  if (!Array.isArray(stored)) return INITIAL_MESSAGES
  const messages = stored.filter(isChatMessage)
  return messages.length > 0 ? messages : INITIAL_MESSAGES
}

export function useChatController() {
  const [messages, setMessages] = useState<ChatMessage[]>(loadMessages)
  const [isThinking, setIsThinking] = useState(false)

  useEffect(() => {
    writeJson(STORAGE_KEY, messages)
  }, [messages])

  const send = useCallback(
    async (content: string) => {
      const history = messages
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content,
        createdAt: Date.now(),
      }

      setMessages([...history, userMessage])
      setIsThinking(true)

      try {
        const reply = await sendChatMessage(content, history)
        setMessages((previous) => [
          ...previous,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: reply,
            createdAt: Date.now(),
          },
        ])
      } catch {
        setMessages((previous) => [
          ...previous,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: ERROR_REPLY,
            createdAt: Date.now(),
          },
        ])
      } finally {
        setIsThinking(false)
      }
    },
    [messages],
  )

  return { messages, isThinking, send }
}
