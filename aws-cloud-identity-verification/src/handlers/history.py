from typing import Any, Dict

from src.services.history import list_verifications
from src.utils.http import response
from src.utils.validation import require_user_id


def handle_history(event: Dict[str, Any]) -> Dict[str, Any]:
    user_id = require_user_id(
        (event.get("pathParameters") or {}).get("user_id")
    )
    query = event.get("queryStringParameters") or {}
    try:
        limit = int(query.get("limit", "20"))
    except ValueError as exc:
        raise ValueError("limit must be an integer") from exc

    return response(
        200,
        {
            "user_id": user_id,
            "items": list_verifications(user_id, limit),
        },
    )
