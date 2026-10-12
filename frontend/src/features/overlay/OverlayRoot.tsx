import { DEFAULT_TOGGLE_HOTKEY } from '../../app/config/shortcuts'
import { Portal } from '../../shared/components/Portal'
import { ChatOverlay } from '../chat/components/ChatOverlay'
import { useGlobalHotkey } from './useGlobalHotkey'
import { useOverlayVisibility } from './useOverlayVisibility'

export function OverlayRoot() {
  const { isOpen, toggle } = useOverlayVisibility(true)

  useGlobalHotkey(DEFAULT_TOGGLE_HOTKEY, toggle)

  if (!isOpen) return null

  return (
    <Portal>
      <ChatOverlay onClose={toggle} />
    </Portal>
  )
}
