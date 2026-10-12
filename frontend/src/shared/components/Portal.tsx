import type { ReactNode } from 'react'
import { createPortal } from 'react-dom'

type PortalProps = {
  children: ReactNode
  container?: HTMLElement | null
}

export function Portal({ children, container }: PortalProps) {
  const target = container ?? (typeof document !== 'undefined' ? document.body : null)

  if (!target) return null

  return createPortal(children, target)
}
