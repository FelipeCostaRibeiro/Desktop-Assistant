import { useRef, type CSSProperties } from 'react'
import { useDragPosition } from '../../overlay/useDragPosition'
import { useChatController } from '../hooks/useChatController'
import { ChatBubble } from './ChatBubble'
import { ChatInput } from './ChatInput'
import { MessageList } from './MessageList'
import styles from './ChatOverlay.module.css'

type ChatOverlayProps = {
  onClose?: () => void
}

const OVERLAY_MARGIN = 24

export function ChatOverlay({ onClose }: Readonly<ChatOverlayProps>) {
  const containerRef = useRef<HTMLDivElement>(null)
  const { position, dragHandleProps } = useDragPosition(containerRef)
  const { messages, isThinking, send } = useChatController()

  const style: CSSProperties = position
    ? { transform: `translate3d(${position.x}px, ${position.y}px, 0)` }
    : {
        left: 'auto',
        top: 'auto',
        right: OVERLAY_MARGIN,
        bottom: OVERLAY_MARGIN,
      }

  return (
    <section ref={containerRef} className={styles.overlay} style={style}>
      <ChatBubble onClose={onClose} dragHandleProps={dragHandleProps}>
        <MessageList messages={messages} isThinking={isThinking} />
        <ChatInput onSend={send} disabled={isThinking} />
      </ChatBubble>
    </section>
  )
}
