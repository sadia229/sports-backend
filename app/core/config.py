from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Supabase Configuration.
    # Default to empty so the app can still boot (docs/health) when a deploy is
    # missing env vars — routes that actually need Supabase raise a clear error
    # at call time instead of crashing the whole serverless function at import.
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    @property
    def supabase_configured(self) -> bool:
        return bool(self.SUPABASE_URL and self.SUPABASE_SERVICE_ROLE_KEY)

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379"

    # API Configuration
    VENDOR_API_KEY: Optional[str] = None

    # bKash Billing Credentials
    BKASH_APP_KEY: Optional[str] = None
    BKASH_APP_SECRET: Optional[str] = None
    BKASH_USERNAME: Optional[str] = None
    BKASH_PASSWORD: Optional[str] = None

    # SMTP / Email Configuration (verification codes, password resets)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM: str = "no-reply@aimatchpredictor.com"
    SMTP_USE_TLS: bool = True

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API Contract Version
    API_VERSION: str = "2.0.0"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
