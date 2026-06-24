"""
Quick Supabase data check via the REST API (PostgREST) — no supabase-py needed.

Run locally:
    source .venv/bin/activate
    PYTHONPATH=. python scripts/check_supabase.py
    PYTHONPATH=. python scripts/check_supabase.py users matches
"""
import sys

import httpx

from app.core.config import settings


def main() -> None:
    print("Supabase URL:", settings.SUPABASE_URL or "(not set)")
    if not settings.supabase_configured:
        print("✗ Not configured — set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env")
        sys.exit(1)

    base = settings.SUPABASE_URL.rstrip("/") + "/rest/v1"
    key = settings.SUPABASE_SERVICE_ROLE_KEY
    headers = {"apikey": key, "Authorization": f"Bearer {key}"}

    tables = sys.argv[1:] or ["users", "matches", "predictions", "subscriptions"]

    with httpx.Client(timeout=15) as client:
        for table in tables:
            url = f"{base}/{table}"
            try:
                r = client.get(url, headers=headers, params={"select": "*", "limit": 5})
                if r.status_code == 200:
                    rows = r.json()
                    print(f"\n[{table}] {len(rows)} row(s):")
                    for row in rows:
                        print("   ", row)
                    if not rows:
                        print("    (table exists but empty)")
                elif r.status_code == 404 or "does not exist" in r.text:
                    print(f"\n[{table}] ✗ table does not exist yet")
                else:
                    print(f"\n[{table}] ✗ {r.status_code}: {r.text[:160]}")
            except Exception as exc:  # noqa: BLE001
                print(f"\n[{table}] ✗ {type(exc).__name__}: {str(exc)[:160]}")


if __name__ == "__main__":
    main()
