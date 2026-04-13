from app.db.session import SessionLocal
from app.services.agents.coordinator import CoordinatorAgent
from app.services.scan_service import get_scan, mark_scan_completed, mark_scan_failed, mark_scan_running
from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.scan_tasks.run_scan_task")
def run_scan_task(scan_id: str) -> None:
    with SessionLocal() as db:
        scan = get_scan(db, scan_id)
        if not scan:
            return
        try:
            mark_scan_running(db, scan)
            CoordinatorAgent().run(db, scan)
            mark_scan_completed(db, scan)
        except Exception as exc:  # noqa: BLE001
            mark_scan_failed(db, scan, f"Scan failed: {exc}")
            raise

