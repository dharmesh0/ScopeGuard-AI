from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.models import ApprovalStatus


class ApprovalCreate(BaseModel):
    engagement_id: UUID
    target: str
    attestation: str = Field(
        min_length=20,
        description="Operator attestation that the target is in scope and testing is authorized.",
    )


class ApprovalDecision(BaseModel):
    status: ApprovalStatus


class ApprovalResponse(BaseModel):
    id: UUID
    engagement_id: UUID
    target: str
    attestation: str
    status: ApprovalStatus
    reviewed_by: UUID | None
    reviewed_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}

