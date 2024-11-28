import json
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import CORSConfig, APIGatewayRestResolver, Response, content_types
from src.utils.ssm import get_parameter
from src.utils.user import User
from http import HTTPStatus

logger = Logger(service="strava-webhook")
app = APIGatewayRestResolver(cors=CORSConfig(allow_origin="*"))

@app.get("/webhook")
def webhook_verification():
    """Handles the initial verification challenge from Strava"""
    
    query_params = app.current_event.query_string_parameters
    WEBHOOK_VERIFY_TOKEN = get_parameter('webhook_verify_token', True)
    if query_params.get('hub.verify_token') != WEBHOOK_VERIFY_TOKEN:
        logger.warning('invalid verify token')
        return Response(
            status_code=HTTPStatus.BAD_REQUEST.value,  # 400
            content_type=content_types.APPLICATION_JSON,
            body="Invalid Verification Request",
        )
    if query_params.get('hub.mode') == 'subscribe':
        return {
            "hub.challenge": query_params.get('hub.challenge')
        }


@app.post("/webhook")
def webhook_handler():
    """Handles incoming events from Strava"""
    event_body = app.current_event.body

    data = json.loads(event_body)
    logger.info(f"Received data: {data}")

    # Validate subscription id
    received_subscription_id = data['subscription_id']
    WEBHOOK_SUBSCRIPTION_ID = get_parameter('webhook_subscription_id', True)

    if received_subscription_id != int(WEBHOOK_SUBSCRIPTION_ID):
        logger.error("Invalid subscription id")
        return Response(
            status_code=HTTPStatus.FORBIDDEN.value,  # 403
            content_type=content_types.APPLICATION_JSON,
            body="Forbidden",
        )
    
    if data['aspect_type'] == 'delete':
        logger.info("skipping delete event")
        return "Skipping delete event"
    
    user = User(id=data['owner_id'])
    if data['aspect_type'] == 'update':
        updates = data.get('updates')
        if updates.get('authorized') == 'false':
            logger.info(f"User {user.id} revoked access, deleting from db")
            user.delete_from_db()
            return "User deleted"

    user.load_from_db()

    logger.info(user.username)

    return "Event received successfully"

@logger.inject_lambda_context(log_event=True)
def lambda_handler(event, context):
    return app.resolve(event, context)
