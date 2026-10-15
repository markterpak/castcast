"""AWS Lambda entry point: adapts Lambda Function URL events to the ASGI app."""

from mangum import Mangum

from castcast_api.main import app
from castcast_core.logging import configure_logging
from castcast_core.settings import get_settings

configure_logging(get_settings().log_level)

handler = Mangum(app, lifespan="off")
