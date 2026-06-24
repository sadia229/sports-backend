import logging

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.security import get_current_user
from app.core.middleware import (
    SecurityHeadersMiddleware,
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    ErrorHandlingMiddleware,
)
from app.api import (
    matches,
    predictions,
    users,
    chat,
    subscriptions,
    webhooks,
    auth,
    rewards,
    ws,
)

# Ensure our app loggers (request timing, email service, etc.) actually emit.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s | %(message)s",
)

app = FastAPI(
    title="AI Match Predictor - Backend",
    description="Cricket/Football prediction, analytics, and entertainment service",
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Add middleware stack (order matters - applied in reverse)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# CORS middleware (last to be applied)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_api_version_header(request, call_next):
    response = await call_next(request)
    response.headers["X-API-Version"] = settings.API_VERSION
    return response


# Reusable JWT guard. Attaching it at include_router level applies it to every
# route in that router without repeating Depends() on each handler — the same
# dependency object is reused across all protected endpoints.
auth_required = [Depends(get_current_user)]

# Include routers. Every router except /auth requires a Bearer token.
app.include_router(auth.router)  # Public: issues/verifies tokens (the only open routes)
app.include_router(matches.router, dependencies=auth_required)
app.include_router(predictions.router, dependencies=auth_required)
app.include_router(users.router, dependencies=auth_required)
app.include_router(chat.router, dependencies=auth_required)
app.include_router(rewards.router, dependencies=auth_required)
app.include_router(subscriptions.router, dependencies=auth_required)
app.include_router(webhooks.router, dependencies=auth_required)
app.include_router(ws.router, dependencies=auth_required)


@app.get("/")
async def root():
    return {
        "success": True,
        "data": {
            "message": "AI Match Predictor API",
            "version": settings.API_VERSION,
            "status": "running"
        },
        "error": None,
        "meta": {
            "environment": settings.ENVIRONMENT,
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


@app.get("/health")
async def health():
    return {
        "success": True,
        "data": {"status": "healthy"},
        "error": None,
        "meta": {}
    }


@app.get("/status")
async def status():
    """Detailed status endpoint."""
    return {
        "success": True,
        "data": {
            "status": "operational",
            "version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT,
            "timestamp": "2026-06-24T16:30:00Z"
        },
        "error": None,
        "meta": {}
    }
