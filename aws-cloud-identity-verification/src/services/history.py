from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List
from uuid import uuid4

from boto3.dynamodb.conditions import Key

from src import aws_clients
from src.config import VERIFICATION_TABLE


def _table():
    return aws_clients.dynamodb.Table(VERIFICATION_TABLE)


def record_verification(
    user_id: str,
    verified: bool,
    similarity: float,
    liveness_confidence: float,
) -> Dict[str, Any]:
    created_at = datetime.now(timezone.utc).isoformat()
    item = {
        "user_id": user_id,
        "record_id": f"{created_at}#{uuid4().hex[:8]}",
        "created_at": created_at,
        "verified": verified,
        "similarity": Decimal(str(round(similarity, 2))),
        "liveness_confidence": Decimal(
            str(round(liveness_confidence, 2))
        ),
    }
    _table().put_item(Item=item)
    return item


def list_verifications(
    user_id: str,
    limit: int = 20,
) -> List[Dict[str, Any]]:
    result = _table().query(
        KeyConditionExpression=Key("user_id").eq(user_id),
        ScanIndexForward=False,
        Limit=max(1, min(limit, 50)),
    )

    items = result.get("Items", [])
    return [
        {
            **item,
            "similarity": float(item.get("similarity", 0)),
            "liveness_confidence": float(
                item.get("liveness_confidence", 0)
            ),
        }
        for item in items
    ]
