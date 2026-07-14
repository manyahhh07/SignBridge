"""
HTTP routes for translation.

Step 1 status: only /status is functional. The other two routes are
intentionally marked NOT IMPLEMENTED (raising 501) rather than silently
returning fake data - they'll be wired to real logic in Step 4 (sign
recognition) and Step 6 (text-to-sign).
"""

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.core.logger import get_logger
from app.schemas.translation import (
    HealthResponse,
    TextToSignRequest,
    TextToSignResponse,
)

router = APIRouter(prefix="/api/v1", tags=["translation"])
logger = get_logger(__name__)


@router.get("/status", response_model=HealthResponse)
async def get_status() -> HealthResponse:
    """Basic liveness/config check used by the frontend to confirm the API is reachable."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        environment=settings.environment,
    )


@router.post("/translate/text-to-sign", response_model=TextToSignResponse)
async def text_to_sign(payload: TextToSignRequest) -> TextToSignResponse:
    """
    NOT IMPLEMENTED YET.

    Will map `payload.text` to a sequence of gesture ids via the gesture
    library abstraction built in Step 6.
    """
    logger.info("text_to_sign called before implementation: %r", payload.text)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Text-to-sign translation is implemented in Step 6.",
    )