import asyncio
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Awaitable, Callable

from .terminal_policy import evaluate

Confirmer = Callable[[str, str | None], Awaitable[bool]]


@dataclass
class CommandResult:
    command: str
    status: str
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0
    truncated: bool = False
    reason: str | None = None

    def to_tool_content(self) -> str:
        payload = {
            "status": self.status,
            "exit_code": self.exit_code,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "truncated": self.truncated,
        }
        if self.reason:
            payload["reason"] = self.reason
        return json.dumps(payload, ensure_ascii=False)


async def _deny_all(_command: str, _reason: str | None) -> bool:
    return False


def _truncate(text: str, limit: int) -> tuple[str, bool]:
    if len(text) <= limit:
        return text, False
    return text[:limit], True


class TerminalSession:
    def __init__(
        self,
        root: str | Path,
        env: dict[str, str] | None = None,
        confirmer: Confirmer | None = None,
    ) -> None:
        self.root = Path(root).resolve()
        self.cwd = self.root
        self.env = {**os.environ, **(env or {})}
        self.confirmer: Confirmer = confirmer or _deny_all
        self.history: list[str] = []

    async def run(
        self,
        command: str,
        *,
        timeout: float = 30.0,
        max_output: int = 20_000,
        confirmer: Confirmer | None = None,
    ) -> CommandResult:
        decision = evaluate(command, self.cwd, self.root)
        if not decision.allowed:
            return CommandResult(command=command, status="blocked", reason=decision.reason)

        if decision.requires_confirmation:
            confirm = confirmer or self.confirmer
            approved = await confirm(command, decision.reason)
            if not approved:
                return CommandResult(command=command, status="denied", reason=decision.reason)

        self.history.append(command)
        return await self._execute(command, timeout, max_output)

    def _shell_argv(self, command: str) -> list[str]:
        if sys.platform == "win32":
            return ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command]
        return ["/bin/sh", "-lc", command]

    async def _execute(self, command: str, timeout: float, max_output: int) -> CommandResult:
        start = time.monotonic()
        try:
            process = await asyncio.create_subprocess_exec(
                *self._shell_argv(command),
                cwd=str(self.cwd),
                env=self.env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except (OSError, ValueError) as exc:
            return CommandResult(command=command, status="error", reason=str(exc))

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(), timeout=timeout
            )
            status = "ok"
            exit_code = process.returncode
            reason = None
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            stdout_bytes, stderr_bytes = b"", b""
            status = "timeout"
            exit_code = None
            reason = f"tempo limite de {timeout}s excedido"

        duration_ms = int((time.monotonic() - start) * 1000)
        stdout, truncated_out = _truncate(stdout_bytes.decode("utf-8", "replace"), max_output)
        stderr, truncated_err = _truncate(stderr_bytes.decode("utf-8", "replace"), max_output)

        return CommandResult(
            command=command,
            status=status,
            exit_code=exit_code,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
            truncated=truncated_out or truncated_err,
            reason=reason,
        )
