import json
from dataclasses import dataclass
from typing import Any

from mangum.types import LambdaCognitoIdentity, LambdaMobileClientContext

from castcast_api.handler import handler


def _function_url_event(path: str) -> dict[str, Any]:
    """A minimal Lambda Function URL event (payload format 2.0)."""
    return {
        "version": "2.0",
        "routeKey": "$default",
        "rawPath": path,
        "rawQueryString": "",
        "headers": {"host": "example.lambda-url.us-east-1.on.aws"},
        "requestContext": {
            "http": {"method": "GET", "path": path, "protocol": "HTTP/1.1", "sourceIp": "1.2.3.4"},
            "stage": "$default",
        },
        "isBase64Encoded": False,
    }


@dataclass
class FakeLambdaContext:
    """Satisfies Mangum's LambdaContext protocol without a real Lambda runtime."""

    function_name: str = "castcast-api-test"
    function_version: str = "$LATEST"
    invoked_function_arn: str = "arn:aws:lambda:us-east-1:000000000000:function:castcast-api-test"
    memory_limit_in_mb: int = 512
    aws_request_id: str = "test-request"
    log_group_name: str = "/aws/lambda/castcast-api-test"
    log_stream_name: str = "test-stream"
    identity: LambdaCognitoIdentity | None = None
    client_context: LambdaMobileClientContext | None = None

    def get_remaining_time_in_millis(self) -> int:
        return 30_000


def test_lambda_handler_serves_health_route() -> None:
    response = handler(_function_url_event("/health"), FakeLambdaContext())

    assert response["statusCode"] == 200
    assert json.loads(response["body"])["status"] == "ok"
