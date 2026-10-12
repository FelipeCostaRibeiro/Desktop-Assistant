import { useCallback } from 'react'
import type { Hotkey } from '../../app/config/shortcuts'
import { useEventListener } from '../../shared/hooks/useEventListener'

export function useGlobalHotkey(hotkey: Hotkey, handler: () => void) {
  const matches = useCallback(
    (event: KeyboardEvent) => {
      if (event.key.toLowerCase() !== hotkey.key.toLowerCase()) return false
      if (Boolean(hotkey.ctrl) !== event.ctrlKey) return false
      if (Boolean(hotkey.shift) !== event.shiftKey) return false
      if (Boolean(hotkey.alt) !== event.altKey) return false
      if (Boolean(hotkey.meta) !== event.metaKey) return false
      return true
    },
    [hotkey],
  )

  const listener = useCallback(
    (event: KeyboardEvent) => {
      if (!matches(event)) return
      event.preventDefault()
      handler()
    },
    [matches, handler],
  )

  useEventListener('keydown', listener)
}
