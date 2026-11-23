import base64
import binascii
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

TABLE_NAME = os.environ.get("TABLE_NAME", "IdentityUsers")
IMAGE_BUCKET = os.environ.get("IMAGE_BUCKET", "identity-reference-images")
MATCH_THRESHOLD = float(os.environ.get("MATCH_THRESHOLD", "90"))
LIVENESS_THRESHOLD = float(os.environ.get("LIVENESS_THRESHOLD", "90"))
MAX_IMAGE_BYTES = int(os.environ.get("MAX_IMAGE_BYTES", str(5 * 1024 * 1024)))

s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")
dynamodb = boto3.resource("dynamodb")
cloudwatch = boto3.client("cloudwatch")

def _response(status: int, body: Dict[str, Any]) -> Dict[str, Any]:
    return {"statusCode": status, "headers": {"Content-Type": "application/json", "Cache-Control": "no-store"}, "body": json.dumps(body)}

def _parse_json_body(event: Dict[str, Any]) -> Dict[str, Any]:
    body = event.get("body")
    if not body:
        return {}
    if event.get("isBase64Encoded"):
        body = base64.b64decode(body).decode("utf-8")
    if isinstance(body, dict):
        return body
    try:
        return json.loads(body)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Request body must be valid JSON") from exc

def _decode_image(image_base64: str) -> bytes:
    if not image_base64:
        raise ValueError("image_base64 is required")
    if "," in image_base64 and image_base64.split(",", 1)[0].startswith("data:"):
        image_base64 = image_base64.split(",", 1)[1]
    try:
        image = base64.b64decode(image_base64, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("image_base64 is not valid base64") from exc
    if not image:
        raise ValueError("Decoded image is empty")
    if len(image) > MAX_IMAGE_BYTES:
        raise ValueError(f"Image exceeds {MAX_IMAGE_BYTES} byte limit")
    return image

def _emit_metric(name: str, value: float = 1.0) -> None:
    try:
        cloudwatch.put_metric_data(Namespace="CloudIdentityVerification", MetricData=[{"MetricName": name, "Value": value, "Unit": "Count"}])
    except ClientError:
        logger.exception("Unable to emit CloudWatch metric", extra={"metric": name})

def _table():
    return dynamodb.Table(TABLE_NAME)

def health(_: Dict[str, Any]) -> Dict[str, Any]:
    return _response(200, {"status": "ok", "service": "cloud-identity-verification"})

def enroll(event: Dict[str, Any]) -> Dict[str, Any]:
    body = _parse_json_body(event)
    user_id = str(body.get("user_id", "")).strip()
    if not user_id:
        return _response(400, {"error": "user_id is required"})
    image = _decode_image(body.get("image_base64", ""))
    image_key = f"reference/{user_id}.jpg"
    detection = rekognition.detect_faces(Image={"Bytes": image}, Attributes=["DEFAULT"])
    if len(detection.get("FaceDetails", [])) != 1:
        return _response(422, {"error": "Enrollment image must contain exactly one detectable face"})
    s3.put_object(Bucket=IMAGE_BUCKET, Key=image_key, Body=image, ContentType="image/jpeg", ServerSideEncryption="AES256")
    enrolled_at = datetime.now(timezone.utc).isoformat()
    _table().put_item(Item={"user_id": user_id, "image_key": image_key, "enrolled_at": enrolled_at})
    _emit_metric("EnrollmentSuccess")
    return _response(201, {"user_id": user_id, "enrolled_at": enrolled_at})

def create_liveness_session(_: Dict[str, Any]) -> Dict[str, Any]:
    result = rekognition.create_face_liveness_session()
    return _response(201, {"session_id": result["SessionId"]})

def get_liveness_result(event: Dict[str, Any]) -> Dict[str, Any]:
    session_id = (event.get("pathParameters") or {}).get("session_id")
    if not session_id:
        return _response(400, {"error": "session_id is required"})
    result = rekognition.get_face_liveness_session_results(SessionId=session_id)
    confidence = float(result.get("Confidence", 0.0))
    status = result.get("Status", "UNKNOWN")
    passed = status == "SUCCEEDED" and confidence >= LIVENESS_THRESHOLD
    if not passed:
        _emit_metric("LivenessFailure")
    return _response(200, {"session_id": session_id, "status": status, "confidence": round(confidence, 2), "threshold": LIVENESS_THRESHOLD, "passed": passed})

def _validate_liveness(session_id: Optional[str]) -> Dict[str, Any]:
    if not session_id:
        return {"passed": False, "reason": "liveness_session_id is required"}
    result = rekognition.get_face_liveness_session_results(SessionId=session_id)
    confidence = float(result.get("Confidence", 0.0))
    status = result.get("Status", "UNKNOWN")
    return {"passed": status == "SUCCEEDED" and confidence >= LIVENESS_THRESHOLD, "status": status, "confidence": round(confidence, 2)}

def verify(event: Dict[str, Any]) -> Dict[str, Any]:
    body = _parse_json_body(event)
    user_id = str(body.get("user_id", "")).strip()
    if not user_id:
        return _response(400, {"error": "user_id is required"})
    image = _decode_image(body.get("image_base64", ""))
    liveness = _validate_liveness(body.get("liveness_session_id"))
    if not liveness.get("passed"):
        _emit_metric("SpoofOrLivenessFailure")
        return _response(403, {"verified": False, "reason": "liveness_failed", "liveness": liveness})
    item = _table().get_item(Key={"user_id": user_id}).get("Item")
    if not item:
        return _response(404, {"error": "user is not enrolled"})
    comparison = rekognition.compare_faces(SourceImage={"S3Object": {"Bucket": IMAGE_BUCKET, "Name": item["image_key"]}}, TargetImage={"Bytes": image}, SimilarityThreshold=MATCH_THRESHOLD, QualityFilter="AUTO")
    similarity = max((float(m.get("Similarity", 0.0)) for m in comparison.get("FaceMatches", [])), default=0.0)
    verified = similarity >= MATCH_THRESHOLD
    _emit_metric("VerificationSuccess" if verified else "VerificationFailure")
    return _response(200, {"user_id": user_id, "verified": verified, "similarity": round(similarity, 2), "match_threshold": MATCH_THRESHOLD, "liveness": liveness})

def lambda_handler(event: Dict[str, Any], _context: Any) -> Dict[str, Any]:
    route = event.get("routeKey") or f"{event.get('httpMethod', '')} {event.get('resource', '')}".strip()
    routes = {"GET /health": health, "POST /enroll": enroll, "POST /verify": verify, "POST /liveness/session": create_liveness_session, "GET /liveness/{session_id}": get_liveness_result}
    handler = routes.get(route)
    if not handler:
        return _response(404, {"error": "route not found", "route": route})
    try:
        return handler(event)
    except ValueError as exc:
        return _response(400, {"error": str(exc)})
    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "AWSClientError")
        _emit_metric("ServiceError")
        return _response(502, {"error": "AWS service request failed", "code": error_code})
    except Exception:
        logger.exception("Unhandled service error")
        _emit_metric("ServiceError")
        return _response(500, {"error": "internal server error"})
