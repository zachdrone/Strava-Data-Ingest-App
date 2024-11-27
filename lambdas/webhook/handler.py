import json
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import CORSConfig, APIGatewayRestResolver
from lambdas.helpers.ssm import get_parameter
from lambdas.helpers.user import User

logger = Logger(service="strava-webhook")
app = APIGatewayRestResolver(cors=CORSConfig(allow_origin="*"))

WEBHOOK_VERIFY_TOKEN = get_parameter('webhook_verify_token', True)
WEBHOOK_SUBSCRIPTION_ID = get_parameter('webhook_subscription_id', True)

@app.get("/webhook")
def webhook_verification():
    """Handles the initial verification challenge from Strava"""
    query_params = app.current_event.query_string_parameters
    if query_params.get('hub.verify_token') != WEBHOOK_VERIFY_TOKEN:
        logger.warning('invalid verify token')
        {"statusCode": 400, "body": "Invalid Verification Request"}
    if query_params.get('hub.mode') == 'subscribe':
        return {
            "hub.challenge": query_params.get('hub.challenge')
        }
    return {"statusCode": 400, "body": "Invalid Verification Request"}

@app.post("/webhook")
def webhook_handler():
    """Handles incoming events from Strava"""
    event_body = app.current_event.body

    data = json.loads(event_body)
    logger.info(f"Received data: {data}")

    # Validate subscription id
    received_subscription_id = data['subscription_id']
    
    if received_subscription_id != int(WEBHOOK_SUBSCRIPTION_ID):
        logger.error("Invalid subscription id")
        return {"statusCode": 403, "body": "Forbidden"}
    
    if data['aspect_type'] == 'delete':
        logger.info("skipping delete event")
        return {"statusCode": 200, "body": "Skipping delete event"}
    
    user = User(id=data['owner_id'])
    if data['aspect_type'] == 'update':
        updates = data.get('updates')
        if updates.get('authorized') == 'false':
            logger.info(f"User {user.id} revoked access, deleting from db")
            user.delete_from_db()
            return

    user.load_from_db()

    logger.info(user.username)

    return {"statusCode": 200, "body": "Event received successfully"}

def lambda_handler(event, context):
    logger.info(event)
    return app.resolve(event, context)
