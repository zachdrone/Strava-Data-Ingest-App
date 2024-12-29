from aws_lambda_powertools import Logger

from src.utils.user import User


logger = Logger(service="check-child-users")


def lambda_handler(event, context):
    logger.info(event)
    user_id = event["user_id"]
    activity_id = event["activity_id"]

    user = User(user_id)
    user.save_activity_to_db(activity_id)

    return "success"
