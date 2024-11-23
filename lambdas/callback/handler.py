from aws_lambda_powertools import Logger, Tracer
from lambdas.helpers.asm import get_secret

logger = Logger(service="my-lambda-service")
tracer = Tracer(service="my-lambda-service")

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.info(event)
    logger.info("Lambda 1 is processing the event")
    secret = get_secret()
    return {"statusCode": 200, "body": "Hello from callback!"}
