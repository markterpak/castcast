"""FastAPI application. Routes for scores, predictions and catches arrive in Phase 5."""

from importlib.metadata import version

from fastapi import FastAPI
from pydantic import BaseModel

from castcast_core.settings import Environment, get_settings


class Health(BaseModel):
    status: str
    env: Environment
    version: str


app = FastAPI(title="castcast API", version=version("castcast-api"))


@app.get("/health")
def health() -> Health:
    """Liveness check used by deploy smoke tests."""
    return Health(status="ok", env=get_settings().env, version=app.version)
