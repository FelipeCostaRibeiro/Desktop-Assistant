import { useEffect, useRef } from 'react'

type ListenerTarget = Window | Document | HTMLElement

export function useEventListener<K extends keyof WindowEventMap>(
  type: K,
  handler: (event: WindowEventMap[K]) => void,
  target?: ListenerTarget | null,
) {
  const handlerRef = useRef(handler)

  useEffect(() => {
    handlerRef.current = handler
  }, [handler])

  useEffect(() => {
    const element: EventTarget = target ?? window
    if (!element) return

    const listener = (event: Event) => {
      handlerRef.current(event as WindowEventMap[K])
    }

    element.addEventListener(type, listener)
    return () => element.removeEventListener(type, listener)
  }, [type, target])
}
