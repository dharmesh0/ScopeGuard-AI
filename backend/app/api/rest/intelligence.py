from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.services.intelligence.cve_feed import CVEFeedService

router = APIRouter()
service = CVEFeedService()


@router.get("/latest-cves")
def latest_cves(user=Depends(get_current_user)) -> list[dict]:
    del user
    return service.latest(limit=10)
