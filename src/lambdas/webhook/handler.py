import json
import os
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import (
    CORSConfig,
    APIGatewayRestResolver,
    Response,
    content_types,
)
from src.utils.ssm import get_parameter
from src.utils.user import User
from src.utils.boto3_singleton import get_boto3_client
from http import HTTPStatus

logger = Logger(service="strava-webhook")
app = APIGatewayRestResolver(cors=CORSConfig(allow_origin="*"))

activity_queue_url = os.environ["ACTIVITY_QUEUE_URL"]
delete_activity_queue_url = os.environ["DELETE_ACTIVITY_QUEUE_URL"]

sqs_client = get_boto3_client("sqs")


@app.get("/webhook")
def webhook_verification():
    """Handles the initial verification challenge from Strava"""

    query_params = app.current_event.query_string_parameters
    WEBHOOK_VERIFY_TOKEN = get_parameter("webhook_verify_token", True)
    if query_params.get("hub.verify_token") != WEBHOOK_VERIFY_TOKEN:
        logger.warning("invalid verify token")
        return Response(
            status_code=HTTPStatus.BAD_REQUEST.value,  # 400
            content_type=content_types.APPLICATION_JSON,
            body="Invalid Verification Request",
        )
    if query_params.get("hub.mode") == "subscribe":
        return {"hub.challenge": query_params.get("hub.challenge")}


@app.post("/webhook")
def webhook_handler():
    """Handles incoming events from Strava"""
    event_body = app.current_event.body

    data = json.loads(event_body)
    logger.info(f"Received data: {data}")

    # Validate subscription id
    received_subscription_id = data["subscription_id"]
    WEBHOOK_SUBSCRIPTION_ID = get_parameter("webhook_subscription_id", True)

    if received_subscription_id != int(WEBHOOK_SUBSCRIPTION_ID):
        logger.error("Invalid subscription id")
        return Response(
            status_code=HTTPStatus.FORBIDDEN.value,  # 403
            content_type=content_types.APPLICATION_JSON,
            body="Forbidden",
        )

    user = User(id=data["owner_id"])
    if data["aspect_type"] == "update":
        updates = data.get("updates")
        if updates.get("authorized") == "false":
            logger.info(f"User {user.id} revoked access, deleting from db")
            user.delete_from_db()
            return "User deleted"

    if data["object_type"] == "activity":
        if data["aspect_type"] == "delete":
            event_data = {"activity_id": data["object_id"], "user_id": user.id}
            logger.info(f"deleting {event_data}")
            response = sqs_client.send_message(
                QueueUrl=delete_activity_queue_url, MessageBody=json.dumps(event_data)
            )

        elif data["aspect_type"] == "create":
            user.load_from_db()
            event_data = {"activity_id": data["object_id"], "user_id": user.id}
            logger.info(f"sending event with payload: {event_data}")
            response = sqs_client.send_message(
                QueueUrl=activity_queue_url, MessageBody=json.dumps(event_data)
            )
            logger.info(response)
        else:
            logger.info("unprocessable aspect type", event_body=event_body)

    return "success"


@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    return app.resolve(event, context)
