from prometheus_client import Gauge
from sqlalchemy import func, select

from app.db.models import Finding, Scan, ScanStatus, Severity
from app.db.session import SessionLocal

scans_total_gauge = Gauge("scopeguard_scans_total", "Total scans recorded")
active_scans_gauge = Gauge("scopeguard_active_scans", "Scans currently running or awaiting approval")
findings_total_gauge = Gauge("scopeguard_findings_total", "Total findings recorded")
critical_findings_gauge = Gauge("scopeguard_critical_findings", "Critical findings recorded")


def _query_scalar(statement) -> float:
    with SessionLocal() as db:
        value = db.scalar(statement)
        return float(value or 0)


def initialize_metrics() -> None:
    scans_total_gauge.set_function(lambda: _query_scalar(select(func.count(Scan.id))))
    active_scans_gauge.set_function(
        lambda: _query_scalar(
            select(func.count(Scan.id)).where(
                Scan.status.in_([ScanStatus.running, ScanStatus.waiting_for_approval, ScanStatus.queued])
            )
        )
    )
    findings_total_gauge.set_function(lambda: _query_scalar(select(func.count(Finding.id))))
    critical_findings_gauge.set_function(
        lambda: _query_scalar(select(func.count(Finding.id)).where(Finding.severity == Severity.critical))
    )
