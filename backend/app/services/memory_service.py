from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import MemoryEntry, Scan
from app.services.llm.factory import get_llm_provider


class MemoryService:
    def __init__(self) -> None:
        self.provider = get_llm_provider()

    def store_scan_memory(self, db: Session, scan: Scan, content: str, metadata: dict | None = None) -> MemoryEntry:
        entry = MemoryEntry(
            scan_id=scan.id,
            target=scan.target,
            content=content,
            embedding=self.provider.embed(content),
            entry_metadata=metadata or {},
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry

    def retrieve_related(self, db: Session, target: str, query_text: str, limit: int = 5) -> list[MemoryEntry]:
        query_embedding = self.provider.embed(query_text)
        statement = (
            select(MemoryEntry)
            .where(MemoryEntry.target == target, MemoryEntry.embedding.is_not(None))
            .order_by(MemoryEntry.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )
        return list(db.scalars(statement))
