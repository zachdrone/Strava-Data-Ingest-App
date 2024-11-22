# tests/test_lambda_handler.py

import pytest
import os

from lambda_handler import lambda_handler

def test_dynamic_handler_selection(monkeypatch, lambda_context):
    # Set the environment variable to point to my_lambda_1's handler
    monkeypatch.setenv('handler', 'lambdas.my_lambda_1.handler.lambda_handler')

    # Simulate a Lambda event
    event = {"key": "value"}

    # Call the generic handler
    response = lambda_handler(event, lambda_context)

    # Assert the response from my_lambda_1's handler
    assert response["statusCode"] == 200
    assert response["body"] == "Hello from Lambda 1!"

def test_invalid_handler(monkeypatch, lambda_context):
    # Set an invalid handler path
    monkeypatch.setenv('handler', 'invalid.handler.path')

    # Simulate a Lambda event
    event = {"key": "value"}

    # Call the generic handler, expecting it to handle the error gracefully
    response = lambda_handler(event, lambda_context)

    # Assert an error response
    assert response["statusCode"] == 500
    assert "Error loading handler" in response["body"]
