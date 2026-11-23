import os

TABLE_NAME = os.environ.get("TABLE_NAME", "IdentityUsers")
IMAGE_BUCKET = os.environ.get("IMAGE_BUCKET", "identity-reference-images")
MATCH_THRESHOLD = float(os.environ.get("MATCH_THRESHOLD", "90"))
LIVENESS_THRESHOLD = float(os.environ.get("LIVENESS_THRESHOLD", "90"))
MAX_IMAGE_BYTES = int(os.environ.get("MAX_IMAGE_BYTES", str(5 * 1024 * 1024)))
METRIC_NAMESPACE = "CloudIdentityVerification"
