from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Engagement, User
from app.schemas.engagement import EngagementCreate


def create_engagement(db: Session, payload: EngagementCreate, user: User) -> Engagement:
    engagement = Engagement(
        name=payload.name,
        description=payload.description,
        scope=payload.scope,
        approval_mode=payload.approval_mode,
        created_by=user.id,
    )
    db.add(engagement)
    db.commit()
    db.refresh(engagement)
    return engagement


def list_engagements(db: Session) -> list[Engagement]:
    return list(db.scalars(select(Engagement).order_by(Engagement.created_at.desc())))


def get_engagement(db: Session, engagement_id) -> Engagement | None:
    return db.scalar(select(Engagement).where(Engagement.id == engagement_id))

