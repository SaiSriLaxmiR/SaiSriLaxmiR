from src.app import lambda_handler
from tests.conftest import b64, make_event, parse_response


def test_verify_rejects_failed_liveness(aws_mocks):
    aws_mocks[
        "rekognition"
    ].get_face_liveness_session_results.return_value = {
        "Status": "SUCCEEDED",
        "Confidence": 30.0,
    }

    status, body = parse_response(
        lambda_handler(
            make_event(
                "POST /verify",
                {
                    "user_id": "u1",
                    "image_base64": b64(b"probe"),
                    "liveness_session_id": "s1",
                },
            ),
            None,
        )
    )

    assert status == 403
    assert body["reason"] == "liveness_failed"


def test_verify_success(aws_mocks):
    aws_mocks[
        "rekognition"
    ].get_face_liveness_session_results.return_value = {
        "Status": "SUCCEEDED",
        "Confidence": 99.2,
    }
    aws_mocks["table"].get_item.return_value = {
        "Item": {
            "user_id": "u1",
            "image_key": "reference/u1.jpg",
        }
    }
    aws_mocks["rekognition"].compare_faces.return_value = {
        "FaceMatches": [{"Similarity": 98.7}]
    }

    status, body = parse_response(
        lambda_handler(
            make_event(
                "POST /verify",
                {
                    "user_id": "u1",
                    "image_base64": b64(b"probe"),
                    "liveness_session_id": "s1",
                },
            ),
            None,
        )
    )

    assert status == 200
    assert body["verified"] is True


def test_verify_unenrolled_user(aws_mocks):
    aws_mocks[
        "rekognition"
    ].get_face_liveness_session_results.return_value = {
        "Status": "SUCCEEDED",
        "Confidence": 99.0,
    }
    aws_mocks["table"].get_item.return_value = {}

    status, body = parse_response(
        lambda_handler(
            make_event(
                "POST /verify",
                {
                    "user_id": "missing",
                    "image_base64": b64(b"probe"),
                    "liveness_session_id": "s1",
                },
            ),
            None,
        )
    )

    assert status == 404
