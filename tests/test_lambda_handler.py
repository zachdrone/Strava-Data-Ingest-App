import os
from unittest.mock import patch, MagicMock
import pytest
from lambdas.lambda_handler import lambda_handler

@pytest.fixture
def mock_context():
    return MagicMock()

def test_lambda_handler_valid_handler(mock_context):
    os.environ['handler'] = 'test_module.test_function'

    with patch('builtins.__import__') as mock_import:
        mock_module = MagicMock()
        mock_function = MagicMock(return_value={"statusCode": 200, "body": "success"})
        mock_module.test_function = mock_function
        mock_import.return_value = mock_module

        event = {"key": "value"}
        response = lambda_handler(event, mock_context)

        mock_import.assert_called_once_with('test_module', fromlist=['test_function'])
        mock_function.assert_called_once_with(event, mock_context)
        assert response == {"statusCode": 200, "body": "success"}

def test_lambda_handler_default_handler(mock_context):
    os.environ.pop('handler', None)

    with patch('builtins.__import__') as mock_import:
        mock_module = MagicMock()
        mock_function = MagicMock(return_value={"statusCode": 200, "body": "default success"})
        mock_module.handler = mock_function
        mock_import.return_value = mock_module

        event = {"key": "value"}
        response = lambda_handler(event, mock_context)

        mock_import.assert_called_once_with('default', fromlist=['handler'])
        mock_function.assert_called_once_with(event, mock_context)
        assert response == {"statusCode": 200, "body": "default success"}

def test_lambda_handler_invalid_module(mock_context):
    os.environ['handler'] = 'invalid_module.handler'

    with patch('builtins.__import__', side_effect=ImportError("No module named 'invalid_module'")):
        event = {"key": "value"}
        response = lambda_handler(event, mock_context)

        assert response['statusCode'] == 500
        assert "Error loading handler invalid_module.handler" in response['body']

def test_lambda_handler_invalid_function(mock_context):
    os.environ['handler'] = 'test_module.invalid_function'

    def side_effect(module_name, fromlist=None):
        if module_name == 'test_module':
            mock_module = MagicMock()
            if fromlist and 'invalid_function' in fromlist:
                del mock_module.invalid_function
            return mock_module
        else:
            return __import__(module_name, fromlist=fromlist)

    with patch('builtins.__import__', side_effect=side_effect) as mock_import:
        event = {"key": "value"}
        response = lambda_handler(event, mock_context)

        assert any(
            call.args[0] == 'test_module' and call.kwargs.get('fromlist') == ['invalid_function']
            for call in mock_import.mock_calls
        ), "Expected __import__ to be called with ('test_module', {'fromlist': ['invalid_function']})"

        assert response['statusCode'] == 500
        assert "Error loading handler test_module.invalid_function" in response['body']

def test_lambda_handler_malformed_handler_value(mock_context):
    os.environ['handler'] = 'malformed'

    event = {"key": "value"}
    response = lambda_handler(event, mock_context)

    assert response['statusCode'] == 500
    assert "Error loading handler malformed" in response['body']
