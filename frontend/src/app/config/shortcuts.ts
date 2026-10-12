export type Hotkey = {
  key: string
  ctrl?: boolean
  shift?: boolean
  alt?: boolean
  meta?: boolean
}

export const DEFAULT_TOGGLE_HOTKEY: Hotkey = { key: ' ', ctrl: true }
