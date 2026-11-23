import logging
from typing import Any, Dict

from botocore.exceptions import ClientError

from src.handlers.enroll import handle_enroll
from src.handlers.health import handle_health
from src.handlers.history import handle_history
from src.handlers.liveness import (
    handle_create_liveness,
    handle_get_liveness,
)
from src.handlers.verify import handle_verify
from src.services.metrics import emit_metric
from src.utils.http import response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

ROUTES = {
    "GET /health": handle_health,
    "POST /enroll": handle_enroll,
    "POST /verify": handle_verify,
    "GET /history/{user_id}": handle_history,
    "POST /liveness/session": handle_create_liveness,
    "GET /liveness/{session_id}": handle_get_liveness,
}


def lambda_handler(
    event: Dict[str, Any],
    _context: Any,
) -> Dict[str, Any]:
    route = event.get("routeKey") or (
        f"{event.get('httpMethod', '')} "
        f"{event.get('resource', '')}"
    ).strip()

    handler = ROUTES.get(route)
    if not handler:
        return response(
            404,
            {
                "error": "route not found",
                "route": route,
            },
        )

    try:
        return handler(event)
    except ValueError as exc:
        return response(400, {"error": str(exc)})
    except ClientError as exc:
        error_code = (
            exc.response
            .get("Error", {})
            .get("Code", "AWSClientError")
        )
        emit_metric("ServiceError")
        return response(
            502,
            {
                "error": "AWS service request failed",
                "code": error_code,
            },
        )
    except Exception:
        logger.exception("Unhandled service error")
        emit_metric("ServiceError")
        return response(
            500,
            {"error": "internal server error"},
        )
