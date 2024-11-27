# tests/test_my_lambda_1.py

import pytest
from lambdas.health.handler import lambda_handler

def test_lambda_handler(lambda_context):
    # Simulate a Lambda event
    event = {"key": "value"}
    # Call the handler
    response = lambda_handler(event, lambda_context)

    # Assert the response
    assert response["statusCode"] == 200
    assert response["body"] == "We are healthy!"
