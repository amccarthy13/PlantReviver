from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    environment: str = "dev"

    # Database
    database_url: str = (
        "postgresql+asyncpg://plantreviver:plantreviver@localhost:5432/plantreviver"
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    # Auth
    jwt_secret: str = "dev-insecure-change-me"
    jwt_algorithm: str = "HS256"
    access_token_ttl_seconds: int = 3600
    refresh_token_ttl_seconds: int = 60 * 60 * 24 * 30
    apple_bundle_id: str = "com.example.plantreviver"

    # Premium integrations (optional until built)
    anthropic_api_key: str | None = None
    openweather_api_key: str | None = None

    # Object storage (R2)
    r2_account_id: str | None = None
    r2_access_key_id: str | None = None
    r2_secret_access_key: str | None = None
    r2_bucket: str | None = None

    # Rate limiting (slowapi; in-memory now, Redis when multi-instance) — §12
    rate_limit_default: str = "200/minute"

    # AI cost circuit breaker (§12) — instant manual kill switch
    ai_enabled: bool = True

    # Admin dashboard (SQLAdmin). MUST be overridden with strong values in prod.
    admin_username: str = "admin"
    admin_password: str = "change-me-admin"
    admin_session_secret: str = "dev-insecure-admin-session-secret"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
