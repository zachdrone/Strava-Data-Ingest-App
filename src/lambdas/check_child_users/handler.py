import json
import os

from aws_lambda_powertools import Logger

from src.utils.user import User

logger = Logger(service="process-strava-data")
bucket_name = os.environ["S3_BUCKET"]


def lambda_handler(event, context):
    logger.info(event)
    for record in event["Records"]:
        body = json.loads(record["body"])
        user_id = body["user_id"]

        user = User(user_id)
        user.load_from_db()
        user.refresh_tokens()

        return {"child_users": [{"child_user_id": id} for id in user.children]}
