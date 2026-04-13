import asyncio
from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import Depends, FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import select, text
from strawberry.fastapi import GraphQLRouter

from app.api.deps import get_current_user
from app.api.graphql.schema import schema
from app.api.router import api_router
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.core.rate_limit import limiter
from app.core.token_utils import decode_subject
from app.db.base import Base
from app.db.models import ScanLog, User
from app.db.session import SessionLocal, engine
from app.metrics import initialize_metrics
from app.services.auth_service import ensure_default_admin
from app.services.graph_service import GraphService

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
    initialize_metrics()
    with SessionLocal() as db:
        ensure_default_admin(db, settings.default_admin_email, settings.default_admin_password)
    try:
        GraphService().ensure_constraints()
    except Exception:
        pass
    yield


app = FastAPI(title=settings.project_name, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def graphql_context(user=Depends(get_current_user)) -> dict:
    return {"user": user}


app.include_router(api_router)
app.include_router(GraphQLRouter(schema, context_getter=graphql_context), prefix="/graphql")
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


def get_user_from_token(token: str) -> User | None:
    subject = decode_subject(token)
    if not subject:
        return None
    with SessionLocal() as db:
        try:
            return db.get(User, UUID(subject))
        except ValueError:
            return None


@app.websocket("/ws/scans/{scan_id}")
async def scan_logs_websocket(websocket: WebSocket, scan_id: str) -> None:
    token = websocket.query_params.get("token", "")
    user = get_user_from_token(token)
    if not user:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    last_id = 0
    try:
        while True:
            with SessionLocal() as db:
                logs = list(
                    db.scalars(
                        select(ScanLog).where(ScanLog.scan_id == scan_id, ScanLog.id > last_id).order_by(ScanLog.id.asc())
                    )
                )
            for entry in logs:
                last_id = entry.id
                await websocket.send_json(
                    {
                        "id": entry.id,
                        "level": entry.level,
                        "message": entry.message,
                        "created_at": entry.created_at.isoformat(),
                    }
                )
            await asyncio.sleep(settings.websocket_poll_interval_seconds)
    except WebSocketDisconnect:
        return
