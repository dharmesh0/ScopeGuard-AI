from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.models import ApprovalStatus
from app.db.session import get_db
from app.schemas.approval import ApprovalCreate, ApprovalDecision, ApprovalResponse
from app.services.approval_service import create_approval_request, decide_approval, get_approval, list_approvals
from app.services.scan_service import resume_scan

router = APIRouter()


@router.get("", response_model=list[ApprovalResponse])
def get_approvals(db: Session = Depends(get_db), user=Depends(get_current_user)) -> list[ApprovalResponse]:
    del user
    return [ApprovalResponse.model_validate(item) for item in list_approvals(db)]


@router.post("", response_model=ApprovalResponse, status_code=status.HTTP_201_CREATED)
def post_approval(payload: ApprovalCreate, db: Session = Depends(get_db), user=Depends(get_current_user)) -> ApprovalResponse:
    del user
    approval = create_approval_request(db, payload)
    return ApprovalResponse.model_validate(approval)


@router.post("/{approval_id}/decision", response_model=ApprovalResponse)
def approval_decision(
    approval_id,
    payload: ApprovalDecision,
    db: Session = Depends(get_db),
    reviewer=Depends(require_admin),
) -> ApprovalResponse:
    approval = get_approval(db, approval_id)
    if not approval:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Approval not found.")
    approval = decide_approval(db, approval, reviewer, payload.status)

    if payload.status == ApprovalStatus.approved:
        from app.db.models import Scan

        pending_scan = db.query(Scan).filter(Scan.target == approval.target, Scan.engagement_id == approval.engagement_id).order_by(Scan.created_at.desc()).first()
        if pending_scan:
            pending_scan.approval_status = ApprovalStatus.approved
            db.add(pending_scan)
            db.commit()
            resume_scan(db, pending_scan)
    return ApprovalResponse.model_validate(approval)
