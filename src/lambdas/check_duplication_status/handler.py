from aws_lambda_powertools import Logger

from src.utils.user import User

logger = Logger(service="check-duplication-status")


def lambda_handler(event, context):
    logger.info(event)
    child_id = event["child_id"]
    upload_id = event["upload_id"]

    child = User(child_id)
    child.load_from_db()
    child.refresh_tokens()

    resp = child.strava.get_upload(upload_id)
    print(resp)

    return {
        "child_activity_id": resp["activity_id"],
        "status": resp["status"],
        "error": resp["error"],
    }
