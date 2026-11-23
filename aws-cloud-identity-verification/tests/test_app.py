import base64
import json
import os
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")

import src.app as app

def event(route, body=None, path_parameters=None):
    payload = {"routeKey": route}
    if body is not None:
        payload["body"] = json.dumps(body)
    if path_parameters is not None:
        payload["pathParameters"] = path_parameters
    return payload

@pytest.fixture(autouse=True)
def aws_mocks(monkeypatch):
    monkeypatch.setattr(app, "s3", MagicMock())
    monkeypatch.setattr(app, "rekognition", MagicMock())
    monkeypatch.setattr(app, "cloudwatch", MagicMock())
    table = MagicMock()
    monkeypatch.setattr(app, "_table", lambda: table)
    return table

def parse(response):
    return response["statusCode"], json.loads(response["body"])

def test_health():
    status, body = parse(app.lambda_handler(event("GET /health"), None))
    assert status == 200
    assert body["status"] == "ok"

def test_enroll_requires_one_face(aws_mocks):
    app.rekognition.detect_faces.return_value = {"FaceDetails": []}
    image = base64.b64encode(b"fake-jpeg").decode()
    status, body = parse(app.lambda_handler(event("POST /enroll", {"user_id": "u1", "image_base64": image}), None))
    assert status == 422
    assert "exactly one" in body["error"]

def test_enroll_success(aws_mocks):
    app.rekognition.detect_faces.return_value = {"FaceDetails": [{"BoundingBox": {}}]}
    image = base64.b64encode(b"fake-jpeg").decode()
    status, body = parse(app.lambda_handler(event("POST /enroll", {"user_id": "u1", "image_base64": image}), None))
    assert status == 201
    assert body["user_id"] == "u1"

def test_verify_rejects_failed_liveness(aws_mocks):
    app.rekognition.get_face_liveness_session_results.return_value = {"Status": "SUCCEEDED", "Confidence": 30.0}
    image = base64.b64encode(b"probe").decode()
    status, body = parse(app.lambda_handler(event("POST /verify", {"user_id": "u1", "image_base64": image, "liveness_session_id": "s1"}), None))
    assert status == 403
    assert body["reason"] == "liveness_failed"

def test_verify_success(aws_mocks):
    app.rekognition.get_face_liveness_session_results.return_value = {"Status": "SUCCEEDED", "Confidence": 99.2}
    aws_mocks.get_item.return_value = {"Item": {"user_id": "u1", "image_key": "reference/u1.jpg"}}
    app.rekognition.compare_faces.return_value = {"FaceMatches": [{"Similarity": 98.7}]}
    image = base64.b64encode(b"probe").decode()
    status, body = parse(app.lambda_handler(event("POST /verify", {"user_id": "u1", "image_base64": image, "liveness_session_id": "s1"}), None))
    assert status == 200
    assert body["verified"] is True

def test_verify_unenrolled_user(aws_mocks):
    app.rekognition.get_face_liveness_session_results.return_value = {"Status": "SUCCEEDED", "Confidence": 99.0}
    aws_mocks.get_item.return_value = {}
    image = base64.b64encode(b"probe").decode()
    status, body = parse(app.lambda_handler(event("POST /verify", {"user_id": "missing", "image_base64": image, "liveness_session_id": "s1"}), None))
    assert status == 404

def test_liveness_result():
    app.rekognition.get_face_liveness_session_results.return_value = {"Status": "SUCCEEDED", "Confidence": 97.4}
    status, body = parse(app.lambda_handler(event("GET /liveness/{session_id}", path_parameters={"session_id": "s1"}), None))
    assert status == 200
    assert body["passed"] is True
