from typing import Any, Dict

from src.services.metrics import emit_metric
from src.services.rekognition_service import has_exactly_one_face
from src.services.storage import save_enrollment, save_reference_image
from src.utils.http import parse_json_body, response
from src.utils.validation import decode_image, require_user_id


def handle_enroll(event: Dict[str, Any]) -> Dict[str, Any]:
    body = parse_json_body(event)
    user_id = require_user_id(body.get("user_id"))
    image = decode_image(body.get("image_base64", ""))

    if not has_exactly_one_face(image):
        return response(
            422,
            {
                "error": (
                    "Enrollment image must contain exactly one detectable face"
                )
            },
        )

    image_key = save_reference_image(user_id, image)
    enrolled_at = save_enrollment(user_id, image_key)
    emit_metric("EnrollmentSuccess")

    return response(
        201,
        {
            "user_id": user_id,
            "enrolled_at": enrolled_at,
        },
    )
