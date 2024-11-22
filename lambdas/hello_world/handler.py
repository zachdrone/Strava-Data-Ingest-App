from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.event_handler import APIGatewayHttpResolver

logger = Logger(service="my-lambda-service")
tracer = Tracer(service="my-lambda-service")
app = APIGatewayHttpResolver()

@app.get("/hello")
@tracer.capture_method
def hello_world():
    logger.info("Hello World Lambda is invoked")
    return {"message": "Hello from Lambda"}

def lambda_handler(event, context):
    return app.resolve(event, context)