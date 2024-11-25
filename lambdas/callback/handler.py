import json
import boto3
from aws_lambda_powertools import Logger, Tracer
from lambdas.helpers.auth import get_parameter
from lambdas.helpers.boto3_singleton import get_boto3_resource
from lambdas.helpers.user import User

logger = Logger(service="my-lambda-service")
tracer = Tracer(service="my-lambda-service")

dynamodb = get_boto3_resource('dynamodb')
table = dynamodb.Table('users')

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.info(event)

    expected_state = get_parameter('strava_callback_state', True)
    received_state = event['queryStringParameters']['state']
    if received_state != expected_state:
        return {
            "statusCode": 400,
            "body": json.dumps({"message": "Invalid state parameter."})
        }
    
    user = User()
    user.scope = event['queryStringParameters']['scope']
    user.load_from_auth_code(auth_code=event['queryStringParameters']['code'])

    return {"statusCode": 200, "body": "Hello from callback!"}