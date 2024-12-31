import os
from unittest.mock import patch, MagicMock
import pytest
from src.lambdas.lambda_handler import lambda_handler


@pytest.fixture
def mock_context():
    return MagicMock()


def test_lambda_handler_valid_handler(mock_context):
    os.environ["handler"] = "test_module.test_function"

    with patch("builtins.__import__") as mock_import:
        mock_module = MagicMock()
        mock_function = MagicMock(return_value={"statusCode": 200, "body": "success"})
        mock_module.test_function = mock_function
        mock_import.return_value = mock_module

        event = {"key": "value"}
        response = lambda_handler(event, mock_context)

        mock_import.assert_called_once_with("test_module", fromlist=["test_function"])
        mock_function.assert_called_once_with(event, mock_context)
        assert response == {"statusCode": 200, "body": "success"}


def test_lambda_handler_default_handler(mock_context):
    os.environ.pop("handler", None)

    with patch("builtins.__import__") as mock_import:
        mock_module = MagicMock()
        mock_function = MagicMock(
            return_value={"statusCode": 200, "body": "default success"}
        )
        mock_module.handler = mock_function
        mock_import.return_value = mock_module

        event = {"key": "value"}
        response = lambda_handler(event, mock_context)

        mock_import.assert_called_once_with("default", fromlist=["handler"])
        mock_function.assert_called_once_with(event, mock_context)
        assert response == {"statusCode": 200, "body": "default success"}
