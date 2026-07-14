"""
SignBridge AI - FastAPI entrypoint.

Run with:
    uvicorn app.main:app --reload --port 8000

(from inside the backend/ directory, with the virtualenv active)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_translate, routes_ws
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title=settings.app_name,
    description="Real-time sign language translation platform.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes_translate.router)
app.include_router(routes_ws.router)

# Routers added in later steps:
#   routes_speech     - speech-to-text / text-to-speech        (Step 7)


@app.on_event("startup")
async def on_startup() -> None:
    logger.info(
        "%s starting up | environment=%s | debug=%s",
        settings.app_name,
        settings.environment,
        settings.debug,
    )


@app.get("/")
async def root() -> dict:
    return {
        "message": f"{settings.app_name} API is running",
        "docs": "/docs",
        "status_endpoint": "/api/v1/status",
    }