from aws_lambda_powertools import Logger

from src.utils.user import User


logger = Logger(service="store_activity_in_dynamo")


def lambda_handler(event, context):
    logger.info(event)
    user_id = event["user_id"]
    activity_id = event["activity_id"]
    parent_id = event.get("parent_id")
    parent_activity_id = event.get("parent_activity_id")

    user = User(user_id)
    user.save_activity_to_db(
        activity_id=activity_id,
        parent_id=parent_id if parent_id else user_id,
        parent_activity_id=parent_activity_id if parent_activity_id else activity_id,
    )

    return "success"
