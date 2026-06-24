from fastapi import APIRouter
from app.models.prediction import PredictionCreate, Prediction

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.post("")
async def submit_prediction(prediction: PredictionCreate) -> dict:
    """Submit a game prediction (winner / top scorer / total runs / MOTM / first wicket)."""
    return {
        "success": True,
        "data": {
            "id": "pred_123",
            "match_id": prediction.match_id,
            "prediction_type": prediction.prediction_type,
            "prediction_value": prediction.prediction_value,
            "user_id": "user_123",
            "points": 0,
            "is_correct": False,
            "created_at": "2026-06-24T16:00:00Z",
            "settled_at": None
        },
        "error": None,
        "meta": {}
    }
