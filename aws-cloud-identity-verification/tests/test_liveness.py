from src.app import lambda_handler
from tests.conftest import make_event, parse_response


def test_create_liveness_session(aws_mocks):
    aws_mocks[
        "rekognition"
    ].create_face_liveness_session.return_value = {
        "SessionId": "abc"
    }
    status, body = parse_response(
        lambda_handler(
            make_event("POST /liveness/session"),
            None,
        )
    )
    assert status == 201
    assert body["session_id"] == "abc"


def test_get_liveness_result(aws_mocks):
    aws_mocks[
        "rekognition"
    ].get_face_liveness_session_results.return_value = {
        "Status": "SUCCEEDED",
        "Confidence": 97.4,
    }
    status, body = parse_response(
        lambda_handler(
            make_event(
                "GET /liveness/{session_id}",
                path_parameters={"session_id": "s1"},
            ),
            None,
        )
    )
    assert status == 200
    assert body["passed"] is True
