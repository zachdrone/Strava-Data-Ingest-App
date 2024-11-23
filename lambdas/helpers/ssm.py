import boto3
from botocore.exceptions import ClientError

def get_parameter(client, param, decryption):
    try:
        get_parameter_response = client.get_parameter(
            Name=param,
            WithDecryption=decryption
        )
    except ClientError as e:
        raise e

    return get_parameter_response['Parameter']['Value']

def get_client_params():
    session = boto3.session.Session()
    client = session.client(
        service_name='ssm',
        region_name='us-east-1'
    )

    return {
        "client_id": get_parameter(client, "strava_client_id", False),
        "client_secret": get_parameter(client, "strava_client_secret", True)
    }