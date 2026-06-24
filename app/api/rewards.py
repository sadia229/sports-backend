from fastapi import APIRouter, Depends
from app.core.security import get_current_user, TokenData

router = APIRouter(prefix="/rewards", tags=["rewards"])


@router.get("/badges")
async def get_user_badges(token_data: TokenData = Depends(get_current_user)) -> dict:
    """Get user's earned badges."""
    return {
        "success": True,
        "data": {
            "user_id": token_data.user_id,
            "badges": [
                {
                    "id": "badge_1",
                    "type": "perfect_day",
                    "name": "Perfect Day",
                    "description": "Got all predictions correct in a day",
                    "earned_at": "2026-06-20T10:30:00Z"
                },
                {
                    "id": "badge_2",
                    "type": "7_day_streak",
                    "name": "Week Master",
                    "description": "7-day prediction streak",
                    "earned_at": "2026-06-15T14:20:00Z"
                }
            ],
            "total_badges": 2
        },
        "error": None,
        "meta": {}
    }


@router.get("/premium-days")
async def get_premium_days(token_data: TokenData = Depends(get_current_user)) -> dict:
    """Get user's earned free premium days (non-cash reward)."""
    return {
        "success": True,
        "data": {
            "user_id": token_data.user_id,
            "available_premium_days": 3,
            "used_premium_days": 5,
            "total_earned": 8,
            "premium_days": [
                {
                    "id": "day_1",
                    "granted_at": "2026-06-20T10:30:00Z",
                    "used_at": "2026-06-21T00:00:00Z",
                    "reason": "7_day_streak"
                },
                {
                    "id": "day_2",
                    "granted_at": "2026-06-15T14:20:00Z",
                    "used_at": None,
                    "reason": "contest_prize"
                }
            ]
        },
        "error": None,
        "meta": {}
    }


@router.post("/redeem-premium-day")
async def redeem_premium_day(token_data: TokenData = Depends(get_current_user)) -> dict:
    """
    Redeem one free premium day (non-cash reward).

    - Adds 24 hours of premium access
    - Cannot be converted to cash
    - Stacks with active subscription
    """
    return {
        "success": True,
        "data": {
            "user_id": token_data.user_id,
            "premium_day_redeemed": True,
            "premium_until": "2026-06-25T16:00:00Z",
            "remaining_days": 2
        },
        "error": None,
        "meta": {}
    }


@router.get("/giveaway-entries")
async def get_giveaway_entries(token_data: TokenData = Depends(get_current_user)) -> dict:
    """Get user's sponsor giveaway entries earned through streaks."""
    return {
        "success": True,
        "data": {
            "user_id": token_data.user_id,
            "total_entries": 12,
            "active_giveaways": [
                {
                    "id": "giveaway_1",
                    "sponsor": "Sponsor A",
                    "prize": "Cricket Gear Package",
                    "entries": 3,
                    "expires_at": "2026-07-01T23:59:59Z"
                }
            ]
        },
        "error": None,
        "meta": {}
    }


@router.get("/rank-history")
async def get_rank_history(token_data: TokenData = Depends(get_current_user)) -> dict:
    """Get user's rank progression history."""
    return {
        "success": True,
        "data": {
            "user_id": token_data.user_id,
            "current_rank": 42,
            "current_points": 1500,
            "rank_progression": [
                {
                    "rank": 50,
                    "points": 1000,
                    "date": "2026-06-15T10:30:00Z"
                },
                {
                    "rank": 45,
                    "points": 1200,
                    "date": "2026-06-18T14:20:00Z"
                }
            ]
        },
        "error": None,
        "meta": {}
    }
