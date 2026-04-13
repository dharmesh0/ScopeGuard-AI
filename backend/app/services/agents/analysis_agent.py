from collections import Counter

from app.services.agents.base import AgentContext, AgentResult
from app.services.agents.prompts import SYSTEM_PROMPT
from app.services.intelligence.cve_feed import CVEFeedService
from app.services.llm.factory import get_llm_provider


class AnalysisAgent:
    def __init__(self) -> None:
        self.provider = get_llm_provider()
        self.cve_service = CVEFeedService()

    def run(self, context: AgentContext) -> AgentResult:
        logs = ["Analysis agent correlating findings, memory, and CVE intelligence."]
        try:
            cves = self.cve_service.latest(limit=5)
        except Exception as exc:  # noqa: BLE001
            cves = []
            logs.append(f"CVE enrichment unavailable: {exc}")
        context.latest_cves = cves
        severity_counts = Counter(item["severity"] for item in context.findings)
        prompt = "\n".join(
            [
                f"Target: {context.target}",
                f"Findings: {context.findings}",
                f"Related memory: {context.memory}",
                f"Latest CVEs: {cves}",
                f"Severity counts: {dict(severity_counts)}",
            ]
        )
        try:
            summary = self.provider.generate(SYSTEM_PROMPT, prompt)
        except Exception as exc:  # noqa: BLE001
            summary = f"Analysis provider unavailable. Defensive summary fallback: {exc}"
        logs.append("Analysis agent generated defensive summary.")
        return AgentResult(logs=logs, findings=context.findings, summary=summary)
