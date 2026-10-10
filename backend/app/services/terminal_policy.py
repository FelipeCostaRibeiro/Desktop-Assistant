import re
from dataclasses import dataclass
from pathlib import Path

DESTRUCTIVE_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"\brm\s+-[a-z]*r[a-z]*\b", "remocao recursiva (rm -r)"),
    (r"\bremove-item\b.*-(recurse|force)", "Remove-Item recursivo/forcado"),
    (r"\bdel\b\s+/[fsq]", "del com /f /s /q"),
    (r"\b(rmdir|rd)\b\s+/s", "rmdir /s"),
    (r"\bformat\b", "formatacao de disco"),
    (r"\bmkfs(\.\w+)?\b", "mkfs"),
    (r"\bdd\b.*\bof=", "dd"),
    (r"\b(shutdown|reboot|halt|poweroff)\b", "desligamento"),
    (r"\b(stop-computer|restart-computer)\b", "desligamento (PowerShell)"),
    (r":\(\)\s*\{", "fork bomb"),
    (r"\bsudo\b", "elevacao de privilegio"),
    (r"\bgit\s+push\b.*(--force|-f)\b", "git push forcado"),
    (r"\bgit\s+reset\b.*--hard", "git reset --hard"),
    (r"\bgit\s+clean\b.*-[a-z]*[fd]", "git clean destrutivo"),
    (r">\s*(/dev/[sh]d|\\\\\.\\physicaldrive)", "escrita direta em disco"),
    (r"\bchmod\s+-R\s+777", "chmod 777 recursivo"),
    (r"\b(curl|wget|invoke-webrequest|iwr)\b.*\|\s*(sh|bash|iex|invoke-expression)", "pipe remoto para execucao"),
)


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str | None = None


def evaluate(command: str, cwd: Path, root: Path) -> PolicyDecision:
    try:
        Path(cwd).resolve().relative_to(Path(root).resolve())
    except (ValueError, OSError):
        return PolicyDecision(
            allowed=False,
            requires_confirmation=False,
            reason="diretorio de trabalho fora do permitido",
        )

    for pattern, label in DESTRUCTIVE_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return PolicyDecision(
                allowed=True,
                requires_confirmation=True,
                reason=f"padrao de risco detectado: {label}",
            )

    return PolicyDecision(allowed=True, requires_confirmation=False)
