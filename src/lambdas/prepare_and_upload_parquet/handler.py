import os

from aws_lambda_powertools import Logger

from src.utils.gpx import get_gpx_from_s3, gpx_to_parquet

logger = Logger(service="prepare_and_upload_parquet")
gpx_data_bucket = os.environ["GPX_DATA_BUCKET"]
parquet_data_bucket = os.environ["PARQUET_DATA_BUCKET"]


def lambda_handler(event, context):
    logger.info(event)
    user_id = event["user_id"]
    activity_id = event["activity_id"]
    gpx_data_key = event["gpx_data_s3_key"]

    gpx_data = get_gpx_from_s3(gpx_data_bucket, gpx_data_key)

    parquet_data_key = f"{user_id}/{activity_id}.parquet"
    resp = gpx_to_parquet(
        gpx_data,
        parquet_data_bucket,
        parquet_data_key,
    )
    logger.info(resp)

    return {
        "parquet_data_s3_key": parquet_data_key,
    }
