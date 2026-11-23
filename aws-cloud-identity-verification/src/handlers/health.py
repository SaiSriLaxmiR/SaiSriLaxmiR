from typing import Any, Dict

from src.utils.http import response


def handle_health(_: Dict[str, Any]) -> Dict[str, Any]:
    return response(
        200,
        {
            "status": "ok",
            "service": "cloud-identity-verification",
        },
    )
