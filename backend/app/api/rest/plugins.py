from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.services.plugins.registry import list_plugins

router = APIRouter()


@router.get("")
def plugins(user=Depends(get_current_user)) -> list[dict]:
    del user
    return list_plugins()

