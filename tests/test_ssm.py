import pytest
from unittest.mock import MagicMock, patch
from botocore.exceptions import ClientError
from src.utils.ssm import get_parameter

@pytest.fixture
def mock_ssm_client():
    return MagicMock()


def test_get_parameter_success(mock_ssm_client):
    mock_response = {
        "Parameter": {
            "Value": "test-value"
        }
    }
    mock_ssm_client.get_parameter.return_value = mock_response

    param = "test-param"
    decryption = True
    result = get_parameter(param, decryption, ssm=mock_ssm_client)

    assert result == "test-value"

    mock_ssm_client.get_parameter.assert_called_once_with(
        Name=param,
        WithDecryption=decryption
    )


def test_get_parameter_client_error(mock_ssm_client):
    mock_ssm_client.get_parameter.side_effect = ClientError(
        error_response={
            "Error": {
                "Code": "ParameterNotFound",
                "Message": "The parameter does not exist."
            }
        },
        operation_name="GetParameter"
    )

    param = "non-existent-param"
    decryption = False

    with pytest.raises(ClientError) as exc_info:
        get_parameter(param, decryption, ssm=mock_ssm_client)

    assert exc_info.value.response["Error"]["Code"] == "ParameterNotFound"
    assert exc_info.value.response["Error"]["Message"] == "The parameter does not exist."

    mock_ssm_client.get_parameter.assert_called_once_with(
        Name=param,
        WithDecryption=decryption
    )


@patch("src.utils.ssm.get_boto3_client")
def test_get_parameter_with_default_ssm(mock_get_boto3_client):
    mock_ssm_client = MagicMock()
    mock_get_boto3_client.return_value = mock_ssm_client

    mock_response = {
        "Parameter": {
            "Value": "default-client-value"
        }
    }
    mock_ssm_client.get_parameter.return_value = mock_response

    param = "default-param"
    decryption = True
    result = get_parameter(param, decryption)

    assert result == "default-client-value"

    mock_get_boto3_client.assert_called_once_with("ssm")

    mock_ssm_client.get_parameter.assert_called_once_with(
        Name=param,
        WithDecryption=decryption
    )

