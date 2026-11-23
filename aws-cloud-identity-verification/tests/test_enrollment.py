from src.app import lambda_handler
from tests.conftest import b64, make_event, parse_response


def test_enrollment_requires_exactly_one_face(aws_mocks):
    aws_mocks["rekognition"].detect_faces.return_value = {
        "FaceDetails": []
    }
    status, body = parse_response(
        lambda_handler(
            make_event(
                "POST /enroll",
                {
                    "user_id": "u1",
                    "image_base64": b64(),
                },
            ),
            None,
        )
    )
    assert status == 422
    assert "exactly one" in body["error"]


def test_enrollment_success(aws_mocks):
    aws_mocks["rekognition"].detect_faces.return_value = {
        "FaceDetails": [{}]
    }
    status, body = parse_response(
        lambda_handler(
            make_event(
                "POST /enroll",
                {
                    "user_id": "u1",
                    "image_base64": b64(),
                },
            ),
            None,
        )
    )
    assert status == 201
    assert body["user_id"] == "u1"
    aws_mocks["s3"].put_object.assert_called_once()
    aws_mocks["table"].put_item.assert_called_once()
