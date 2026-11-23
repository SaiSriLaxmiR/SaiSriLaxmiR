from typing import Any, Dict

from src.services.metrics import emit_metric
from src.services.rekognition_service import (
    create_liveness_session,
    get_liveness_result,
)
from src.utils.http import response


def handle_create_liveness(_: Dict[str, Any]) -> Dict[str, Any]:
    return response(
        201,
        {"session_id": create_liveness_session()},
    )


def handle_get_liveness(event: Dict[str, Any]) -> Dict[str, Any]:
    session_id = (event.get("pathParameters") or {}).get("session_id")
    if not session_id:
        return response(400, {"error": "session_id is required"})

    result = get_liveness_result(session_id)
    if not result["passed"]:
        emit_metric("LivenessFailure")

    return response(200, result)
