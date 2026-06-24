from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class SubscriptionPlan(BaseModel):
    id: str
    name: str
    billing_cycle: Literal["daily", "weekly", "monthly"]
    price_poisha: int
    price_bdt: float
    features: list[str]
    daily_predictions: int
    support_priority: str


class SubscriptionCreate(BaseModel):
    plan_id: str
    billing_method: Literal["bkash", "telco"]


class Subscription(SubscriptionCreate):
    id: str
    user_id: str
    status: Literal["active", "pending", "cancelled", "expired"]
    started_at: datetime
    expires_at: datetime
    transaction_id: str = None
