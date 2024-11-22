import sys
import os
import json
import pytest
from types import SimpleNamespace

# Add the root directory (parent directory) to the PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture()
def lambda_context():
    """ Generates AWS Lambda context"""

    data = """{
        "aws_request_id": "abcdef",
        "invoked_function_arn": "arn:aws:lambda:eu-west-1:123456789012:function:SampleFunctionName-ERERWEREWR",
        "log_group_name": "/aws/lambda/SampleFunctionName-ERERWEREWR",
        "function_name": "SampleFunctionName-ERERWEREWR",
        "function_version": "$LATEST",
        "memory_limit_in_mb": 1234
    }"""

    context = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))

    return context