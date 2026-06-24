from supabase import create_client, Client
from app.core.config import settings


def get_supabase_client() -> Client:
    """Initialize and return Supabase client"""
    supabase: Client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_SERVICE_ROLE_KEY
    )
    return supabase


# Create a global instance
supabase_client = get_supabase_client()
