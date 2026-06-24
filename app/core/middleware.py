from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
import logging
import uuid
from app.core.config import settings

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    # Paths that render API documentation and need to load assets from a CDN.
    DOCS_PATHS = ("/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect")

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Swagger UI / ReDoc load CSS+JS from jsdelivr and a favicon from
        # fastapi.tiangolo.com. A strict `default-src 'self'` blocks those and
        # renders a blank docs page, so relax the CSP for the docs routes only.
        if request.url.path in self.DOCS_PATHS:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
                "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
                "img-src 'self' https://fastapi.tiangolo.com data:; "
                "worker-src 'self' blob:"
            )
        else:
            response.headers["Content-Security-Policy"] = "default-src 'self'"

        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests with request ID."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        start_time = time.perf_counter()
        response = await call_next(request)
        process_time = time.perf_counter() - start_time

        # Always expose timing on the response for clients/proxies.
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.4f}"

        # Log every request's response time (skip noisy health/metrics probes).
        if request.url.path not in ("/health", "/metrics"):
            client_ip = request.client.host if request.client else "unknown"
            logger.info(
                "[%s] %s %s -> %s in %.3fs (ip=%s)",
                request_id,
                request.method,
                request.url.path,
                response.status_code,
                process_time,
                client_ip,
            )

        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Basic rate limiting middleware.
    In production, use Redis-based rate limiting.
    """

    def __init__(self, app):
        super().__init__(app)
        self.request_counts = {}

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path == "/health":
            return await call_next(request)

        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Simple in-memory rate limiting (1000 requests per minute per IP)
        # In production: use Redis
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {"count": 0, "reset_at": time.time() + 60}

        if time.time() > self.request_counts[client_ip]["reset_at"]:
            self.request_counts[client_ip] = {"count": 0, "reset_at": time.time() + 60}

        self.request_counts[client_ip]["count"] += 1

        if self.request_counts[client_ip]["count"] > 1000:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "data": None,
                    "error": "Rate limit exceeded",
                    "meta": {"retry_after": 60}
                }
            )

        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = "1000"
        response.headers["X-RateLimit-Remaining"] = str(
            1000 - self.request_counts[client_ip]["count"]
        )
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Handle and format errors consistently."""

    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "data": None,
                    "error": "Internal server error",
                    "meta": {
                        "request_id": getattr(request.state, "request_id", "unknown")
                    }
                }
            )


class CORSEnhancedMiddleware(BaseHTTPMiddleware):
    """Enhanced CORS configuration."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # CORS headers
        response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin", "*")
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Max-Age"] = "3600"

        return response
