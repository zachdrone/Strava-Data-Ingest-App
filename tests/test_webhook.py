import json
import pytest
from unittest.mock import patch, MagicMock
from src.lambda_function import lambda_handler, WEBHOOK_VERIFY_TOKEN, WEBHOOK_SUBSCRIPTION_ID

# Fixture for Lambda context
@pytest.fixture
def lambda_context():
    class LambdaContext:
        def __init__(self):
            self.function_name = "strava-webhook"
            self.memory_limit_in_mb = 128
            self.invoked_function_arn = "arn:aws:lambda:us-east-1:123456789012:function:strava-webhook"
            self.aws_request_id = "fake-request-id"

    return LambdaContext()

# Test for webhook verification success
def test_webhook_verification_success(lambda_context):
    event = {
        "httpMethod": "GET",
        "queryStringParameters": {
            "hub.verify_token": WEBHOOK_VERIFY_TOKEN,
            "hub.mode": "subscribe",
            "hub.challenge": "challenge_code"
        },
        "headers": {},
        "body": None
    }

    response = lambda_handler(event, lambda_context)
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["hub.challenge"] == "challenge_code"

# Test for webhook verification failure
def test_webhook_verification_failure(lambda_context):
    event = {
        "httpMethod": "GET",
        "queryStringParameters": {
            "hub.verify_token": "invalid_token",
            "hub.mode": "subscribe",
            "hub.challenge": "challenge_code"
        },
        "headers": {},
        "body": None
    }

    response = lambda_handler(event, lambda_context)
    assert response["statusCode"] == 400
    assert response["body"] == "Invalid Verification Request"

# Test for webhook handler with valid subscription id
@patch("src.lambda_function.User")
def test_webhook_handler_valid_subscription(mock_user, lambda_context):
    event_body = {
        "subscription_id": int(WEBHOOK_SUBSCRIPTION_ID),
        "aspect_type": "create",
        "owner_id": 12345
    }
    event = {
        "httpMethod": "POST",
        "queryStringParameters": None,
        "headers": {},
        "body": json.dumps(event_body)
    }

    mock_user.return_value.load_from_db = MagicMock()
    mock_user.return_value.username = "test_user"

    response = lambda_handler(event, lambda_context)
    assert response["statusCode"] == 200
    assert response["body"] == "Event received successfully"

# Test for webhook handler with invalid subscription id
def test_webhook_handler_invalid_subscription(lambda_context):
    event_body = {
        "subscription_id": 99999,
        "aspect_type": "create",
        "owner_id": 12345
    }
    event = {
        "httpMethod": "POST",
        "queryStringParameters": None,
        "headers": {},
        "body": json.dumps(event_body)
    }

    response = lambda_handler(event, lambda_context)
    assert response["statusCode"] == 403
    assert response["body"] == "Forbidden"

# Test for webhook handler delete aspect type
def test_webhook_handler_delete_aspect_type(lambda_context):
    event_body = {
        "subscription_id": int(WEBHOOK_SUBSCRIPTION_ID),
        "aspect_type": "delete",
        "owner_id": 12345
    }
    event = {
        "httpMethod": "POST",
        "queryStringParameters": None,
        "headers": {},
        "body": json.dumps(event_body)
    }

    response = lambda_handler(event, lambda_context)
    assert response["statusCode"] == 200
    assert response["body"] == "Skipping delete event"

# Test for user revoking access
@patch("src.lambda_function.User")
def test_webhook_handler_user_revoked_access(mock_user, lambda_context):
    event_body = {
        "subscription_id": int(WEBHOOK_SUBSCRIPTION_ID),
        "aspect_type": "update",
        "owner_id": 12345,
        "updates": {"authorized": "false"}
    }
    event = {
        "httpMethod": "POST",
        "queryStringParameters": None,
        "headers": {},
        "body": json.dumps(event_body)
    }

    mock_user.return_value.delete_from_db = MagicMock()

    response = lambda_handler(event, lambda_context)
    mock_user.return_value.delete_from_db.assert_called_once()
    assert response is None
