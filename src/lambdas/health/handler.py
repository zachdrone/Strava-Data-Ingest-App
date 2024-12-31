# lambdas/my_lambda_1/handler.py
from aws_lambda_powertools import Logger, Tracer

logger = Logger(service="health-endpoint")
tracer = Tracer(service="health-endpoint")


@logger.inject_lambda_context(log_event=True)
@tracer.capture_lambda_handler
def lambda_handler(event, context):
    return {"statusCode": 200, "body": "We are healthy updated!"}
