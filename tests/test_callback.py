import json
import pytest
from unittest.mock import patch, MagicMock
from src.lambdas.callback.handler import lambda_handler
from src.utils.ssm import get_parameter
from src.utils.user import User

@pytest.fixture
def mock_context():
    """Fixture to create a mock Lambda context."""
    return MagicMock()

@patch("src.lambdas.callback.handler.get_parameter")
@patch("src.lambdas.callback.handler.User")
def test_lambda_handler_success(mock_user_class, mock_get_parameter, mock_context):
    mock_get_parameter.return_value = "expected_state_value"
    
    mock_user = MagicMock()
    mock_user_class.return_value = mock_user

    event = {
        "queryStringParameters": {
            "state": "expected_state_value",
            "scope": "read,write",
            "code": "auth_code_value"
        }
    }

    response = lambda_handler(event, mock_context)

    assert response["statusCode"] == 200
    assert response["body"] == "Authorized!"
    mock_get_parameter.assert_called_once_with('strava_callback_state', True)
    mock_user.load_from_auth_code.assert_called_once_with(auth_code="auth_code_value")
    assert mock_user.scope == "read,write"

@patch("src.lambdas.callback.handler.get_parameter")
@patch("src.lambdas.callback.handler.User")
def test_lambda_handler_invalid_state(mock_user_class, mock_get_parameter, mock_context):
    mock_get_parameter.return_value = "expected_state_value"
    
    event = {
        "queryStringParameters": {
            "state": "invalid_state_value",
            "scope": "read,write",
            "code": "auth_code_value"
        }
    }

    response = lambda_handler(event, mock_context)

    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {"message": "Invalid state parameter."}
    mock_get_parameter.assert_called_once_with('strava_callback_state', True)
    mock_user_class.assert_not_called()

@patch("src.lambdas.callback.handler.get_parameter")
def test_lambda_handler_missing_query_parameters(mock_get_parameter, mock_context):
    mock_get_parameter.return_value = "expected_state_value"
    
    event = {
        "queryStringParameters": None
    }

    response = lambda_handler(event, mock_context)

    assert response["statusCode"] == 400
    assert "message" in json.loads(response["body"]) 
    mock_get_parameter.assert_called_once_with('strava_callback_state', True)

@patch("src.lambdas.callback.handler.get_parameter")
def test_lambda_handler_missing_state_key(mock_get_parameter, mock_context):
    mock_get_parameter.return_value = "expected_state_value"
    
    event = {
        "queryStringParameters": {
            "scope": "read,write",
            "code": "auth_code_value"
        }
    }

    response = lambda_handler(event, mock_context)

    assert response["statusCode"] == 400
    assert "message" in json.loads(response["body"]) 
    mock_get_parameter.assert_called_once_with('strava_callback_state', True)
