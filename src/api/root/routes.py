from fastapi import APIRouter, status
from api.config import get_settings

router = APIRouter()
settings = get_settings()


@router.get("/health")
def get_health():
    return True


@router.get("/db/path")
def get_db_path():
    return settings.db.URL
