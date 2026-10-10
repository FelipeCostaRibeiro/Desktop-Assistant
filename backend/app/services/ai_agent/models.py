import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from openai import AsyncOpenAI
from pydantic import SecretStr

_client: AsyncOpenAI | None = None
_embeddings_model: OpenAIEmbeddings | None = None
from openai.types.chat import ChatCompletionToolParam

MODEL_CHAT = "deepseek/deepseek-v4.1-flash"
MODEL_EMBEDDING = "openai/text-embedding-3-small"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

def get_embeddings_model() -> OpenAIEmbeddings:
    global _embeddings_model
    if _embeddings_model is None:
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        _embeddings_model = OpenAIEmbeddings(
            model=MODEL_EMBEDDING,
            api_key=SecretStr(api_key) if api_key else None,
            base_url=OPENROUTER_BASE_URL,
        )
    return _embeddings_model


def get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        load_dotenv() 
        _client = AsyncOpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY"),
            base_url=OPENROUTER_BASE_URL,
        )
    return _client

CLASSIFICATION_REASONING_DESCRIPTION = (
    "Classifica a mensagem do usuário em um dos quatro níveis de raciocínio com base em "
    "QUANTAS RELAÇÕES ela exige: conectar fatos, comparar valores, encadear passos (multi-hop) "
    "ou sintetizar várias fontes. Na dúvida entre dois níveis, escolha o mais alto.\n\n"
    "reasoning_off — pedido direto, sem inferência nem combinação de informações: saudação, "
    "small talk, tradução literal, formatação, ou resposta que é um único dado já explícito no "
    "contexto. Ex.: 'Bom dia'; 'Reescreva esta frase em maiúsculas'.\n\n"
    "reasoning_low — uma única relação ou um único passo. Ex.: 'O produto X está em estoque?' "
    "(checa um fato isolado); 'Resuma este parágrafo'; 'Qual o preço do plano B?'.\n\n"
    "reasoning_high — exige relacionar 2 ou mais informações, comparação ou encadeamento "
    "(multi-hop). Ex.: 'O plano A fica mais barato que o B para 3 usuários?' (cruza preço com "
    "regra de quantidade); 'Qual arquivo menciona o autor citado no outro documento?' (liga "
    "duas fontes); 'Quem chefia o setor responsável pelo item X?' (cadeia pessoa->setor->item).\n\n"
    "reasoning_max — várias relações interdependentes, restrições combinadas e síntese sobre "
    "muitas fontes ou cadeias longas, com possível conflito a resolver. Ex.: 'Considerando o "
    "histórico de compras, o contrato vigente e a política de reembolso, qual o valor final e o "
    "prazo?' (agrega 3+ fontes e aplica regras); 'Qual foi o segundo maior crescimento e em que "
    "trimestre ocorreu após a maior queda?' (comparação temporal encadeada)."
)
CLASSIFICATION_TOOL: ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "name": "classify_reasoning",
        "description": "Classifica a complexidade da mensagem do usuário para determinar o nível de raciocínio do modelo.",
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "intention": {
                    "type": "string",
                    "enum": [
                        "reasoning_off",
                        "reasoning_low",
                        "reasoning_high",
                        "reasoning_max",
                    ],
                    "description": (CLASSIFICATION_REASONING_DESCRIPTION),
                },
            },
            "required": ["intention"],
            "additionalProperties": False,
        },
    },
}

TERMINAL_TOOL_DESCRIPTION = (
    "Executa um comando no shell do sistema e retorna status, exit_code, stdout e stderr. "
    "Use para inspecionar arquivos, rodar testes, git e outras tarefas de linha de comando. "
    "Comandos destrutivos exigem confirmacao do usuario e podem ser negados."
)

TERMINAL_TOOL: ChatCompletionToolParam = {
    "type": "function",
    "function": {
        "name": "run_terminal_command",
        "description": TERMINAL_TOOL_DESCRIPTION,
        "strict": True,
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "O comando exato a ser executado no shell.",
                },
                "timeout_seconds": {
                    "type": "number",
                    "description": "Tempo maximo de execucao em segundos.",
                },
            },
            "required": ["command", "timeout_seconds"],
            "additionalProperties": False,
        },
    },
}
