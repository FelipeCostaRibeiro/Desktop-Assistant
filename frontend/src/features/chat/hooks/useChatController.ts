import { useCallback, useState } from 'react'
import type { ChatMessage } from '../types'

const INITIAL_MESSAGES: ChatMessage[] = [
  {
    id: 'seed',
    role: 'assistant',
    content: 'Oi! Sou seu assistente. Pergunte alguma coisa para começar.',
    createdAt: Date.now(),
  },
]

export function useChatController() {
  const [messages, setMessages] = useState<ChatMessage[]>(INITIAL_MESSAGES)
  const [isThinking, setIsThinking] = useState(false)

  const send = useCallback((content: string) => {
    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
      createdAt: Date.now(),
    }

    setMessages((previous) => [...previous, userMessage])
    setIsThinking(true)

    window.setTimeout(() => {
      setMessages((previous) => [
        ...previous,
        {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: `(visual) Você disse: "${content}"`,
          createdAt: Date.now(),
        },
      ])
      setIsThinking(false)
    }, 900)
  }, [])

  return { messages, isThinking, send }
}
