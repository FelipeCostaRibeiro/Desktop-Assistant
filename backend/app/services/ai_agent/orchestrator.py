import json
from typing import Any, cast
from .models import (
    MODEL_CHAT,
    get_client,
    CLASSIFICATION_TOOL,
    TERMINAL_TOOL,
    )
from openai.types.chat import (
    ChatCompletionMessageFunctionToolCall,
    ChatCompletionMessageParam,
    ChatCompletionToolChoiceOptionParam,
)

MAX_HISTORY_CONTEXT = 15
CLASSIFY_WINDOW = 5
MAX_AGENT_STEPS = 8
DEFAULT_INTENTION = "reasoning_off"
TERMINAL_TOOL_NAME = "run_terminal_command"

REASONING_PARAMS: dict[str, dict] = {
    "reasoning_off": {"enabled": False},
    "reasoning_low": {"effort": "low"},
    "reasoning_high": {"effort": "high"},
    "reasoning_max": {"effort": "high", "max_tokens": 32000},
}


def prepare_message(messages: list[dict[str, str]]) -> list[ChatCompletionMessageParam]:
    system = [messages[0]]
    chat = messages[1:]
    recent_chat = chat[-MAX_HISTORY_CONTEXT:]
    return cast("list[ChatCompletionMessageParam]", system + recent_chat)


async def classify(messages: list[dict[str, str]]) -> str:
    context = messages[0:1] + messages[1:][-CLASSIFY_WINDOW:]
    prompt = context + [
        {
            "role": "user",
            "content": "Classifique a mensagem do usuário imediatamente acima por nível de raciocínio.",
        }
    ]
    classification = await get_client().chat.completions.create(
        model=MODEL_CHAT,
        messages=cast("list[ChatCompletionMessageParam]", prompt),
        tools=[CLASSIFICATION_TOOL],
        tool_choice=cast(
            "ChatCompletionToolChoiceOptionParam",
            {"type": "function", "function": {"name": "classify_reasoning"}},
        ),
    )
    tool_calls = classification.choices[0].message.tool_calls or []
    if not tool_calls:
        return DEFAULT_INTENTION
    call = cast("ChatCompletionMessageFunctionToolCall", tool_calls[0])
    arguments = json.loads(call.function.arguments)
    return arguments.get("intention", DEFAULT_INTENTION)


async def generate_answer(messages: list[dict[str, str]]) -> str:
    intention = await classify(messages)
    answer = await get_client().chat.completions.create(
        model=MODEL_CHAT,
        messages=prepare_message(messages),
        extra_body={"reasoning": REASONING_PARAMS.get(intention, REASONING_PARAMS[DEFAULT_INTENTION])},
    )
    return answer.choices[0].message.content or ""


async def generate_answer_stream(messages: list[dict[str, str]]):
    intention = await classify(messages)
    stream = await get_client().chat.completions.create(
        model=MODEL_CHAT,
        messages=prepare_message(messages),
        extra_body={"reasoning": REASONING_PARAMS.get(intention, REASONING_PARAMS[DEFAULT_INTENTION])},
        stream=True,
    )
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta


async def _run_tool_call(
    call: ChatCompletionMessageFunctionToolCall,
    session: Any,
    confirmer: Any,
) -> str:
    if call.function.name != TERMINAL_TOOL_NAME:
        return json.dumps(
            {"status": "error", "reason": f"ferramenta desconhecida: {call.function.name}"},
            ensure_ascii=False,
        )
    if session is None:
        return json.dumps(
            {"status": "error", "reason": "terminal indisponivel"},
            ensure_ascii=False,
        )
    try:
        arguments = json.loads(call.function.arguments or "{}")
    except json.JSONDecodeError:
        return json.dumps(
            {"status": "error", "reason": "argumentos invalidos"},
            ensure_ascii=False,
        )

    command = arguments.get("command")
    if not command or not isinstance(command, str):
        return json.dumps(
            {"status": "error", "reason": "campo 'command' ausente"},
            ensure_ascii=False,
        )

    timeout = float(arguments.get("timeout_seconds") or 30)
    result = await session.run(command, timeout=timeout, confirmer=confirmer)
    return result.to_tool_content()


async def run_agent(
    messages: list[dict[str, str]],
    session: Any,
    confirmer: Any = None,
    max_steps: int = MAX_AGENT_STEPS,
) -> str:
    intention = await classify(messages)
    reasoning = REASONING_PARAMS.get(intention, REASONING_PARAMS[DEFAULT_INTENTION])
    trajectory = cast("list[ChatCompletionMessageParam]", list(prepare_message(messages)))

    for _ in range(max_steps):
        response = await get_client().chat.completions.create(
            model=MODEL_CHAT,
            messages=trajectory,
            tools=[TERMINAL_TOOL],
            extra_body={"reasoning": reasoning},
        )
        message = response.choices[0].message
        tool_calls = message.tool_calls or []
        if not tool_calls:
            return message.content or ""

        trajectory.append(
            cast(
                "ChatCompletionMessageParam",
                {
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [call.model_dump() for call in tool_calls],
                },
            )
        )

        for raw_call in tool_calls:
            call = cast("ChatCompletionMessageFunctionToolCall", raw_call)
            content = await _run_tool_call(call, session, confirmer)
            trajectory.append(
                cast(
                    "ChatCompletionMessageParam",
                    {"role": "tool", "tool_call_id": call.id, "content": content},
                )
            )

    return "Limite de passos do agente atingido sem resposta final."
