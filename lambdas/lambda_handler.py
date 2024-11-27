import os
from aws_lambda_powertools import Logger

logger = Logger(service="dynamic-handler")

def lambda_handler(event, context):
    handler = os.getenv('handler', 'default.handler')
    logger.info(f"event: {event}")
    logger.info(f"handler: {handler}")

    try:
        module_name, function_name = handler.rsplit('.', 1)
        module = __import__(module_name, fromlist=[function_name])
        handler_function = getattr(module, function_name)
    except Exception as e:
        logger.exception(e)
        return {
            "statusCode": 500,
            "body": f"Error loading handler {handler}: {str(e)}"
        }

    return handler_function(event, context)
