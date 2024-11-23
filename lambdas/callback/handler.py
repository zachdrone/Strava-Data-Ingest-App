from aws_lambda_powertools import Logger, Tracer
from lambdas.helpers.ssm import get_client_params

logger = Logger(service="my-lambda-service")
tracer = Tracer(service="my-lambda-service")

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.info(event)
    client_params = get_client_params()
    return {"statusCode": 200, "body": "Hello from callback!"}
