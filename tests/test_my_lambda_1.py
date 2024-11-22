# tests/test_my_lambda_1.py

import pytest
from lambdas.my_lambda_1.handler import lambda_handler

def test_lambda_handler(lambda_context):
    # Simulate a Lambda event
    event = {"key": "value"}
    context = {}  # You can mock a context object if needed

    # Call the handler
    response = lambda_handler(event, lambda_context)

    # Assert the response
    assert response["statusCode"] == 200
    assert response["body"] == "Hello from Lambda 1!"
