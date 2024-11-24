import json
from aws_lambda_powertools import Logger, Tracer
from lambdas.helpers.auth import get_client_params, exchange_auth_code, get_parameter

logger = Logger(service="my-lambda-service")
tracer = Tracer(service="my-lambda-service")

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.info(event)

    expected_state = get_parameter('strava_callback_state', True)
    recieved_state = event['queryStringParameters']['state']

    if recieved_state != expected_state:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid state parameter."})
        }

    client_params = get_client_params()

    auth = exchange_auth_code(
        **client_params,
        auth_code=event['queryStringParameters']['code']
    )

    

    return {"statusCode": 200, "body": "Hello from callback!"}
