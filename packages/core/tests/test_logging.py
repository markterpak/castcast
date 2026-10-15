import json
import logging
import sys
from collections.abc import Iterator

import pytest

from castcast_core.logging import JsonFormatter, configure_logging


def _record(**extra: object) -> logging.LogRecord:
    record = logging.makeLogRecord({"name": "castcast.test", "levelname": "INFO", "msg": "hi %s"})
    record.args = ("there",)
    for key, value in extra.items():
        setattr(record, key, value)
    return record


def test_formats_record_as_json_with_message_args_applied() -> None:
    payload = json.loads(JsonFormatter().format(_record()))

    assert payload["message"] == "hi there"
    assert payload["level"] == "INFO"
    assert payload["logger"] == "castcast.test"
    assert payload["timestamp"].endswith("+00:00")


def test_includes_extra_fields() -> None:
    payload = json.loads(JsonFormatter().format(_record(source="ny_dec", rows=42)))

    assert payload["source"] == "ny_dec"
    assert payload["rows"] == 42


def test_includes_exception_traceback() -> None:
    try:
        raise ValueError("boom")
    except ValueError:
        record = logging.makeLogRecord({"msg": "failed", "levelname": "ERROR"})
        record.exc_info = sys.exc_info()

    payload = json.loads(JsonFormatter().format(record))

    assert "ValueError: boom" in payload["exception"]


@pytest.fixture
def restore_root_logger() -> Iterator[None]:
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    yield
    root.handlers[:] = handlers
    root.setLevel(level)


@pytest.mark.usefixtures("restore_root_logger")
def test_configure_logging_replaces_handlers_and_is_idempotent(
    capsys: pytest.CaptureFixture[str],
) -> None:
    configure_logging("DEBUG")
    configure_logging("DEBUG")

    logging.getLogger("castcast.test").debug("ready", extra={"stage": "bronze"})

    lines = capsys.readouterr().err.strip().splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0])["stage"] == "bronze"
