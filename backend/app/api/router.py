from fastapi import APIRouter

from app.api.rest import approvals, auth, engagements, health, intelligence, plugins, reports, scans

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(engagements.router, prefix="/engagements", tags=["engagements"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(plugins.router, prefix="/plugins", tags=["plugins"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["intelligence"])

