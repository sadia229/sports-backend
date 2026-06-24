from pydantic import BaseModel
from typing import Any, Optional, Dict


class APIResponse(BaseModel):
    """Standard API response envelope."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    meta: Dict[str, Any] = {}


class ErrorDetail(BaseModel):
    """Error response detail."""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class ValidationError(APIResponse):
    """Validation error response."""
    success: bool = False
    error: str
    meta: Dict[str, Any] = {"validation_errors": {}}


# Standard error messages
ERRORS = {
    "UNAUTHORIZED": "Authentication required",
    "FORBIDDEN": "Permission denied",
    "NOT_FOUND": "Resource not found",
    "INVALID_INPUT": "Invalid input data",
    "RATE_LIMITED": "Too many requests",
    "INTERNAL_ERROR": "Internal server error",
    "PREMIUM_REQUIRED": "Premium subscription required",
    "MATCH_NOT_FOUND": "Match not found",
    "PREDICTION_NOT_FOUND": "Prediction not found",
    "INVALID_PREDICTION_TYPE": "Invalid prediction type",
    "MATCH_ALREADY_SETTLED": "Match already settled",
    "DAILY_LIMIT_EXCEEDED": "Daily prediction limit exceeded",
}
