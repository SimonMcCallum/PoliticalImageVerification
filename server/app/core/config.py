"""Runtime settings.

Two security-critical values (``SECRET_KEY`` and ``MASTER_ENCRYPTION_KEY``)
must be supplied from the environment in production. If they are not,
the application refuses to start rather than silently generating fresh
per-process values which would invalidate every JWT on the next restart
and (worse) leave previously-encrypted database content unrecoverable.

Set ``PIVS_ENV=test`` to allow ephemeral defaults for unit tests; the
test conftest already sets both values explicitly so the only place
this matters is during local manual hacking. Anything other than
``test`` or ``development`` is treated as production.
"""

import os
import secrets

from pydantic import field_validator
from pydantic_settings import BaseSettings


def _is_test_or_dev() -> bool:
    env = os.environ.get("PIVS_ENV", "").lower()
    return env in ("test", "development", "dev")


def _require_env(name: str) -> str:
    """Demand an env var. Returns the value or raises at import time."""
    val = os.environ.get(name)
    if val:
        return val
    if _is_test_or_dev():
        # Ephemeral fallback ONLY for development/tests.
        return (
            secrets.token_urlsafe(32) if name == "SECRET_KEY" else secrets.token_hex(32)
        )
    raise RuntimeError(
        f"Required environment variable {name} is not set. "
        f"Refusing to start in production mode without it. "
        f"Set PIVS_ENV=development to allow an ephemeral default."
    )


class Settings(BaseSettings):
    PROJECT_NAME: str = "NZ Political Image Verification"
    API_V1_PREFIX: str = "/api/v1"

    # Deployment environment. Anything other than "test"/"development"
    # requires SECRET_KEY and MASTER_ENCRYPTION_KEY to be set in env.
    PIVS_ENV: str = "production"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://pivs:pivs_secret@localhost:5432/pivs"

    # Security: NEVER allow these to silently default in production.
    SECRET_KEY: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # Encryption master KEK. In production, source from HSM/KMS.
    MASTER_ENCRYPTION_KEY: str = ""

    # Storage
    STORAGE_BACKEND: str = "local"  # "local" or "s3"
    LOCAL_STORAGE_PATH: str = "./storage"
    S3_BUCKET: str = ""
    S3_ENDPOINT: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""

    # Verification
    PDQ_MATCH_THRESHOLD: int = 31
    PHASH_MATCH_THRESHOLD: int = 10
    VERIFICATION_BASE_URL: str = "http://localhost:3000/verify"

    # Badge
    BADGE_MAX_AREA_PERCENT: float = 5.0
    BADGE_DEFAULT_POSITION: str = "bottom-right"

    # Promoter Statement
    PROMOTER_MIN_FONT_SIZE: int = 12
    PROMOTER_WCAG_CONTRAST_RATIO: float = 4.5
    PROMOTER_OCR_MATCH_THRESHOLD: float = 0.8

    # Email Processing
    EMAIL_PROCESSING_ENABLED: bool = False
    EMAIL_IMAP_HOST: str = ""
    EMAIL_IMAP_PORT: int = 993
    EMAIL_IMAP_USER: str = ""
    EMAIL_IMAP_PASSWORD: str = ""
    EMAIL_SMTP_HOST: str = ""
    EMAIL_SMTP_PORT: int = 587
    EMAIL_SMTP_USER: str = ""
    EMAIL_SMTP_PASSWORD: str = ""
    EMAIL_PROCESSING_ADDRESS: str = ""
    EMAIL_POLL_INTERVAL_SECONDS: int = 30
    EMAIL_VERIFICATION_EXPIRE_MINUTES: int = 30
    EMAIL_SENDING_ENABLED: bool = True

    # Password reset
    PASSWORD_RESET_EXPIRE_MINUTES: int = 60

    # Rate limiting
    RATE_LIMIT_VERIFY_PER_MINUTE: int = 30
    RATE_LIMIT_SUBMIT_PER_MINUTE: int = 10

    # Extension report/flag rate limiting (per-IP per minute)
    RATE_LIMIT_EXTENSION_REPORT_PER_MINUTE: int = 60
    RATE_LIMIT_EXTENSION_FLAG_PER_MINUTE: int = 10

    # CORS
    # Comma-separated list of additional allowed origins beyond the default
    # localhost dev set and the derived VERIFICATION_BASE_URL origin.
    CORS_EXTRA_ORIGINS: str = ""

    # Privacy / IPP 12. Geolocation of public verifications is disabled
    # by default. The previous implementation called ip-api.com over
    # plain HTTP, which is a cross-border disclosure of personal
    # information. Re-enable only when an in-process, NZ-resident
    # offline database (eg. MaxMind GeoLite2) is in place.
    GEO_LOOKUP_ENABLED: bool = False

    model_config = {"env_file": ".env", "extra": "ignore"}

    @field_validator("SECRET_KEY", mode="before")
    @classmethod
    def _resolve_secret_key(cls, v: str) -> str:
        return v or _require_env("SECRET_KEY")

    @field_validator("MASTER_ENCRYPTION_KEY", mode="before")
    @classmethod
    def _resolve_master_key(cls, v: str) -> str:
        return v or _require_env("MASTER_ENCRYPTION_KEY")


settings = Settings()
