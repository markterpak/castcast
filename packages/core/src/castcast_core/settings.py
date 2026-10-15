"""Runtime settings, read from ``CASTCAST_*`` environment variables."""

from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    """Where castcast runs. ``dev`` and ``prod`` each map to their own AWS account (ADR 0004)."""

    LOCAL = "local"
    DEV = "dev"
    PROD = "prod"


class Settings(BaseSettings):
    """Settings shared by every castcast component."""

    model_config = SettingsConfigDict(env_prefix="CASTCAST_", frozen=True)

    env: Environment = Environment.LOCAL
    aws_region: str = "us-east-1"
    data_bucket: str | None = Field(
        default=None,
        description="S3 bucket for the bronze/silver/gold lakehouse. None means local storage.",
    )
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings, built once from the environment."""
    return Settings()
