from dataclasses import dataclass, field


@dataclass
class AgentContext:
    scan_id: str
    target: str
    human_in_the_loop: bool
    memory: list[str] = field(default_factory=list)
    findings: list[dict] = field(default_factory=list)
    latest_cves: list[dict] = field(default_factory=list)
    summary: str = ""


@dataclass
class AgentResult:
    logs: list[str]
    findings: list[dict] = field(default_factory=list)
    summary: str = ""

