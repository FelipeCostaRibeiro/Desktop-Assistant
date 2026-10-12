# 🐍 Backend — DeskAI Chatbot

**[← Voltar ao README principal](../README.md)**

API e núcleo de IA do DeskAI Chatbot: orquestra os modelos de linguagem, classifica o esforço de raciocínio de cada mensagem e executa comandos de shell por meio de um agente com ferramentas, sob uma política de segurança.

> **Legenda de estado:** 📘 Implementado · 📐 Planejado · 🔒 Segurança.

---

## 🧰 Stack

<p>
  <img src="https://skillicons.dev/icons?i=python,fastapi" alt="Python, FastAPI" height="48" />
</p>

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-4051B5?style=for-the-badge&logoColor=white)
![OpenAI SDK](https://img.shields.io/badge/OpenAI%20SDK-412991?style=for-the-badge&logo=openai&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![OpenRouter](https://img.shields.io/badge/OpenRouter-6467F2?style=for-the-badge&logo=openrouter&logoColor=white)

- **Python 3.12+**
- **FastAPI + Uvicorn** — API HTTP e servidor ASGI.
- **OpenAI SDK (async)** — cliente dos modelos via OpenRouter.
- **LangChain OpenAI** — modelo de *embeddings* (configurado, ainda sem uso).
- **Pydantic** — validação de entrada/saída.
- **python-dotenv** — carregamento do `.env`.

---

## 📂 Estrutura

```
backend/
├── pyproject.toml            # Dependências, build e task "poe backend"
└── app/
    ├── main.py               # create_app(): instancia FastAPI, CORS e registra rotas
    ├── api/
    │   └── routes_chat.py    # POST /chat: valida a requisição e chama o orquestrador
    ├── db/
    │   └── database.py       # 📐 persistência de histórico (ainda vazio)
    └── services/
        ├── terminal_policy.py   # 🔒 evaluate(): padrões destrutivos + jail de diretório
        ├── terminal_service.py  # TerminalSession, CommandResult, timeout e truncamento
        └── ai_agent/
            ├── models.py        # Cliente OpenRouter, embeddings e definição das tools
            └── orchestrator.py  # Classificação, respostas diretas/streaming e laço do agente
```

---

## 🔄 Fluxo de uma requisição

```
HTTP POST /chat
      │
      ▼
api/routes_chat.py ── build_messages() ──► system prompt + histórico + mensagem
      │
      ▼
orchestrator.generate_answer(messages)
      │
      ├── classify(messages)  ── força tool call "classify_reasoning" ──► nível de raciocínio
      │
      ▼
get_client().chat.completions.create(..., extra_body={"reasoning": ...})
      │
      ▼
ChatResponse { reply }
```

O router monta a lista de mensagens (`build_messages`) com o prompt de sistema (`SYSTEM_PROMPT`), o histórico recebido e a nova mensagem, e delega ao orquestrador. Falhas na chamada da LLM viram `HTTPException 502`.

---

## 🧠 Raciocínio adaptativo

Antes de responder, o orquestrador classifica a mensagem em um dos quatro níveis (`orchestrator.classify`), usando *function calling* forçado sobre a tool `classify_reasoning` (definida em `models.CLASSIFICATION_TOOL`). O nível escolhido define os parâmetros enviados ao modelo via `extra_body`:

| Nível | Parâmetros (`REASONING_PARAMS`) |
| --- | --- |
| `reasoning_off` | `enabled: false` |
| `reasoning_low` | `effort: "low"` |
| `reasoning_high` | `effort: "high"` |
| `reasoning_max` | `effort: "high"`, `max_tokens: 32000` |

A decisão usa os **últimos 5 turnos de conversa** (`CLASSIFY_WINDOW`). Sem *tool call* na resposta, o padrão é `reasoning_off`.

**Janela de contexto** — `prepare_message()` mantém sempre o prompt de sistema e as **últimas 15 mensagens** (`MAX_HISTORY_CONTEXT`) para controlar o consumo de tokens.

---

## 🤖 Respostas e agente

O orquestrador expõe três caminhos:

- 📘 `generate_answer(messages)` — resposta simples, sem ferramentas (usada hoje pela rota `/chat`).
- 📘 `generate_answer_stream(messages)` — mesma resposta em *streaming*, token a token. **Ainda sem rota que a exponha.**
- 📘 `run_agent(messages, session, confirmer, max_steps=8)` — laço do agente com *tool calling* (`MAX_AGENT_STEPS`). **Ainda sem rota que o exponha.**

### Ciclo do agente

```
estado + objetivo → LLM escolhe ação → tool call → observação (resultado) → nova decisão → resposta final
```

Em cada passo o modelo recebe o histórico da trajetória e as ferramentas disponíveis. Se não houver *tool call*, o conteúdo é a resposta final. Se houver, cada chamada é executada e o resultado volta como mensagem `tool`, alimentando a próxima decisão. Ao atingir o limite de passos, retorna um aviso de limite atingido.

A ferramenta `run_terminal_command` (`models.TERMINAL_TOOL`) recebe `command` e `timeout_seconds`, e a execução é delegada à `TerminalSession` (ver abaixo).

---

## 🔒 Segurança e execução

Nada é executado no terminal sem passar pela política:

- **`terminal_policy.evaluate(command, cwd, root)`** — verifica o diretório de trabalho (bloqueia caminhos fora da raiz) e procura padrões destrutivos (`DESTRUCTIVE_PATTERNS`): `rm -r`, `Remove-Item -Recurse/-Force`, `format`, `mkfs`, `dd of=`, `shutdown`/`reboot`, fork bomb, `sudo`, `git push --force`, `git reset --hard`, `git clean` destrutivo, escrita direta em disco, `chmod -R 777`, pipe remoto para shell, entre outros. Retorna um `PolicyDecision` com `allowed` / `requires_confirmation` / `reason`.
- **Confirmação humana (`confirmer`)** — comandos marcados como de risco só rodam se o `confirmer` aprovar. Sem confirmação configurada, o padrão nega tudo (`_deny_all`).
- **`TerminalSession`** — executa o comando em `PowerShell` (Windows) ou `/bin/sh` (demais sistemas), com `timeout` por comando (padrão 30s), saída truncada em 20.000 caracteres e histórico de comandos. Retorna um `CommandResult`, serializado para o modelo por `to_tool_content()`.

### Resultados possíveis

| Resultado | Quando acontece |
| --- | --- |
| `ok` | Comando executou (inclui `exit_code`) |
| `blocked` | Diretório fora da raiz permitida |
| `denied` | Usuário negou a confirmação |
| `timeout` | Passou do tempo limite; processo encerrado |
| `error` | Falha ao iniciar o processo |

---

## 🔌 Endpoints

| Método | Rota | Estado | Descrição |
| --- | --- | --- | --- |
| `POST` | `/chat` | 📘 | Recebe `message` e `history`, retorna `{ "reply": string }` |
| `POST` | `/chat/stream` | 📐 | Resposta em *streaming* (usa `generate_answer_stream`) |
| `POST` | `/agent` | 📐 | Execução do agente de terminal com confirmação |
| `WS` | `/ws` | 📐 | Mensagens, streaming e pedidos de confirmação |

### `POST /chat`

**Requisição**

```json
{
  "message": "Olá, tudo bem?",
  "history": [
    { "role": "user", "content": "Oi" },
    { "role": "assistant", "content": "Olá!" }
  ]
}
```

**Resposta**

```json
{ "reply": "Tudo ótimo! Como posso ajudar?" }
```

---

## ⚙️ Configuração

Crie um arquivo `.env` dentro de `backend/`:

```env
OPENROUTER_API_KEY=sua_chave_aqui
# Opcional (padrão: http://localhost:5173)
CORS_ORIGINS=http://localhost:5173
```

Modelos e *endpoint* (em `app/services/ai_agent/models.py`):

| Constante | Valor |
| --- | --- |
| `MODEL_CHAT` | `deepseek/deepseek-v4.1-flash` |
| `MODEL_EMBEDDING` | `openai/text-embedding-3-small` |
| `OPENROUTER_BASE_URL` | `https://openrouter.ai/api/v1` |

---

## ▶️ Como executar

```bash
cd backend

python -m venv .venv
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # Linux/macOS

pip install -e .

# Sobe a API com reload na porta 8000
poe backend
```

A API fica em `http://localhost:8000`. A tarefa `poe backend` está definida em `pyproject.toml` (`[tool.poe.tasks]`) e executa `uvicorn app.main:app --reload --port 8000`.

---

## 📐 Planejado

- Sessão de conversa e recepção de imagem na rota de chat.
- Persistência do histórico em banco (`app/db/database.py`).
- Memória de longo prazo e busca semântica com *embeddings* (`get_embeddings_model` já configurado, ainda sem uso).
- Ferramenta de busca/consulta web.
- Exposição de *streaming*, agente e WebSocket via API.
