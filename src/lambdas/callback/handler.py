import json
from aws_lambda_powertools import Logger, Tracer
from src.utils.ssm import get_parameter
from src.utils.user import User

logger = Logger(service="my-lambda-service")
tracer = Tracer(service="my-lambda-service")


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.info(event)

    expected_state = get_parameter("strava_callback_state", True)
    if event.get("queryStringParameters") is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Missing query parameters."}),
        }
    if event.get("queryStringParameters").get("state") is None:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Missing state parameter."}),
        }
    received_state = event["queryStringParameters"]["state"]
    if received_state != expected_state:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid state parameter."}),
        }

    user = User()
    user.scope = event["queryStringParameters"]["scope"]
    user.load_from_auth_code(auth_code=event["queryStringParameters"]["code"])

    return {"statusCode": 200, "body": "Authorized!"}

