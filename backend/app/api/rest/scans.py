from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.rate_limit import limiter
from app.db.models import ScanLog
from app.db.session import get_db
from app.schemas.scan import DashboardStats, ScanCreate, ScanLogResponse, ScanResponse
from app.services.scan_service import create_scan, dashboard_stats, get_scan, list_scans, resume_scan

router = APIRouter()


@router.get("/dashboard", response_model=DashboardStats)
def stats(db: Session = Depends(get_db), user=Depends(get_current_user)) -> DashboardStats:
    del user
    return dashboard_stats(db)


@router.get("", response_model=list[ScanResponse])
def get_scans(db: Session = Depends(get_db), user=Depends(get_current_user)) -> list[ScanResponse]:
    del user
    scans = list_scans(db)
    return [ScanResponse.model_validate(scan, from_attributes=True) for scan in scans]


@limiter.limit("15/minute")
@router.post("", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
def post_scan(request: Request, payload: ScanCreate, db: Session = Depends(get_db), user=Depends(get_current_user)) -> ScanResponse:
    del request
    try:
        scan = create_scan(db, payload, user)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ScanResponse.model_validate(scan, from_attributes=True)


@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan_detail(scan_id, db: Session = Depends(get_db), user=Depends(get_current_user)) -> ScanResponse:
    del user
    scan = get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")
    return ScanResponse.model_validate(scan, from_attributes=True)


@router.get("/{scan_id}/logs", response_model=list[ScanLogResponse])
def scan_logs(scan_id, db: Session = Depends(get_db), user=Depends(get_current_user)) -> list[ScanLogResponse]:
    del user
    logs = db.query(ScanLog).filter(ScanLog.scan_id == scan_id).order_by(ScanLog.id.asc()).all()
    return [ScanLogResponse.model_validate(item) for item in logs]


@router.post("/{scan_id}/resume", response_model=ScanResponse)
def resume(scan_id, db: Session = Depends(get_db), user=Depends(get_current_user)) -> ScanResponse:
    del user
    scan = get_scan(db, scan_id)
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found.")
    try:
        scan = resume_scan(db, scan)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ScanResponse.model_validate(scan, from_attributes=True)
