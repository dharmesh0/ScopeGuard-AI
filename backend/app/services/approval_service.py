from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Approval, ApprovalStatus, Engagement, User
from app.schemas.approval import ApprovalCreate
from app.utils.targets import match_scope


def ensure_target_is_authorized(engagement: Engagement, target: str) -> None:
    if not match_scope(target, engagement.scope):
        raise ValueError("Target is outside the approved engagement scope.")


def create_approval_request(db: Session, payload: ApprovalCreate) -> Approval:
    approval = Approval(
        engagement_id=payload.engagement_id,
        target=payload.target,
        attestation=payload.attestation,
        status=ApprovalStatus.pending,
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval


def list_approvals(db: Session) -> list[Approval]:
    return list(db.scalars(select(Approval).order_by(Approval.created_at.desc())))


def get_approval(db: Session, approval_id) -> Approval | None:
    return db.scalar(select(Approval).where(Approval.id == approval_id))


def get_latest_approval(db: Session, engagement_id, target: str) -> Approval | None:
    return db.scalar(
        select(Approval)
        .where(Approval.engagement_id == engagement_id, Approval.target == target)
        .order_by(Approval.created_at.desc())
    )


def decide_approval(db: Session, approval: Approval, reviewer: User, status: ApprovalStatus) -> Approval:
    approval.status = status
    approval.reviewed_by = reviewer.id
    approval.reviewed_at = datetime.now(UTC)
    db.add(approval)
    db.commit()
    db.refresh(approval)
    return approval
