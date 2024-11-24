import boto3
from botocore.exceptions import ClientError
import requests

def _get_parameter(client, param, decryption):
    try:
        get_parameter_response = client.get_parameter(
            Name=param,
            WithDecryption=decryption
        )
    except ClientError as e:
        raise e

    return get_parameter_response['Parameter']['Value']

def get_parameter(param, decryption):
    session = boto3.session.Session()
    client = session.client(
        service_name='ssm',
        region_name='us-east-1'
    )

    return _get_parameter(client, param, decryption)

def get_client_params():
    return {
        "client_id": get_parameter("strava_client_id", False),
        "client_secret": get_parameter("strava_client_secret", True)
    }

def exchange_auth_code(client_id, client_secret, auth_code):
    params = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": auth_code,
        "grant_type": "authorization_code"
    }

    r = requests.post(
        "https://www.strava.com/oauth/token",
        data=params,
    )

    return r.json()