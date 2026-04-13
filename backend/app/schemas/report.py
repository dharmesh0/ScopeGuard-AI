from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ReportResponse(BaseModel):
    id: UUID
    scan_id: UUID
    markdown_path: str
    pdf_path: str
    checksum: str
    created_at: datetime

    model_config = {"from_attributes": True}

