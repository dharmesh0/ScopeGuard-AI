from datetime import UTC, datetime

from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session

from app.db.models import Approval, ApprovalStatus, Finding, Scan, ScanLog, ScanStatus, Severity, User
from app.schemas.scan import DashboardStats, ScanCreate
from app.services.approval_service import ensure_target_is_authorized, get_latest_approval
from app.services.engagement_service import get_engagement


def add_scan_log(db: Session, scan: Scan, message: str, level: str = "INFO") -> None:
    entry = ScanLog(scan_id=scan.id, level=level, message=message)
    db.add(entry)
    db.commit()


def create_scan(db: Session, payload: ScanCreate, user: User) -> Scan:
    engagement = get_engagement(db, payload.engagement_id)
    if not engagement:
        raise ValueError("Engagement not found.")

    ensure_target_is_authorized(engagement, payload.target)
    latest_approval = get_latest_approval(db, engagement.id, payload.target)
    approval_status = ApprovalStatus.approved if user.role.value == "admin" or not engagement.approval_mode else ApprovalStatus.pending
    status = ScanStatus.queued if approval_status == ApprovalStatus.approved else ScanStatus.waiting_for_approval
    if engagement.approval_mode and latest_approval and latest_approval.status == ApprovalStatus.approved:
        approval_status = ApprovalStatus.approved
        status = ScanStatus.queued

    scan = Scan(
        engagement_id=engagement.id,
        requested_by=user.id,
        target=payload.target,
        human_in_the_loop=payload.human_in_the_loop,
        approval_status=approval_status,
        status=status,
        policy_snapshot={"scope": engagement.scope, "attestation": payload.attestation},
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    add_scan_log(db, scan, "Scan request created.")
    if scan.approval_status == ApprovalStatus.pending:
        db.add(
            Approval(
                engagement_id=engagement.id,
                target=payload.target,
                attestation=payload.attestation,
                status=ApprovalStatus.pending,
            )
        )
        db.commit()
        add_scan_log(db, scan, "Approval request created automatically for this scan.")
    if scan.status == ScanStatus.queued:
        queue_scan(db, scan)
    return scan


def queue_scan(db: Session, scan: Scan) -> Scan:
    from app.tasks.scan_tasks import run_scan_task

    add_scan_log(db, scan, "Scan queued for worker execution.")
    run_scan_task.delay(str(scan.id))
    return scan


def resume_scan(db: Session, scan: Scan) -> Scan:
    if scan.approval_status != ApprovalStatus.approved:
        raise ValueError("Scan cannot resume until approval is granted.")
    if scan.status not in {ScanStatus.waiting_for_approval, ScanStatus.queued}:
        return scan
    scan.status = ScanStatus.queued
    db.add(scan)
    db.commit()
    db.refresh(scan)
    queue_scan(db, scan)
    return scan


def list_scans(db: Session) -> list[Scan]:
    return list(db.scalars(select(Scan).order_by(desc(Scan.created_at))))


def get_scan(db: Session, scan_id) -> Scan | None:
    return db.scalar(select(Scan).where(Scan.id == scan_id))


def dashboard_stats(db: Session) -> DashboardStats:
    scans_total = db.scalar(select(func.count(Scan.id))) or 0
    active_scans = (
        db.scalar(select(func.count(Scan.id)).where(Scan.status.in_([ScanStatus.running, ScanStatus.queued, ScanStatus.waiting_for_approval])))
        or 0
    )
    findings_total = db.scalar(select(func.count(Finding.id))) or 0
    critical_findings = db.scalar(select(func.count(Finding.id)).where(Finding.severity == Severity.critical)) or 0
    return DashboardStats(
        scans_total=scans_total,
        active_scans=active_scans,
        findings_total=findings_total,
        critical_findings=critical_findings,
    )


def mark_scan_running(db: Session, scan: Scan) -> None:
    scan.status = ScanStatus.running
    scan.started_at = datetime.now(UTC)
    db.add(scan)
    db.commit()
    add_scan_log(db, scan, "Worker started scan execution.")


def mark_scan_completed(db: Session, scan: Scan) -> None:
    scan.status = ScanStatus.completed
    scan.completed_at = datetime.now(UTC)
    db.add(scan)
    db.commit()
    add_scan_log(db, scan, "Scan completed successfully.")


def mark_scan_failed(db: Session, scan: Scan, reason: str) -> None:
    scan.status = ScanStatus.failed
    scan.completed_at = datetime.now(UTC)
    db.add(scan)
    db.commit()
    add_scan_log(db, scan, reason, level="ERROR")
