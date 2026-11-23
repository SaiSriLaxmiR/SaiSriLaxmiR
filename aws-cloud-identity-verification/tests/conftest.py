import base64
import json
import os
from unittest.mock import MagicMock

import pytest

os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_EC2_METADATA_DISABLED", "true")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")

from src import aws_clients


def make_event(route, body=None, path_parameters=None):
    payload = {"routeKey": route}
    if body is not None:
        payload["body"] = json.dumps(body)
    if path_parameters is not None:
        payload["pathParameters"] = path_parameters
    return payload


def parse_response(response):
    return response["statusCode"], json.loads(response["body"])


def b64(data=b"fake-image"):
    return base64.b64encode(data).decode()


@pytest.fixture(autouse=True)
def aws_mocks(monkeypatch):
    s3 = MagicMock()
    rekognition = MagicMock()
    dynamodb = MagicMock()
    cloudwatch = MagicMock()
    table = MagicMock()
    dynamodb.Table.return_value = table

    monkeypatch.setattr(aws_clients, "s3", s3)
    monkeypatch.setattr(aws_clients, "rekognition", rekognition)
    monkeypatch.setattr(aws_clients, "dynamodb", dynamodb)
    monkeypatch.setattr(aws_clients, "cloudwatch", cloudwatch)

    return {
        "s3": s3,
        "rekognition": rekognition,
        "dynamodb": dynamodb,
        "cloudwatch": cloudwatch,
        "table": table,
    }
