import logging

from botocore.exceptions import ClientError

from src import aws_clients
from src.config import METRIC_NAMESPACE

logger = logging.getLogger(__name__)


def emit_metric(name: str, value: float = 1.0) -> None:
    try:
        aws_clients.cloudwatch.put_metric_data(
            Namespace=METRIC_NAMESPACE,
            MetricData=[
                {
                    "MetricName": name,
                    "Value": value,
                    "Unit": "Count",
                }
            ],
        )
    except ClientError:
        logger.exception("Unable to emit CloudWatch metric", extra={"metric": name})
