"""
Lightweight Supabase data access via the REST API (PostgREST).

Uses plain httpx instead of supabase-py (which has heavy, conflicting deps that
break on Python 3.12 / serverless). Works identically locally and on Vercel.

The service-role key is used server-side, so these calls bypass Row Level
Security — never expose it to clients.
"""
from typing import Any, Optional

import httpx

from app.core.config import settings


def _base() -> str:
    return settings.SUPABASE_URL.rstrip("/") + "/rest/v1"


def _headers(extra: Optional[dict] = None) -> dict:
    key = settings.SUPABASE_SERVICE_ROLE_KEY
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    if extra:
        headers.update(extra)
    return headers


async def insert(table: str, row: dict) -> dict:
    """Insert one row and return it (with db-generated fields like id)."""
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            f"{_base()}/{table}",
            headers=_headers({"Prefer": "return=representation"}),
            json=row,
        )
        r.raise_for_status()
        data = r.json()
        return data[0] if isinstance(data, list) and data else data


async def select(
    table: str, filters: Optional[dict] = None, limit: Optional[int] = None
) -> list[dict]:
    """Select rows. filters use PostgREST syntax, e.g. {'email': 'eq.a@b.com'}."""
    params: dict[str, Any] = {"select": "*"}
    if filters:
        params.update(filters)
    if limit:
        params["limit"] = str(limit)
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(f"{_base()}/{table}", headers=_headers(), params=params)
        r.raise_for_status()
        return r.json()
