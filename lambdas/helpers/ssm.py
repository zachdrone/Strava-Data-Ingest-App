import requests
from botocore.exceptions import ClientError
from lambdas.helpers.boto3_singleton import get_boto3_client

def get_parameter(param, decryption, ssm=get_boto3_client('ssm')):
    try:
        get_parameter_response = ssm.get_parameter(
            Name=param,
            WithDecryption=decryption
        )
    except ClientError as e:
        raise e

    return get_parameter_response['Parameter']['Value']