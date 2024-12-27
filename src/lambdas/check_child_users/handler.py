from aws_lambda_powertools import Logger

from src.utils.user import User

logger = Logger(service="check-child-users")


def lambda_handler(event, context):
    logger.info(event)
    user_id = event["user_id"]

    user = User(user_id)
    user.load_from_db()

    return {"child_users": [{"child_user_id": id} for id in user.children]}
