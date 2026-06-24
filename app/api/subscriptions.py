from fastapi import APIRouter
from app.models.subscription import SubscriptionCreate, SubscriptionPlan

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("/plans")
async def get_subscription_plans() -> dict:
    """Get available subscription plans with pricing in poisha and BDT."""
    return {
        "success": True,
        "data": {
            "plans": [
                {
                    "id": "daily",
                    "name": "Daily",
                    "billing_cycle": "daily",
                    "price_poisha": 1000,
                    "price_bdt": 10.0,
                    "features": ["5 daily predictions", "basic analytics"],
                    "daily_predictions": 5,
                    "support_priority": "standard"
                },
                {
                    "id": "weekly",
                    "name": "Weekly",
                    "billing_cycle": "weekly",
                    "price_poisha": 5000,
                    "price_bdt": 50.0,
                    "features": ["15 daily predictions", "advanced analytics"],
                    "daily_predictions": 15,
                    "support_priority": "priority"
                },
                {
                    "id": "monthly_99",
                    "name": "Monthly (99)",
                    "billing_cycle": "monthly",
                    "price_poisha": 9900,
                    "price_bdt": 99.0,
                    "features": ["20 daily predictions", "advanced analytics"],
                    "daily_predictions": 20,
                    "support_priority": "priority"
                }
            ]
        },
        "error": None,
        "meta": {}
    }


@router.post("")
async def start_subscription(subscription: SubscriptionCreate) -> dict:
    """Start a subscription via bKash or telco billing."""
    return {
        "success": True,
        "data": {
            "id": "sub_123",
            "user_id": "user_123",
            "plan_id": subscription.plan_id,
            "billing_method": subscription.billing_method,
            "status": "pending",
            "started_at": "2026-06-24T16:00:00Z",
            "expires_at": "2026-06-25T16:00:00Z",
            "transaction_id": "txn_123"
        },
        "error": None,
        "meta": {}
    }
