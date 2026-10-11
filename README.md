<div align="center">

# 🖥️ Desktop Assistant

**Assistente de IA com raciocínio adaptativo e execução segura de comandos no terminal.**

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow?style=for-the-badge)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)

</div>

---

## 📌 Sobre o projeto

O **Desktop Assistant** é um assistente de IA pensado para rodar no desktop e ajudar o usuário em tarefas do dia a dia, inclusive executando comandos no terminal por conta própria, com camadas de segurança.

O projeto é dividido em duas partes:

- **Backend (Python):** orquestra a comunicação com os modelos de linguagem, decide quanto "esforço de raciocínio" cada mensagem exige e executa comandos de shell por meio de um agente com ferramentas (*tool calling*).
- **Frontend (React + TypeScript):** interface de chat, construída com Vite.

---

## ✨ Funcionalidades

- 🧠 **Raciocínio adaptativo:** cada mensagem é classificada em quatro níveis de complexidade (`reasoning_off`, `reasoning_low`, `reasoning_high` e `reasoning_max`). O nível escolhido define os parâmetros de raciocínio da resposta, equilibrando custo, velocidade e qualidade.
- 🤖 **Agente com *tool calling*:** o modelo pode chamar uma ferramenta de terminal (`run_terminal_command`) em um laço de até 8 passos, usando o resultado de cada comando para decidir o próximo passo.
- ⚡ **Respostas em *streaming*:** a resposta é entregue em tempo real, token a token, de forma assíncrona.
- 🛡️ **Política de segurança para o terminal:**
  - Detecta comandos potencialmente destrutivos (`rm -r`, `sudo`, `git push --force`, `git reset --hard`, `format`, `dd`, `shutdown`, entre outros) e **exige confirmação do usuário**.
  - Bloqueia a execução fora do diretório de trabalho permitido.
  - Aplica *timeout* por comando e trunca saídas muito longas.
- 🪟🐧 **Multiplataforma:** usa `PowerShell` no Windows e `/bin/sh` em Linux/macOS.
- 💬 **Gerenciamento de contexto:** mantém uma janela das mensagens mais recentes do histórico para controlar o consumo de tokens.
- 🔌 **Acesso a vários modelos via OpenRouter:** modelo de chat e modelo de *embeddings* configuráveis em um único lugar.

---

## 🛠️ Tecnologias utilizadas

### Backend

<p>
  <img src="https://skillicons.dev/icons?i=python" alt="Python" height="48" />
</p>

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

## 🧩 Arquitetura

```
Desktop-Assistant/
├── backend/
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── api/
│       │   └── routes_chat.py
│       ├── db/
│       │   └── database.py
│       └── services/
│           ├── terminal_policy.py      # Regras de segurança e confirmação de comandos
│           ├── terminal_service.py     # Execução assíncrona de comandos (sessão de terminal)
│           └── ai_agent/
│               ├── models.py           # Clientes, modelos e definição das tools
│               └── orchestrator.py     # Classificação de raciocínio, streaming e laço do agente
└── frontend/
    ├── index.html
    ├── package.json
    ├── vite.config.ts
    └── src/
        ├── main.tsx
        └── App.tsx
```

### Como funciona o fluxo do agente

1. O usuário envia uma mensagem.
2. Um classificador (via *function calling*) define o nível de raciocínio necessário.
3. O modelo responde com os parâmetros de raciocínio correspondentes, em streaming ou em modo agente.
4. No modo agente, o modelo pode solicitar comandos de terminal, que passam pela **política de segurança** antes de serem executados.
5. O resultado do comando (status, `exit_code`, `stdout` e `stderr`) volta ao modelo, que decide o próximo passo ou entrega a resposta final.

---

### Diagrama conceitural 
Diagrama conceitual do backend, organizado nas camadas do ciclo percepção, decisão e ação. Linhas contínuas existem no código hoje. Linhas tracejadas são planejadas.

<img width="2080" height="3292" alt="Arquitetura_Desktop_Assistant2" src="https://github.com/user-attachments/assets/3d2c2d13-b80e-4052-a9fd-c09f52c1af78" />

## 🚀 Como executar

### Pré-requisitos

- [Python 3.11+](https://www.python.org/downloads/)
- [Node.js](https://nodejs.org/) e npm
- Uma chave de API do [OpenRouter](https://openrouter.ai/)

### Backend

```bash
cd backend

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.venv\Scripts\activate           # Windows

# Instale as dependências
pip install -r requirements.txt
```

Crie um arquivo `.env` dentro de `backend/` com a sua chave:

```env
OPENROUTER_API_KEY=sua_chave_aqui
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

A aplicação ficará disponível em `http://localhost:5173`.

---

## 🗺️ Roadmap

- [x] Classificação automática do nível de raciocínio
- [x] Respostas em streaming
- [x] Agente com ferramenta de terminal
- [x] Política de segurança e confirmação de comandos destrutivos
- [ ] API de chat (rotas e ponto de entrada do servidor)
- [ ] Persistência do histórico de conversas
- [ ] Interface de chat no frontend
- [ ] Busca semântica com *embeddings*
- [ ] Empacotamento como aplicativo desktop

---

## 👨‍💻 Autor

**Felipe Costa Ribeiro**

[![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)](https://github.com/FelipeCostaRibeiro)

---
