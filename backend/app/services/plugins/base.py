from dataclasses import dataclass, field
from typing import Protocol

from app.db.models import Severity


@dataclass
class PluginFinding:
    plugin: str
    title: str
    description: str
    severity: Severity
    evidence: dict
    remediation: str
    references: list[str] = field(default_factory=list)


@dataclass
class PluginContext:
    target: str
    timeout_seconds: int = 20


class ScannerPlugin(Protocol):
    name: str
    description: str

    def run(self, context: PluginContext) -> list[PluginFinding]:
        ...

