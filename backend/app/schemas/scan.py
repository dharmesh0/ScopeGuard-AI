from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.db.models import ApprovalStatus, ScanStatus, Severity


class ScanCreate(BaseModel):
    engagement_id: UUID
    target: str = Field(min_length=3, max_length=512)
    human_in_the_loop: bool = True
    attestation: str = Field(
        min_length=20,
        description="Operator statement confirming they have permission to assess this target.",
    )


class ScanLogResponse(BaseModel):
    id: int
    level: str
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}


class FindingResponse(BaseModel):
    id: UUID
    plugin: str
    title: str
    description: str
    severity: Severity
    evidence: dict
    remediation: str
    references: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class ScanResponse(BaseModel):
    id: UUID
    engagement_id: UUID
    requested_by: UUID
    target: str
    human_in_the_loop: bool
    approval_status: ApprovalStatus
    status: ScanStatus
    policy_snapshot: dict
    summary: str
    severity_counts: dict
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    findings: list[FindingResponse] = []
    logs: list[ScanLogResponse] = []

    model_config = {"from_attributes": True}


class DashboardStats(BaseModel):
    scans_total: int
    active_scans: int
    findings_total: int
    critical_findings: int

