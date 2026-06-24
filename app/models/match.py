from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class MatchBase(BaseModel):
    league: str
    team_a: str
    team_b: str
    status: str
    scheduled_at: datetime


class Match(MatchBase):
    id: str
    created_at: datetime


class PredictionFactor(BaseModel):
    factor: str
    impact: float
    description: str


class WinProbability(BaseModel):
    team_a_probability: float
    team_b_probability: float
    confidence: str
    key_factors: List[PredictionFactor]


class WatchTarget(BaseModel):
    provider: str
    name: str
    url: str
    region: str


class MatchPrediction(BaseModel):
    match_id: str
    win_probability: WinProbability
    expected_score: dict
