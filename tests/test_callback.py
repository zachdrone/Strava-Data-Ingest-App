# tests/test_callback_handler.py
import pytest
import json
from unittest.mock import patch, MagicMock
from aws_lambda_powertools import Logger, Tracer
from src.lambdas.callback.handler import lambda_handler

@pytest.fixture
def mock_User():
    with patch('src.lambdas.callback.handler.User') as mock_User:
        yield mock_User

@pytest.fixture
def mock_get_parameter():
    with patch('src.lambdas.callback.handler.get_parameter') as mock_get_parameter:
        yield mock_get_parameter

def test_lambda_handler(mock_User, mock_get_parameter):
    # Mock dependencies
    mock_User.return_value = MagicMock()
    mock_get_parameter.return_value = 'expected_state'

    # Test lambda_handler function
    event = {'queryStringParameters': {'state': 'expected_state'}}
    context = MagicMock()
    response = lambda_handler(event, context)

    # Assert response
    assert response['statusCode'] == 200
    assert response['body'] == 'Authorized!'

    # Assert mocks were called
    mock_User.assert_called_once()
    mock_get_parameter.assert_called_once_with('strava_callback_state', True)

def test_lambda_handler_invalid_state(mock_User, mock_get_parameter):
    # Mock dependencies
    mock_User.return_value = MagicMock()
    mock_get_parameter.return_value = 'expected_state'

    # Test lambda_handler function with invalid state
    event = {'queryStringParameters': {'state': 'invalid_state'}}
    context = MagicMock()
    response = lambda_handler(event, context)

    # Assert response
    assert response['statusCode'] == 400
    assert response['body'] == json.dumps({'message': 'Invalid state parameter.'})

    # Assert mocks were called
    mock_User.assert_not_called()
    mock_get_parameter.assert_called_once_with('strava_callback_state', True)