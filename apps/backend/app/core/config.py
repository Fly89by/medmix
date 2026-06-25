from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "MED.MIX OS"
    debug: bool = True
    secret_key: str = "change-this-to-a-random-secret-key"

    # Database (accept postgresql:// or postgresql+asyncpg://)
    database_url: str = "postgresql+asyncpg://medmix:medmix_pass@localhost:5432/medmix_db"

    @property
    def async_database_url(self) -> str:
        url = self.database_url
        for prefix in ("postgresql://", "postgres://"):
            if url.startswith(prefix):
                suffix = url[len(prefix):]
                return f"postgresql+asyncpg://{suffix}"
        return url

    # JWT
    jwt_secret_key: str = "change-this-to-a-random-jwt-secret"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # File storage (local filesystem, use Railway Volume in production)
    upload_dir: str = "/app/uploads"

    # MinIO (legacy, kept for compatibility)
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "medmix"
    minio_secret_key: str = "medmix_secret"
    minio_bucket: str = "medmix-storage"
    minio_use_ssl: bool = False

    # OpenAI (optional)
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o-mini"

    # Google Maps (optional - simulation mode if empty)
    google_maps_api_key: Optional[str] = None

    # Email / SMTP (optional - notifications disabled if empty)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None

    model_config = {"env_file": ".env", "case_sensitive": False}


settings = Settings()
