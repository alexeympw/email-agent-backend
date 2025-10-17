from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    redis_url: str = Field(alias="REDIS_URL")
    encryption_key: str = Field(alias="ENCRYPTION_KEY")
    smtp_default_from: str | None = Field(default=None, alias="SMTP_DEFAULT_FROM")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()  # type: ignore[arg-type]
