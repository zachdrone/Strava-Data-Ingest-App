import os
import re

from aws_lambda_powertools import Logger

from src.utils.user import User

logger = Logger(service="process-strava-data")
bucket_name = os.environ["S3_BUCKET"]


def convert_camel_to_sentence(text):
    result = re.sub(r"(?<!^)(?=[A-Z])", " ", text)
    return result[0].upper() + result[1:].lower()


def lambda_handler(event, context):
    logger.info(event)
    user_id = event["user_id"]
    activity_id = event["activity_id"]

    user = User(user_id)
    user.save_activity_to_db(activity_id)

    return "success"
