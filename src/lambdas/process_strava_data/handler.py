import json
import os
import re
from src.utils.user import User
from aws_lambda_powertools import Logger
from src.utils.gpx import create_gpx_from_streams, gpx_to_parquet

logger = Logger(service="process-strava-data")
bucket_name = os.environ["S3_BUCKET"]


def convert_camel_to_sentence(text):
    result = re.sub(r"(?<!^)(?=[A-Z])", " ", text)
    return result[0].upper() + result[1:].lower()


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

        # Temp disable while developing other features
        # logger.info(
        #     f"pushing to {bucket_name}/activity_data/{user.id}/{activity_id}.parquet"
        # )
        # gpx_to_parquet(
        #     gpx_data,
        #     bucket_name,
        #     f"activity_data/{user.id}/{activity_id}.parquet",
        # )

        print(f"user children arr: {user.children}")
        for child_id in user.children:
            child = User(child_id)
            child.load_from_db()
            if user.id in child.parents:
                child.refresh_tokens()
                sport_name = convert_camel_to_sentence(activity.get("sport_type"))
                logger.info(
                    f"uploading activity to user {child.id} {child.firstname} {child.lastname}"
                )
                child.strava.upload_activity_file(
                    gpx_data,
                    "gpx",
                    f"{sport_name} with {user.firstname}!",
                )

    return {"statusCode": 200, "body": json.dumps("Success")}
