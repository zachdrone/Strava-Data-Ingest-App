import json
import os
import re

from aws_lambda_powertools import Logger

from src.utils.gpx import get_gpx_from_s3
from src.utils.user import User

logger = Logger(service="duplicate-activity")
gpx_bucket_name = os.environ["GPX_DATA_BUCKET"]


def convert_camel_to_sentence(text):
    result = re.sub(r"(?<!^)(?=[A-Z])", " ", text)
    return result[0].upper() + result[1:].lower()


def lambda_handler(event, context):
    logger.info(event)
    child_user_id = event["child_user_id"]
    s3_key = event["gpx_data_s3_key"]
    activity = event["activity"]

    child = User(child_user_id)
    child.load_from_db()
    child.refresh_tokens()

    gpx_data = get_gpx_from_s3(gpx_bucket_name, s3_key)

    sport_name = convert_camel_to_sentence(activity.get("sport_type"))
    logger.info(
        f"uploading activity to child user {child.id} {child.firstname} {child.lastname}"
    )
    resp = child.strava.upload_activity_file(
        gpx_data,
        "gpx",
        f"{sport_name} with {child.firstname}!",
    )
    print(resp)

    return {"statusCode": 200, "body": json.dumps("Success")}
