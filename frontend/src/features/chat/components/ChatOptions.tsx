import type { ChatPreferences } from '../types'
import styles from './ChatOptions.module.css'

type ChatOptionsProps = {
  preferences: ChatPreferences
  onChange: (preferences: ChatPreferences) => void
}

export function ChatOptions({ preferences, onChange }: ChatOptionsProps) {
  return (
    <div className={styles.bar}>
      <button
        type="button"
        className={styles.chip}
        aria-pressed={preferences.compact}
        onClick={() =>
          onChange({ ...preferences, compact: !preferences.compact })
        }
      >
        Compacto
      </button>

      <button
        type="button"
        className={styles.chip}
        aria-pressed={preferences.showTimestamps}
        onClick={() =>
          onChange({
            ...preferences,
            showTimestamps: !preferences.showTimestamps,
          })
        }
      >
        Horário
      </button>
    </div>
  )
}
