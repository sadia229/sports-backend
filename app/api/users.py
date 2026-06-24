from fastapi import APIRouter, Query
from app.models.user import UserProfile, UserPoints, UserAccuracy

router = APIRouter(tags=["users"])


@router.get("/leaderboard")
async def get_leaderboard(limit: int = Query(10, ge=1, le=100)) -> dict:
    """Get ranked users by points and accuracy."""
    return {
        "success": True,
        "data": {
            "users": [],
            "total_users": 0
        },
        "error": None,
        "meta": {"limit": limit}
    }


@router.get("/me")
async def get_profile() -> dict:
    """Get current user profile."""
    return {
        "success": True,
        "data": {
            "id": "user_123",
            "email": "user@example.com",
            "username": "player_123",
            "total_points": 1500,
            "accuracy_percentage": 62.5,
            "streak": 5,
            "rank": 42,
            "premium_until": None
        },
        "error": None,
        "meta": {}
    }


@router.get("/me/points")
async def get_user_points() -> dict:
    """Get user points and streak statistics."""
    return {
        "success": True,
        "data": {
            "user_id": "user_123",
            "total_points": 1500,
            "today_points": 50,
            "week_points": 300,
            "month_points": 800,
            "streak": 5,
            "streak_frozen": False
        },
        "error": None,
        "meta": {}
    }


@router.get("/me/accuracy")
async def get_user_accuracy() -> dict:
    """Get user accuracy statistics."""
    return {
        "success": True,
        "data": {
            "user_id": "user_123",
            "total_predictions": 100,
            "correct_predictions": 62,
            "accuracy_percentage": 62.0,
            "best_streak": 8,
            "current_streak": 5
        },
        "error": None,
        "meta": {}
    }
