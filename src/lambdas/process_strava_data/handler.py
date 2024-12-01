import json
import os
from src.utils.user import User
from aws_lambda_powertools import Logger
from src.utils.gpx import create_gpx_from_streams, gpx_to_parquet

logger = Logger(service="process-strava-data")
bucket_name = os.environ["S3_BUCKET"]


def lambda_handler(event, context):
    logger.info(event)
    for record in event["Records"]:
        body = json.loads(record["body"])
        user_id = body["user_id"]
        activity_id = body["activity_id"]

        user = User(user_id)
        user.load_from_db()
        user.refresh_tokens()

        activity = user.strava.get_activity(activity_id)
        stream_data = user.strava.get_activity_streams(activity_id)
        gpx_data = create_gpx_from_streams(stream_data, activity["start_date"])

        logger.info(
            f"pushing to {bucket_name}/activity_data/{user_id}/{activity_id}.parquet"
        )
        gpx_to_parquet(
            gpx_data,
            activity["start_date"],
            bucket_name,
            f"activity_data/{user_id}/{activity_id}.parquet",
        )
    return {"statusCode": 200, "body": json.dumps("Success")}
