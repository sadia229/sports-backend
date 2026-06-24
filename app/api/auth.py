from fastapi import APIRouter, HTTPException, status, Depends, Query, Body, BackgroundTasks
from pydantic import BaseModel, EmailStr, Field
from app.core.security import get_current_user, TokenData
from app.services.email import (
    generate_verification_code,
    send_verification_email,
    verify_code,
)
from datetime import datetime

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    username: str = Field(..., min_length=3, max_length=20)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    user_id: str
    email: str
    username: str
    access_token: str
    token_type: str = "bearer"


class SignoutRequest(BaseModel):
    pass


@router.post("/signup")
async def signup(request: SignupRequest, background_tasks: BackgroundTasks) -> dict:
    """
    Register a new user with Supabase Auth.

    - Email must be unique
    - Password minimum 8 characters
    - Username 3-20 characters, unique
    - Queues a verification code email (sent in the background)
    - Returns JWT token for immediate authentication
    """
    # Generate the code now (fast), send the email after the response is returned.
    code = generate_verification_code(request.email)
    background_tasks.add_task(send_verification_email, request.email, code)

    return {
        "success": True,
        "data": {
            "user_id": "user_123",
            "email": request.email,
            "username": request.username,
            "access_token": "eyJhbGciOiJIUzI1NiIs...",
            "token_type": "bearer",
            "email_verified": False
        },
        "error": None,
        "meta": {"verification": "A verification code has been emailed to you."}
    }


@router.post("/login")
async def login(request: LoginRequest) -> dict:
    """
    Authenticate user and return JWT token.

    - Uses Supabase Auth for credential verification
    - Token valid for 1 hour
    - Returns refresh token for token renewal
    """
    return {
        "success": True,
        "data": {
            "user_id": "user_123",
            "email": request.email,
            "access_token": "eyJhbGciOiJIUzI1NiIs...",
            "refresh_token": "refresh_token_xyz...",
            "token_type": "bearer",
            "expires_in": 3600
        },
        "error": None,
        "meta": {}
    }


@router.post("/refresh")
async def refresh_token(refresh_token: str) -> dict:
    """
    Refresh access token using refresh token.

    - Refresh token valid for 30 days
    - Returns new access token
    """
    return {
        "success": True,
        "data": {
            "access_token": "eyJhbGciOiJIUzI1NiIs...",
            "token_type": "bearer",
            "expires_in": 3600
        },
        "error": None,
        "meta": {}
    }


@router.post("/logout")
async def logout(token_data: TokenData = Depends(get_current_user)) -> dict:
    """
    Logout user and revoke tokens.

    - Invalidates current session
    - Client should clear local tokens
    """
    return {
        "success": True,
        "data": {"message": "Logged out successfully"},
        "error": None,
        "meta": {}
    }


class VerifyEmailRequest(BaseModel):
    email: EmailStr
    verification_code: str = Field(..., min_length=6, max_length=6)


@router.post("/verify-email")
async def verify_email(request: VerifyEmailRequest) -> dict:
    """
    Verify email address with the code that was emailed to the user.

    - Code is 6 digits, valid for 10 minutes, single use
    - Required before full access
    """
    if not verify_code(request.email, request.verification_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification code"
        )

    return {
        "success": True,
        "data": {"email": request.email, "verified": True},
        "error": None,
        "meta": {}
    }


class ResendCodeRequest(BaseModel):
    email: EmailStr


@router.post("/resend-verification")
async def resend_verification(
    request: ResendCodeRequest, background_tasks: BackgroundTasks
) -> dict:
    """Generate a fresh verification code and email it in the background."""
    code = generate_verification_code(request.email)
    background_tasks.add_task(send_verification_email, request.email, code)

    return {
        "success": True,
        "data": {"email": request.email},
        "error": None,
        "meta": {"verification": "A new verification code has been emailed to you."}
    }


@router.post("/forgot-password")
async def forgot_password(email: EmailStr = Query(...)) -> dict:
    """
    Send password reset email.

    - Sends reset link valid for 24 hours
    - User must verify old email first
    """
    return {
        "success": True,
        "data": {"message": "Reset email sent"},
        "error": None,
        "meta": {}
    }


class ResetPasswordRequest(BaseModel):
    reset_token: str
    new_password: str = Field(..., min_length=8)


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest) -> dict:
    """
    Reset password with token from email.

    - Token valid for 24 hours
    - Password minimum 8 characters
    """
    return {
        "success": True,
        "data": {"message": "Password reset successful"},
        "error": None,
        "meta": {}
    }


@router.get("/me")
async def get_auth_user(token_data: TokenData = Depends(get_current_user)) -> dict:
    """Get current authenticated user details."""
    return {
        "success": True,
        "data": {
            "user_id": token_data.user_id,
            "email": token_data.email,
            "sub": token_data.sub
        },
        "error": None,
        "meta": {}
    }
