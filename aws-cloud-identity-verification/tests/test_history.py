from src.app import lambda_handler
from tests.conftest import make_event, parse_response


def test_history_returns_recent_verifications(aws_mocks):
    aws_mocks["table"].query.return_value = {
        "Items": [
            {
                "user_id": "u1",
                "record_id": "2026-11-22T00:00:00Z#abc",
                "created_at": "2026-11-22T00:00:00Z",
                "verified": True,
                "similarity": 98.5,
                "liveness_confidence": 99.1,
            }
        ]
    }

    event = make_event(
        "GET /history/{user_id}",
        path_parameters={"user_id": "u1"},
    )
    event["queryStringParameters"] = {"limit": "20"}

    status, body = parse_response(
        lambda_handler(event, None)
    )

    assert status == 200
    assert body["user_id"] == "u1"
    assert len(body["items"]) == 1
    assert body["items"][0]["verified"] is True
