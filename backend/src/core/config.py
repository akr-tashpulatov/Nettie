from typing import Callable, Literal, Optional

from dotenv import load_dotenv
from pydantic import EmailStr, Field, HttpUrl, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    APP_NAME: str
    APP_URL: HttpUrl

    CORS_ORIGINS: list[str] = ["*"]
    CORS_HEADERS: list[str] = ["*"]
    CORS_METHODS: list[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]

    ENVIRONMENT: Literal["production", "testing", "local"] = Field(default="local")
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int

    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_REGION: str = "us-east-1"
    AWS_S3_SECURE: bool
    AWS_S3_ENDPOINT: str
    AWS_S3_BUCKET_NAME: str
    AWS_S3_PUBLIC_ENDPOINT_URL: Optional[str] = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def AWS_S3_ENDPOINT_URL(self) -> str:
        scheme = "https" if self.AWS_S3_SECURE else "http"
        return f"{scheme}://{self.AWS_S3_ENDPOINT}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def AWS_S3_PRESIGN_ENDPOINT_URL(self) -> str:
        return self.AWS_S3_PUBLIC_ENDPOINT_URL or self.AWS_S3_ENDPOINT_URL

    DEBUG: bool = True
    JWT_ALGORITHM: str
    JWT_SECRET: str
    JWT_REFRESH_SECRET: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int

    MAIL_USERNAME: Optional[str] = None
    MAIL_PASSWORD: Optional[str] = None
    MAIL_FROM: EmailStr
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    MAIL_FROM_NAME: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    # AI explanation (student-facing "Explain this" feature)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_TIMEOUT_SECONDS: float = 30.0
    # Generated explanations are cached in Redis for a week — the concept behind
    # a question is stable, so re-asking the model on every click is wasteful.
    EXPLANATION_CACHE_TTL_SECONDS: int = 60 * 60 * 24 * 7

    # Rate limits
    RATE_LIMIT_DATABASE: int = 1
    RATE_LIMIT_HEADERS_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: list[str | Callable[..., str]] = ["100/minute"]

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def DATABASE_URL_SYNC(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    def REDIS_URL(self, database: Optional[int] = 0) -> str:
        return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{database}"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore[call-arg]
