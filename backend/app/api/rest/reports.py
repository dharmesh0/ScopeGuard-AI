from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy.orm import Session

from app.core.token_utils import decode_subject
from app.db.models import Report, User
from app.db.session import get_db
from app.schemas.report import ReportResponse

router = APIRouter()


def _authorized(request: Request, token: str | None, db: Session) -> bool:
    bearer = request.headers.get("authorization", "")
    if bearer.lower().startswith("bearer "):
        token = bearer.split(" ", 1)[1].strip()
    subject = decode_subject(token) if token else None
    if not subject:
        return False
    try:
        return bool(db.get(User, UUID(subject)))
    except ValueError:
        return False


@router.get("/scan/{scan_id}", response_model=ReportResponse)
def get_report(scan_id, request: Request, db: Session = Depends(get_db), token: str | None = Query(default=None)) -> ReportResponse:
    if not _authorized(request, token, db):
        raise HTTPException(status_code=401, detail="Unauthorized.")
    report = db.query(Report).filter(Report.scan_id == scan_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return ReportResponse.model_validate(report)


@router.get("/scan/{scan_id}/markdown")
def get_report_markdown(
    scan_id,
    request: Request,
    db: Session = Depends(get_db),
    token: str | None = Query(default=None),
) -> PlainTextResponse:
    if not _authorized(request, token, db):
        raise HTTPException(status_code=401, detail="Unauthorized.")
    report = db.query(Report).filter(Report.scan_id == scan_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return PlainTextResponse(Path(report.markdown_path).read_text(encoding="utf-8"))


@router.get("/scan/{scan_id}/pdf")
def get_report_pdf(
    scan_id,
    request: Request,
    db: Session = Depends(get_db),
    token: str | None = Query(default=None),
) -> FileResponse:
    if not _authorized(request, token, db):
        raise HTTPException(status_code=401, detail="Unauthorized.")
    report = db.query(Report).filter(Report.scan_id == scan_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return FileResponse(report.pdf_path, media_type="application/pdf", filename=f"{scan_id}.pdf")
