from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class UserProfile(BaseModel):
    id: str
    email: str
    username: str
    total_points: int
    accuracy_percentage: float
    streak: int
    rank: int
    premium_until: Optional[datetime] = None


class UserPoints(BaseModel):
    user_id: str
    total_points: int
    today_points: int
    week_points: int
    month_points: int
    streak: int
    streak_frozen: bool


class UserAccuracy(BaseModel):
    user_id: str
    total_predictions: int
    correct_predictions: int
    accuracy_percentage: float
    best_streak: int
    current_streak: int
