import type { ChatMessage } from '../types'
import styles from './MessageItem.module.css'

type MessageItemProps = {
  message: ChatMessage
}

export function MessageItem({ message }: MessageItemProps) {
  const isUser = message.role === 'user'

  return (
    <div className={isUser ? `${styles.row} ${styles.user}` : styles.row}>
      <div className={styles.bubble}>{message.content}</div>
    </div>
  )
}
