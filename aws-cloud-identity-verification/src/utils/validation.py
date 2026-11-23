import base64
import binascii

from src.config import MAX_IMAGE_BYTES


def require_user_id(value: object) -> str:
    user_id = str(value or "").strip()
    if not user_id:
        raise ValueError("user_id is required")
    if len(user_id) > 128:
        raise ValueError("user_id must be 128 characters or fewer")
    return user_id


def decode_image(image_base64: str) -> bytes:
    if not image_base64:
        raise ValueError("image_base64 is required")

    payload = image_base64
    if "," in payload and payload.split(",", 1)[0].startswith("data:"):
        payload = payload.split(",", 1)[1]

    try:
        image = base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError) as exc:
        raise ValueError("image_base64 is not valid base64") from exc

    if not image:
        raise ValueError("Decoded image is empty")
    if len(image) > MAX_IMAGE_BYTES:
        raise ValueError(f"Image exceeds {MAX_IMAGE_BYTES} byte limit")

    return image
