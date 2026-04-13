from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.schemas.engagement import EngagementCreate, EngagementResponse
from app.services.engagement_service import create_engagement, list_engagements

router = APIRouter()


@router.get("", response_model=list[EngagementResponse])
def get_engagements(db: Session = Depends(get_db), user=Depends(get_current_user)) -> list[EngagementResponse]:
    del user
    return [EngagementResponse.model_validate(item) for item in list_engagements(db)]


@router.post("", response_model=EngagementResponse, status_code=status.HTTP_201_CREATED)
def post_engagement(payload: EngagementCreate, db: Session = Depends(get_db), user=Depends(get_current_user)) -> EngagementResponse:
    engagement = create_engagement(db, payload, user)
    return EngagementResponse.model_validate(engagement)

