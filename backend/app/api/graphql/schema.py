import strawberry
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.services.plugins.registry import list_plugins
from app.services.scan_service import dashboard_stats, list_scans


@strawberry.type
class PluginType:
    name: str
    description: str
    source: str


@strawberry.type
class DashboardType:
    scans_total: int
    active_scans: int
    findings_total: int
    critical_findings: int


@strawberry.type
class ScanType:
    id: str
    target: str
    status: str
    approval_status: str
    summary: str


@strawberry.type
class Query:
    @strawberry.field
    def dashboard(self) -> DashboardType:
        with SessionLocal() as db:
            stats = dashboard_stats(db)
            return DashboardType(**stats.model_dump())

    @strawberry.field
    def scans(self) -> list[ScanType]:
        with SessionLocal() as db:
            return [
                ScanType(
                    id=str(scan.id),
                    target=scan.target,
                    status=scan.status.value,
                    approval_status=scan.approval_status.value,
                    summary=scan.summary,
                )
                for scan in list_scans(db)
            ]

    @strawberry.field
    def plugins(self) -> list[PluginType]:
        return [PluginType(**plugin) for plugin in list_plugins()]


schema = strawberry.Schema(query=Query)

