"""
Vercel serverless entry point.

Vercel's Python runtime detects the ASGI `app` object exported here and serves
it. All routes are rewritten to this module via vercel.json.
"""
from app.main import app

# Exposed for the Vercel Python runtime (ASGI).
__all__ = ["app"]
