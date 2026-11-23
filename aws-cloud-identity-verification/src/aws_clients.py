import boto3

s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")
dynamodb = boto3.resource("dynamodb")
cloudwatch = boto3.client("cloudwatch")
