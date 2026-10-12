import {
  useCallback,
  useRef,
  useState,
  type PointerEvent as ReactPointerEvent,
  type RefObject,
} from 'react'
import { useEventListener } from '../../shared/hooks/useEventListener'

type Point = { x: number; y: number }

type DragHandleProps = {
  onPointerDown: (event: ReactPointerEvent<HTMLElement>) => void
  onPointerMove: (event: ReactPointerEvent<HTMLElement>) => void
  onPointerUp: (event: ReactPointerEvent<HTMLElement>) => void
}

function clamp(value: number, min: number, max: number) {
  return Math.min(Math.max(value, min), max)
}

export function useDragPosition(
  targetRef: RefObject<HTMLElement | null>,
): { position: Point | null; dragHandleProps: DragHandleProps } {
  const [position, setPosition] = useState<Point | null>(null)
  const offsetRef = useRef<Point>({ x: 0, y: 0 })
  const draggingRef = useRef(false)

  const clampToViewport = useCallback(
    (point: Point): Point => {
      const element = targetRef.current
      if (!element) return point

      const maxX = Math.max(window.innerWidth - element.offsetWidth, 0)
      const maxY = Math.max(window.innerHeight - element.offsetHeight, 0)
      return { x: clamp(point.x, 0, maxX), y: clamp(point.y, 0, maxY) }
    },
    [targetRef],
  )

  const onPointerDown = useCallback(
    (event: ReactPointerEvent<HTMLElement>) => {
      const element = targetRef.current
      if (!element) return

      const rect = element.getBoundingClientRect()
      const origin = position ?? { x: rect.left, y: rect.top }

      draggingRef.current = true
      offsetRef.current = {
        x: event.clientX - origin.x,
        y: event.clientY - origin.y,
      }
      setPosition(origin)
      event.currentTarget.setPointerCapture(event.pointerId)
    },
    [position, targetRef],
  )

  const onPointerMove = useCallback(
    (event: ReactPointerEvent<HTMLElement>) => {
      if (!draggingRef.current) return

      setPosition(
        clampToViewport({
          x: event.clientX - offsetRef.current.x,
          y: event.clientY - offsetRef.current.y,
        }),
      )
    },
    [clampToViewport],
  )

  const onPointerUp = useCallback((event: ReactPointerEvent<HTMLElement>) => {
    draggingRef.current = false
    if (event.currentTarget.hasPointerCapture(event.pointerId)) {
      event.currentTarget.releasePointerCapture(event.pointerId)
    }
  }, [])

  useEventListener('resize', () => {
    setPosition((previous) => (previous ? clampToViewport(previous) : previous))
  })

  return {
    position,
    dragHandleProps: { onPointerDown, onPointerMove, onPointerUp },
  }
}
