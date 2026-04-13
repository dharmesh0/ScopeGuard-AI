from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class EngagementCreate(BaseModel):
    name: str = Field(min_length=3, max_length=255)
    description: str = ""
    scope: list[str] = Field(min_length=1)
    approval_mode: bool = True


class EngagementResponse(BaseModel):
    id: UUID
    name: str
    description: str
    scope: list[str]
    approval_mode: bool
    created_at: datetime

    model_config = {"from_attributes": True}

