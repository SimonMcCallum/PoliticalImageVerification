import secrets
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "NZ Political Image Verification"
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://pivs:pivs_secret@localhost:5432/pivs"

    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"

    # Encryption - in production, use HSM/KMS. This is the master KEK.
    MASTER_ENCRYPTION_KEY: str = secrets.token_hex(32)

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

    # Rate limiting
    RATE_LIMIT_VERIFY_PER_MINUTE: int = 30
    RATE_LIMIT_SUBMIT_PER_MINUTE: int = 10

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
