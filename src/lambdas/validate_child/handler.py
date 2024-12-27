from aws_lambda_powertools import Logger

from src.utils.user import User

logger = Logger(service="validate-child")


def lambda_handler(event, context):
    logger.info(event)
    child_id = event["child_user_id"]
    parent_id = event["parent_id"]
    activity = event["activity"]

    child = User(child_id)
    child.load_from_db()

    parent_valid = parent_id in child.parents
    title_valid = child.firstname.lower() in activity["name"].lower()

    return {
        "child_user_id": child.id,
        "parent_valid": parent_valid,
        "title_valid": title_valid,
    }
