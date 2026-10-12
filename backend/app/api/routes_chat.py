from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.ai_agent.orchestrator import generate_answer

router = APIRouter(tags=["chat"])

SYSTEM_PROMPT = (
    "Você é o DeskAI, um assistente de desktop. "
    "Responda de forma clara, objetiva e em português do Brasil. "
    "Quando não tiver certeza de algo, diga que não sabe em vez de inventar."
)


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str


def build_messages(request: ChatRequest) -> list[dict[str, str]]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(message.model_dump() for message in request.history)
    messages.append({"role": "user", "content": request.message})
    return messages


@router.post("/chat", responses={502: {"description": "Falha na chamada da LLM"}})
async def chat(request: ChatRequest) -> ChatResponse:
    messages = build_messages(request)
    try:
        reply = await generate_answer(messages)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Falha na chamada da LLM: {exc}") from exc
    return ChatResponse(reply=reply)
