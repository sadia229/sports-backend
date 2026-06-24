from pydantic import BaseModel
from typing import Literal
from datetime import datetime


class PredictionCreate(BaseModel):
    match_id: str
    prediction_type: Literal["winner", "top_scorer", "total_runs", "motm", "first_wicket"]
    prediction_value: str


class Prediction(PredictionCreate):
    id: str
    user_id: str
    points: int = 0
    is_correct: bool = False
    created_at: datetime
    settled_at: datetime = None
