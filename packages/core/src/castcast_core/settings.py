"""Runtime settings, read from ``CASTCAST_*`` environment variables."""

from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Deployment environment. Each one maps to its own AWS stack."""

    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class Settings(BaseSettings):
    """Settings shared by every castcast component."""

    model_config = SettingsConfigDict(env_prefix="CASTCAST_", frozen=True)

    env: Environment = Environment.DEV
    aws_region: str = "us-east-2"
    data_bucket: str | None = Field(
        default=None,
        description="S3 bucket for the bronze/silver/gold lakehouse. None means local storage.",
    )
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings, built once from the environment."""
    return Settings()
