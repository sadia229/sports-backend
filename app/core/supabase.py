from functools import lru_cache

from supabase import create_client, Client
from app.core.config import settings


@lru_cache
def get_supabase_client() -> Client:
    """
    Return a cached Supabase client.

    Built lazily on first use (not at import) so a deploy with missing env vars
    still boots and serves /docs + /health; only callers that need Supabase hit
    this clear error.
    """
    if not settings.supabase_configured:
        raise RuntimeError(
            "Supabase is not configured. Set SUPABASE_URL and "
            "SUPABASE_SERVICE_ROLE_KEY in the environment."
        )
    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY,
    )
