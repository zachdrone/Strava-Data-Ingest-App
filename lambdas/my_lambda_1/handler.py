# lambdas/my_lambda_1/handler.py
from aws_lambda_powertools import Logger, Tracer

logger = Logger(service="my-lambda-service")
tracer = Tracer(service="my-lambda-service")

@logger.inject_lambda_context
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    logger.info("Lambda 1 is processing the event")
    return {"statusCode": 200, "body": "Hello from Lambda 1!"}
