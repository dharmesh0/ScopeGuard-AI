from collections import Counter

from sqlalchemy.orm import Session

from app.db.models import Finding, Scan, ScanLog, Severity
from app.services.agents.analysis_agent import AnalysisAgent
from app.services.agents.base import AgentContext
from app.services.agents.recon_agent import ReconAgent
from app.services.agents.reporting_agent import ReportingAgent
from app.services.graph_service import GraphService
from app.services.memory_service import MemoryService
from app.services.report_service import ReportService


class CoordinatorAgent:
    def __init__(self) -> None:
        self.recon = ReconAgent()
        self.analysis = AnalysisAgent()
        self.reporting = ReportingAgent()
        self.memory = MemoryService()
        self.graph = GraphService()
        self.reports = ReportService()

    @staticmethod
    def _persist_logs(db: Session, scan: Scan, messages: list[str]) -> None:
        for message in messages:
            db.add(ScanLog(scan_id=scan.id, level="INFO", message=message))
        db.commit()

    def run(self, db: Session, scan: Scan) -> None:
        context = AgentContext(scan_id=str(scan.id), target=scan.target, human_in_the_loop=scan.human_in_the_loop)
        try:
            memory_entries = self.memory.retrieve_related(db, scan.target, scan.target, limit=3)
            context.memory = [entry.content for entry in memory_entries]
        except Exception:
            context.memory = []

        recon_result = self.recon.run(context)
        self._persist_logs(db, scan, recon_result.logs)
        context.findings = recon_result.findings
        analysis_result = self.analysis.run(context)
        self._persist_logs(db, scan, analysis_result.logs)
        context.summary = analysis_result.summary
        reporting_result = self.reporting.run(context)
        self._persist_logs(db, scan, reporting_result.logs)

        db.query(Finding).filter(Finding.scan_id == scan.id).delete()
        for finding_payload in context.findings:
            db.add(
                Finding(
                    scan_id=scan.id,
                    plugin=finding_payload["plugin"],
                    title=finding_payload["title"],
                    description=finding_payload["description"],
                    severity=Severity(finding_payload["severity"]),
                    evidence=finding_payload["evidence"],
                    remediation=finding_payload["remediation"],
                    references=finding_payload.get("references", []),
                )
            )
        db.commit()
        db.refresh(scan)

        severity_counts = Counter(finding.severity.value for finding in scan.findings)
        scan.summary = reporting_result.summary
        scan.severity_counts = dict(severity_counts)
        db.add(scan)
        db.commit()
        db.refresh(scan)

        memory_content = "\n".join([scan.summary] + [finding.title for finding in scan.findings])
        try:
            self.memory.store_scan_memory(db, scan, memory_content, {"severity_counts": scan.severity_counts})
        except Exception:
            pass
        try:
            self.graph.upsert_scan_graph(scan, scan.findings)
        except Exception:
            pass
        self.reports.generate(db, scan, scan.engagement)
