import pytest
from pydantic import ValidationError

from castcast_core.settings import Environment, Settings


def test_defaults_to_local_with_local_storage(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CASTCAST_ENV", raising=False)
    monkeypatch.delenv("CASTCAST_DATA_BUCKET", raising=False)

    settings = Settings()

    assert settings.env is Environment.LOCAL
    assert settings.data_bucket is None


def test_reads_prefixed_environment_variables(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CASTCAST_ENV", "prod")
    monkeypatch.setenv("CASTCAST_DATA_BUCKET", "castcast-prod-data")

    settings = Settings()

    assert settings.env is Environment.PROD
    assert settings.data_bucket == "castcast-prod-data"


def test_rejects_unknown_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CASTCAST_ENV", "staging")

    with pytest.raises(ValidationError):
        Settings()
