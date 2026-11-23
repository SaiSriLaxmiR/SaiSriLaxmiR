from src.app import lambda_handler
from tests.conftest import make_event, parse_response


def test_health():
    status, body = parse_response(
        lambda_handler(make_event("GET /health"), None)
    )
    assert status == 200
    assert body["status"] == "ok"


def test_unknown_route():
    status, body = parse_response(
        lambda_handler(make_event("GET /missing"), None)
    )
    assert status == 404
    assert body["error"] == "route not found"
