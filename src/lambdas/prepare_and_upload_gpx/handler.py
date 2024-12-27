import os

from aws_lambda_powertools import Logger

from src.utils.boto3_singleton import get_boto3_client
from src.utils.gpx import create_gpx_from_streams
from src.utils.user import User

logger = Logger(service="create-gpx-data")
bucket_name = os.environ["S3_BUCKET"]


def lambda_handler(event, context):
    logger.info(event)
    user_id = event["user_id"]
    activity_id = event["activity_id"]

    user = User(user_id)
    user.load_from_db()
    user.refresh_tokens()

    activity = user.strava.get_activity(activity_id)
    stream_data = user.strava.get_activity_streams(activity_id)
    gpx_data = create_gpx_from_streams(stream_data, activity["start_date"])

    s3_file_key = (f"activity_data/{user.id}/{activity_id}.gpx",)
    s3_client = get_boto3_client("s3")
    logger.info(f"pushing to {bucket_name}/{s3_file_key}")
    s3_client.put_object(Bucket=bucket_name, Key=s3_file_key, Body=gpx_data)

    return {
        "activity": activity,
        "gpx_data_s3_key": s3_file_key,
    }
