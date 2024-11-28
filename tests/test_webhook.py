import json
import pytest
from unittest.mock import patch, MagicMock
from src.lambdas.webhook.handler import lambda_handler

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
@patch("src.lambdas.webhook.handler.get_parameter")
def test_webhook_verification_success(mock_get_parameter, lambda_context):
    # Mock `get_parameter` to return expected tokens
    mock_get_parameter.side_effect = lambda key, decrypt: "expected_verify_token" if key == "webhook_verify_token" else "12345"

    event = {
        "httpMethod": "GET",
        "path": "/webhook",
        "queryStringParameters": {
            "hub.verify_token": "expected_verify_token",
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
@patch("src.lambdas.webhook.handler.get_parameter")
def test_webhook_verification_failure(mock_get_parameter, lambda_context):
    # Mock `get_parameter` to return expected tokens
    mock_get_parameter.side_effect = lambda key, decrypt: "expected_verify_token" if key == "webhook_verify_token" else "12345"

    event = {
        "httpMethod": "GET",
        "path": "/webhook",
        "queryStringParameters": {
            "hub.verify_token": "invalid_token",
            "hub.mode": "subscribe",
            "hub.challenge": "challenge_code"
        },
        "headers": {},
        "body": None
    }

    response = lambda_handler(event, lambda_context)
    print(f"Response: {response}")
    assert response["statusCode"] == 400
    assert response["body"] == "Invalid Verification Request"


@patch("src.lambdas.webhook.handler.get_parameter")
def test_webhook_delete_event(mock_get_parameter, lambda_context):
    # Mock `get_parameter` to return expected tokens
    mock_get_parameter.side_effect = lambda key, decrypt: "expected_verify_token" if key == "webhook_verify_token" else "12345"
    
    event_body = json.dumps({
        "subscription_id": 12345,
        "aspect_type": "delete"
    })
    event = {
        "httpMethod": "POST",
        "path": "/webhook",
        "queryStringParameters": {
            "hub.verify_token": "expected_verify_token",
            "hub.mode": "subscribe",
            "hub.challenge": "challenge_code"
        },
        "headers": {},
        "body": event_body
    }

    response = lambda_handler(event, lambda_context)
    assert response["statusCode"] == 200
    assert response["body"] == "Skipping delete event"

@patch("src.lambdas.webhook.handler.get_parameter")
def test_webhook_access_revoked(mock_get_parameter, lambda_context):
    # Mock `get_parameter` to return expected tokens
    mock_get_parameter.side_effect = lambda key, decrypt: "expected_verify_token" if key == "webhook_verify_token" else "12345"
    
    event_body = json.dumps({
        "subscription_id": 12345,
        "aspect_type": "update",
        "updates": {
            "authorized": "false"
        },
        "owner_id": 12345
    })
    event = {
        "httpMethod": "POST",
        "path": "/webhook",
        "queryStringParameters": {
            "hub.verify_token": "expected_verify_token",
            "hub.mode": "subscribe",
            "hub.challenge": "challenge_code"
        },
        "headers": {},
        "body": event_body
    }

    response = lambda_handler(event, lambda_context)
    assert response["statusCode"] == 200
    assert response["body"] == "User deleted"

# Test for webhook handler with valid subscription id
@patch("src.lambdas.webhook.handler.get_parameter")
@patch("src.lambdas.webhook.handler.User")
def test_webhook_handler_valid_subscription(mock_user, mock_get_parameter, lambda_context):
    # Mock `get_parameter` to return expected values
    mock_get_parameter.side_effect = lambda key, decrypt: "expected_verify_token" if key == "webhook_verify_token" else "12345"

    event_body = {
        "subscription_id": 12345,
        "aspect_type": "create",
        "owner_id": 12345
    }
    event = {
        "httpMethod": "POST",
        "path": "/webhook",
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
@patch("src.lambdas.webhook.handler.get_parameter")
def test_webhook_handler_invalid_subscription(mock_get_parameter, lambda_context):
    # Mock `get_parameter` to return expected values
    mock_get_parameter.side_effect = lambda key, decrypt: "expected_verify_token" if key == "webhook_verify_token" else "12345"

    event_body = {
        "subscription_id": 99999,
        "aspect_type": "create",
        "owner_id": 12345
    }
    event = {
        "httpMethod": "POST",
        "path": "/webhook",
        "queryStringParameters": None,
        "headers": {},
        "body": json.dumps(event_body)
    }

    response = lambda_handler(event, lambda_context)
    assert response["statusCode"] == 403
    assert response["body"] == "Forbidden"
