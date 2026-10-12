<div align="center">

# 🖥️ DeskAI Chatbot

**Assistente de IA com raciocínio adaptativo e execução segura de comandos no terminal, para ajudar a realizar tarefas e comandos no ambiente desktop**

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow?style=for-the-badge)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)

</div>

---

## 📌 Sobre o projeto

O **DeskAI Chatbot** é um assistente de IA pensado para rodar no desktop e ajudar o usuário em tarefas do dia a dia, inclusive executando comandos no terminal por conta própria, com camadas de segurança.

O projeto é dividido em duas partes, cada uma com documentação de arquitetura própria:

- **[Backend (Python)](./backend/README.md):** orquestra a comunicação com os modelos de linguagem, decide quanto "esforço de raciocínio" cada mensagem exige e executa comandos de shell por meio de um agente com ferramentas (*tool calling*).
- **[Frontend (React + TypeScript)](./frontend/README.md):** interface de chat em formato de overlay, construída com Vite.

---

## ✨ Funcionalidades

- 🧠 **Raciocínio adaptativo:** cada mensagem é classificada em quatro níveis de complexidade (`reasoning_off`, `reasoning_low`, `reasoning_high` e `reasoning_max`). O nível escolhido define os parâmetros de raciocínio da resposta, equilibrando custo, velocidade e qualidade.
- 🤖 **Agente com *tool calling*:** o modelo pode chamar uma ferramenta de terminal (`run_terminal_command`) em um laço de até 8 passos, usando o resultado de cada comando para decidir o próximo passo.
- ⚡ **Respostas diretas e com *streaming*:** o orquestrador oferece resposta simples e resposta em tempo real, token a token.
- 🛡️ **Política de segurança para o terminal:**
  - Detecta comandos potencialmente destrutivos (`rm -r`, `sudo`, `git push --force`, `git reset --hard`, `format`, `dd`, `shutdown`, entre outros) e **exige confirmação do usuário**.
  - Bloqueia a execução fora do diretório de trabalho permitido.
  - Aplica *timeout* por comando e trunca saídas muito longas.
- 🪟🐧 **Multiplataforma:** usa `PowerShell` no Windows e `/bin/sh` em Linux/macOS.
- 💬 **Gerenciamento de contexto:** mantém uma janela das mensagens mais recentes do histórico para controlar o consumo de tokens.
- 🔌 **Acesso a vários modelos via OpenRouter:** modelo de chat e modelo de *embeddings* configuráveis em um único lugar.
- 🖼️ **Captura de tela / imagem:** anexar o que está na tela ao pedido.
- 💾 **Persistência e memória:** histórico de conversas em banco, preferências de longo prazo e busca semântica com *embeddings*.
- 🔗 **WebSocket:** mensagens, streaming e pedidos de confirmação em tempo real.

---

## 🛠️ Tecnologias utilizadas

### Backend

<p>
  <img src="https://skillicons.dev/icons?i=python" alt="Python" height="48" />
</p>

![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![OpenAI SDK](https://img.shields.io/badge/OpenAI%20SDK-412991?style=for-the-badge&logo=openai&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![OpenRouter](https://img.shields.io/badge/OpenRouter-6467F2?style=for-the-badge&logo=openrouter&logoColor=white)
![HTTPX](https://img.shields.io/badge/HTTPX-0A0A0A?style=for-the-badge&logoColor=white)

### Frontend

<p>
  <img src="https://skillicons.dev/icons?i=react,ts,vite,nodejs,npm" alt="Frontend" height="48" />
</p>

![React](https://img.shields.io/badge/React%2019-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Oxlint](https://img.shields.io/badge/Oxlint-1E1E2E?style=for-the-badge&logoColor=white)

### Ferramentas

<p>
  <img src="https://skillicons.dev/icons?i=git,github,vscode" alt="Ferramentas" height="48" />
</p>

---

## 🧩 Arquitetura (visão geral)

Diagrama conceitual do backend, organizado nas camadas do ciclo percepção, decisão e ação.

Linhas contínuas existem no código hoje. Linhas tracejadas são planejadas. Os itens destacados em vermelho são as camadas de segurança.

<img width="2080" height="3292" alt="Arquitetura do DeskAI Chatbot" src="https://github.com/user-attachments/assets/3d2c2d13-b80e-4052-a9fd-c09f52c1af78" />

**Fluxo resumido do agente:**

1. O usuário envia uma mensagem pela interface.
2. Um classificador (via *function calling*) define o nível de raciocínio necessário.
3. O modelo responde com os parâmetros de raciocínio correspondentes, em streaming ou em modo agente.
4. No modo agente, o modelo pode solicitar comandos de terminal, que passam pela **política de segurança** antes de serem executados.
5. O resultado do comando (status, `exit_code`, `stdout` e `stderr`) volta ao modelo, que decide o próximo passo ou entrega a resposta final.

Detalhes de implementação em **[backend/README.md](./backend/README.md)** e **[frontend/README.md](./frontend/README.md)**.

---

## 📁 Estrutura do repositório

```
DeskAI-Chatbot/
├── backend/     # API, orquestrador de IA, agente e execução de terminal
├── frontend/    # Interface de chat (overlay) em React + Vite
└── README.md
```

---

## 🚀 Como executar

### Pré-requisitos

- [Python 3.12+](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/) e npm
- Uma chave de API do [OpenRouter](https://openrouter.ai/)

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # Linux/macOS
pip install -e .
poe backend                      # sobe a API em http://localhost:8000
```

Crie `backend/.env` com `OPENROUTER_API_KEY=sua_chave_aqui`. Passo a passo completo em **[backend/README.md](./backend/README.md)**.

### Frontend

```bash
cd frontend
npm install
npm run dev                      # http://localhost:5173
```

Detalhes e variáveis de ambiente em **[frontend/README.md](./frontend/README.md)**.

---

## 🗺️ Roadmap

- [x] Classificação automática do nível de raciocínio
- [x] Respostas diretas e em *streaming* no orquestrador
- [x] Agente com ferramenta de terminal
- [x] Política de segurança e confirmação de comandos destrutivos
- [x] Sessão de terminal com *timeout* e truncamento de saída
- [ ] Expor streaming e agente via API (hoje só há `POST /chat`)
- [ ] Captura de tela / anexo de imagem
- [ ] Diálogo de confirmação de comandos no frontend
- [ ] Transporte WebSocket
- [ ] Persistência do histórico de conversas
- [ ] Memória de longo prazo e busca semântica com *embeddings*
- [ ] Empacotamento como aplicativo desktop

---

## 👨‍💻 Autor

**Felipe Costa Ribeiro**

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/FelipeCostaRibeiro)

---
