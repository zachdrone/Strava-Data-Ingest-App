import json
from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import CORSConfig, APIGatewayRestResolver
from lambdas.helpers.auth import get_parameter

logger = Logger(service="strava-webhook")
app = APIGatewayRestResolver(cors=CORSConfig(allow_origin="*"))

CLIENT_SECRET = get_parameter('strava_client_secret', True)
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
    received_subscription_id = data.get('subscription_id')
    
    if received_subscription_id != int(WEBHOOK_SUBSCRIPTION_ID):
        logger.error("Invalid subscription id")
        return {"statusCode": 403, "body": "Forbidden"}

    return {"statusCode": 200, "body": "Event received successfully"}

def lambda_handler(event, context):
    logger.info("wtf")
    logger.info(event)
    return app.resolve(event, context)
