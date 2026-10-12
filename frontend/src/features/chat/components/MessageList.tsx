import { useAutoScroll } from '../hooks/useAutoScroll'
import type { ChatMessage } from '../types'
import { MessageItem } from './MessageItem'
import styles from './MessageList.module.css'

type MessageListProps = {
  messages: ChatMessage[]
  isThinking: boolean
}

export function MessageList({
  messages,
  isThinking,
}: Readonly<MessageListProps>) {
  const endRef = useAutoScroll(messages.length + (isThinking ? 1 : 0))

  return (
    <div className={styles.list}>
      {messages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}

      {isThinking && (
        <div className={styles.typing} aria-label="Pensando">
          <span />
          <span />
          <span />
        </div>
      )}

      <div ref={endRef} />
    </div>
  )
}
