from typing import Any, Dict, Optional

from src import aws_clients
from src.config import IMAGE_BUCKET, LIVENESS_THRESHOLD, MATCH_THRESHOLD


def has_exactly_one_face(image: bytes) -> bool:
    result = aws_clients.rekognition.detect_faces(
        Image={"Bytes": image},
        Attributes=["DEFAULT"],
    )
    return len(result.get("FaceDetails", [])) == 1


def create_liveness_session() -> str:
    result = aws_clients.rekognition.create_face_liveness_session()
    return result["SessionId"]


def get_liveness_result(session_id: str) -> Dict[str, Any]:
    result = aws_clients.rekognition.get_face_liveness_session_results(
        SessionId=session_id
    )
    confidence = float(result.get("Confidence", 0.0))
    status = result.get("Status", "UNKNOWN")
    return {
        "session_id": session_id,
        "status": status,
        "confidence": round(confidence, 2),
        "threshold": LIVENESS_THRESHOLD,
        "passed": status == "SUCCEEDED" and confidence >= LIVENESS_THRESHOLD,
    }


def validate_liveness(session_id: Optional[str]) -> Dict[str, Any]:
    if not session_id:
        return {
            "passed": False,
            "reason": "liveness_session_id is required",
        }

    result = get_liveness_result(session_id)
    return {
        "passed": result["passed"],
        "status": result["status"],
        "confidence": result["confidence"],
    }


def compare_with_reference(image_key: str, probe_image: bytes) -> float:
    result = aws_clients.rekognition.compare_faces(
        SourceImage={
            "S3Object": {
                "Bucket": IMAGE_BUCKET,
                "Name": image_key,
            }
        },
        TargetImage={"Bytes": probe_image},
        SimilarityThreshold=MATCH_THRESHOLD,
        QualityFilter="AUTO",
    )
    return max(
        (
            float(match.get("Similarity", 0.0))
            for match in result.get("FaceMatches", [])
        ),
        default=0.0,
    )
