from fastapi import HTTPException, Depends, status, Header
from datetime import datetime, timedelta
from typing import Optional
from app.core.config import settings


class TokenData:
    def __init__(self, sub: str, user_id: str, email: str = None):
        self.sub = sub
        self.user_id = user_id
        self.email = email


async def get_current_user(authorization: Optional[str] = Header(None)) -> TokenData:
    """
    Dependency to get current authenticated user from JWT token.

    Extract Bearer token from Authorization header.
    In production, verify with Supabase public key.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization scheme"
            )

        # In production: verify with Supabase
        # For now: mock verification
        user_id = "user_123"  # Extract from token in production
        email = "user@example.com"

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return TokenData(sub=user_id, user_id=user_id, email=email)

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def require_premium(token_data: TokenData = Depends(get_current_user)) -> TokenData:
    """Verify user has active premium subscription."""
    # TODO: Check user's subscription status in database
    return token_data
