import json
import os
from aws_lambda_powertools import Logger
from src.utils.boto3_singleton import get_boto3_client
from src.utils.user import User

GPX_DATA_S3_BUCKET = os.environ["GPX_DATA_BUCKET"]
PARQUET_DATA_S3_BUCKET = os.environ["PARQUET_DATA_BUCKET"]

logger = Logger(service="process-strava-data-trigger")
s3 = get_boto3_client("s3")


def lambda_handler(event, context):
    logger.info(event)
    for record in event["Records"]:
        body = json.loads(record["body"])
        user_id = body["user_id"]
        activity_id = body["activity_id"]

        # delete dynamo record
        user = User(user_id)
        user.delete_activity_from_db(activity_id)

        # delete gpx file record
        gpx_s3_key = f"{user_id}/{activity_id}.gpx"
        response = s3.delete_object(Bucket=GPX_DATA_S3_BUCKET, Key=gpx_s3_key)
        logger.info(f"deleted gpx file {gpx_s3_key}", response=response)

        # delete parquet file
        parquet_s3_key = f"{user.id}/{activity_id}.parquet"
        response = s3.delete_object(Bucket=PARQUET_DATA_S3_BUCKET, Key=parquet_s3_key)
        logger.info(f"deleted parquet file {parquet_s3_key}", response=response)

    return "success"
