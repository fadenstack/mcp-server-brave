"""Health and readiness endpoints."""

from fastapi import APIRouter
from fastapi.responses import UJSONResponse

router = APIRouter(tags=["monitoring"])


@router.get("/health")
async def health_check() -> UJSONResponse:
    return UJSONResponse({"status": "ok", "provider": "brave"})
