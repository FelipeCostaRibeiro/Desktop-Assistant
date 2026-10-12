import { OverlayRoot } from './features/overlay/OverlayRoot'

function App() {
  return (
    <main className="app-shell">
      <p className="app-hint">
        Pressione <kbd>Ctrl</kbd> + <kbd>Espaço</kbd> para mostrar ou esconder o
        assistente.
      </p>
      <OverlayRoot />
    </main>
  )
}

export default App
