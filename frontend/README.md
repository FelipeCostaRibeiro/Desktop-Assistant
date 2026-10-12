# ⚛️ Frontend — DeskAI Chatbot

**[← Voltar ao README principal](../README.md)**

Interface do DeskAI Chatbot: um overlay de chat flutuante, arrastável e acionado por atalho global, construído em **React 19 + TypeScript + Vite**.

> **Legenda de estado:** 📘 Implementado · 📐 Planejado.

---

## 🧰 Stack

<p>
  <img src="https://skillicons.dev/icons?i=react,ts,vite,nodejs,npm" alt="React, TypeScript, Vite, Node, npm" height="48" />
</p>

![React](https://img.shields.io/badge/React%2019-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Oxlint](https://img.shields.io/badge/Oxlint-1E1E2E?style=for-the-badge&logoColor=white)

- **React 19** + **TypeScript** — biblioteca e tipagem.
- **Vite** — dev server, build e HMR.
- **CSS Modules** — estilos escopados por componente.
- **Oxlint** — lint rápido.

---

## 📂 Estrutura

O código é organizado por **camadas** e por **feature** (*feature-first*): cada feature agrupa seus próprios `components`, `hooks`, `api` e `state`; o que é reutilizável vai para `shared/`; composição e configuração ficam em `app/`.

```
src/
├── main.tsx / App.tsx        # bootstrap e composição da raiz
├── app/
│   ├── config/
│   │   ├── env.ts            # API_BASE_URL (VITE_API_URL)
│   │   └── shortcuts.ts      # tipo Hotkey + atalho padrão
│   └── providers/            # 📐 AppProviders / ThemeProvider (stubs vazios)
├── features/
│   ├── chat/
│   │   ├── api/chatApi.ts        # sendChatMessage() → POST /chat
│   │   ├── components/           # ChatBubble, ChatInput, ChatOverlay, MessageItem,
│   │   │                         #   MessageList, ChatOptions (+ .module.css)
│   │   ├── hooks/                # useChatController, useAutoScroll
│   │   │                         # 📐 useChatStream (stub)
│   │   ├── state/                # 📐 chatStore / chatReducer (stubs)
│   │   ├── types.ts              # ChatMessage, ChatRole, ChatPreferences
│   │   └── index.ts              # barrel da feature
│   ├── overlay/
│   │   ├── OverlayRoot.tsx       # ponto de entrada do overlay
│   │   ├── useGlobalHotkey.ts    # atalho global de abrir/fechar
│   │   ├── useOverlayVisibility.ts
│   │   └── useDragPosition.ts    # arrasto com clamp na viewport
│   └── settings/                 # 📐 SettingsPanel, settingsStore, types
└── shared/
    ├── components/           # IconButton, Portal, Spinner
    ├── hooks/useEventListener.ts
    ├── lib/                  # storage.ts (localStorage JSON), classNames.ts
    │                         # 📐 http.ts (stub)
    └── styles/               # tokens.css, globals.css
```

---

## 🧱 Princípios de arquitetura

- **Feature-first.** `chat`, `overlay` e `settings` são features independentes; cada uma concentra sua API, seus componentes, hooks e estado.
- **Camada `shared/`.** Componentes, hooks e utilitários genéricos reutilizáveis, sem regra de negócio.
- **Camada `app/`.** Configuração transversal (variáveis de ambiente, atalhos) e providers globais.
- **Sem biblioteca de UI/estado externa.** O estado do chat é local (`useState`) e persistido em `localStorage`; não há Redux/Zustand nem CSS de terceiros.

---

## 🔄 Fluxo da UI

```
main.tsx
  └─ <App>
       └─ <OverlayRoot>            useOverlayVisibility(true) — aberto por padrão
            │                       useGlobalHotkey(Ctrl+Espaço) — alterna visibilidade
            └─ <Portal>             renderiza fora da árvore principal
                 └─ <ChatOverlay>   useDragPosition(ref)
                      └─ <ChatBubble>        header + área de mensagens + handle de arrasto
                           ├─ <MessageList>  lista + indicador "Pensando" + auto-scroll
                           │    └─ <MessageItem>
                           └─ <ChatInput>    textarea + enviar (Enter envia, Shift+Enter quebra linha)
```

- **Atalho global:** `Ctrl + Espaço` mostra/esconde o overlay (`app/config/shortcuts.ts`).
- **Arrasto:** o overlay pode ser movido pelo *handle* inferior e fica limitado à viewport.
- **Auto-scroll:** `useAutoScroll` mantém a última mensagem visível conforme chegam novas.

---

## 🎨 UI / Design

Guia de estilos da interface: paleta de cores (tokens), átomos, moléculas e telas (claro e escuro).

<img width="2880" height="2364" alt="Guia de estilos do DeskAI Chatbot" src="https://github.com/user-attachments/assets/3969e0c1-e8e4-40fb-82e2-32588273d918" />

**Paleta de cores** (valores claro; variáveis em `src/shared/styles/tokens.css`, com sobrescritas para o tema escuro via `prefers-color-scheme: dark`):

| Token (design) | Variável CSS | Valor |
| --- | --- | --- |
| `accent` | `--da-color-accent` | `#3ab7ed` |
| `accent-soft` | `--da-color-accent-soft` | `rgba(58, 183, 237, .14)` |
| `user` | `--da-color-user` | `#3ab7ed` |
| `surface` | `--da-color-surface` | `#ffffff` |
| `surface-2` | `--da-color-surface-2` | `#f5f4f8` |
| `assistant` | `--da-color-assistant` | `#f1f0f5` |
| `text` | `--da-color-text` | `#1b1a22` |
| `text-muted` | `--da-color-text-muted` | `#6b6375` |
| `border` | `--da-color-border` | `#e5e4e7` |

**Composição (Atomic Design):**

- **Atoms** — barra de arrasto, bolha de mensagem (assistente/usuário), campo de entrada, botão de enviar, botão fechar e indicador "Assistente".
- **Molecules** — painel do `ChatBubble`, barra de entrada (`ChatInput`) e par de mensagens.
- **Screens** — overlay completo nos temas claro e escuro.

---

## 💬 Feature `chat`

- **`useChatController`** — controla a conversa: estado local das mensagens, mensagem-semente inicial, indicador de "pensando", persistência em `localStorage` (chave `desktop-assistant:chat-history`) e tratamento de erro de rede (resposta amigável em caso de falha).
- **`chatApi.sendChatMessage(message, history)`** — faz `POST ${API_BASE_URL}/chat` com `message` e `history` (`{ role, content }`) e retorna `reply`. Hoje é uma requisição HTTP simples, **sem streaming**.
- **Componentes:** `ChatBubble` (moldura/painel), `MessageList` + `MessageItem` (mensagens), `ChatInput` (entrada) e `ChatOptions`.
- **Tipos:** `ChatMessage`, `ChatRole` e `ChatPreferences` em `features/chat/types.ts`.

---

## 🪟 Feature `overlay`

- **`useOverlayVisibility`** — estado de aberto/fechado com `open` / `close` / `toggle`.
- **`useGlobalHotkey(hotkey, handler)`** — escuta `keydown` global e dispara o handler quando o atalho casa.
- **`useDragPosition(targetRef)`** — posição do overlay com arrasto via *pointer events* e *clamp* nas bordas da tela.

---

## ⚙️ Configuração

A URL da API vem da variável de ambiente do Vite:

```ts
// src/app/config/env.ts
export const API_BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'
```

Para apontar para outro backend, crie um `.env` no `frontend/`:

```env
VITE_API_URL=http://localhost:8000
```

---

## ▶️ Como executar

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

Outros scripts:

| Script | Descrição |
| --- | --- |
| `npm run dev` | Dev server com HMR |
| `npm run build` | Type-check (`tsc -b`) + build de produção |
| `npm run preview` | Pré-visualiza o build |
| `npm run lint` | Executa o Oxlint |

---

## 📐 Planejado

- **Captura de tela / anexo de imagem** ao pedido.
- **Diálogo de confirmação** para aprovar ou negar comandos de risco.
- **Transporte WebSocket** para mensagens, streaming e pedidos de confirmação (hoje é `fetch` HTTP simples).
- **Streaming** da resposta no chat (`useChatStream`, hoje stub).
- **Providers globais** (`AppProviders`, `ThemeProvider`) e **painel de configurações** (`SettingsPanel`/`settingsStore`, hoje stubs).
- **Camada de estado dedicada** (`chatStore`/`chatReducer`, hoje stubs) e utilitário HTTP compartilhado (`shared/lib/http.ts`, hoje stub).
