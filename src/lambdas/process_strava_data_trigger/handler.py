import json
import os

from aws_lambda_powertools import Logger

from src.utils.boto3_singleton import get_boto3_client

logger = Logger(service="process-strava-data-trigger")

STATE_MACHINE_ARN = os.environ["STATE_MACHINE_ARN"]
sfn_client = get_boto3_client("stepfunctions")


def lambda_handler(event, context):
    logger.info(event)
    for record in event["Records"]:
        body = json.loads(record["body"])
        user_id = body["user_id"]
        activity_id = body["activity_id"]

        input_payload = json.dumps({"user_id": user_id, "activity_id": activity_id})
        logger.info("starting sfn", input_payload=input_payload)
        response = sfn_client.start_execution(
            stateMachineArn=STATE_MACHINE_ARN,
            input=input_payload,
        )
        logger.info("sfn started", response=response)

    return "success"
