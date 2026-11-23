from datetime import datetime, timezone
from typing import Any, Dict, Optional

from src import aws_clients
from src.config import IMAGE_BUCKET, TABLE_NAME


def _table():
    return aws_clients.dynamodb.Table(TABLE_NAME)


def save_reference_image(user_id: str, image: bytes) -> str:
    image_key = f"reference/{user_id}.jpg"
    aws_clients.s3.put_object(
        Bucket=IMAGE_BUCKET,
        Key=image_key,
        Body=image,
        ContentType="image/jpeg",
        ServerSideEncryption="AES256",
    )
    return image_key


def save_enrollment(user_id: str, image_key: str) -> str:
    enrolled_at = datetime.now(timezone.utc).isoformat()
    _table().put_item(
        Item={
            "user_id": user_id,
            "image_key": image_key,
            "enrolled_at": enrolled_at,
        }
    )
    return enrolled_at


def get_enrollment(user_id: str) -> Optional[Dict[str, Any]]:
    return _table().get_item(Key={"user_id": user_id}).get("Item")
