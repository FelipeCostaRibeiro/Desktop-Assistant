import type { HTMLAttributes, ReactNode } from 'react'
import styles from './ChatBubble.module.css'

type ChatBubbleProps = {
  children: ReactNode
  onClose?: () => void
  dragHandleProps?: HTMLAttributes<HTMLDivElement>
}

export function ChatBubble({ children, onClose, dragHandleProps }: ChatBubbleProps) {
  return (
    <div className={styles.bubble}>
      <header className={styles.header}>
        <div className={styles.title}>
          <span className={styles.pulse} />
          DeskAI
        </div>

        {onClose && (
          <button
            type="button"
            className={styles.close}
            onClick={onClose}
            aria-label="Fechar"
          >
            &times;
          </button>
        )}
      </header>

      <div className={styles.body}>{children}</div>

      <div
        className={styles.handle}
        aria-label="Arraste para mover"
        {...dragHandleProps}
      >
        <span className={styles.grip} />
      </div>
    </div>
  )
}
