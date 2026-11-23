from typing import Any, Dict

from src.config import MATCH_THRESHOLD
from src.services.metrics import emit_metric
from src.services.rekognition_service import (
    compare_with_reference,
    validate_liveness,
)
from src.services.storage import get_enrollment
from src.utils.http import parse_json_body, response
from src.utils.validation import decode_image, require_user_id


def handle_verify(event: Dict[str, Any]) -> Dict[str, Any]:
    body = parse_json_body(event)
    user_id = require_user_id(body.get("user_id"))
    image = decode_image(body.get("image_base64", ""))

    liveness = validate_liveness(body.get("liveness_session_id"))
    if not liveness.get("passed"):
        emit_metric("SpoofOrLivenessFailure")
        return response(
            403,
            {
                "verified": False,
                "reason": "liveness_failed",
                "liveness": liveness,
            },
        )

    enrollment = get_enrollment(user_id)
    if not enrollment:
        return response(404, {"error": "user is not enrolled"})

    similarity = compare_with_reference(
        enrollment["image_key"],
        image,
    )
    verified = similarity >= MATCH_THRESHOLD

    emit_metric(
        "VerificationSuccess"
        if verified
        else "VerificationFailure"
    )

    return response(
        200,
        {
            "user_id": user_id,
            "verified": verified,
            "similarity": round(similarity, 2),
            "match_threshold": MATCH_THRESHOLD,
            "liveness": liveness,
        },
    )
