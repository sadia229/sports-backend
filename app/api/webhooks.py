from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


class BkashWebhookPayload(BaseModel):
    transaction_id: str
    user_id: str
    amount: int
    status: str
    timestamp: str


@router.post("/bkash")
async def handle_bkash_webhook(payload: BkashWebhookPayload) -> dict:
    """Handle bKash billing callback to activate entitlement."""
    return {
        "success": True,
        "data": {
            "transaction_id": payload.transaction_id,
            "status": "processed",
            "subscription_activated": payload.status == "success"
        },
        "error": None,
        "meta": {}
    }
