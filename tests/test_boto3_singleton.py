import pytest
from unittest.mock import patch, MagicMock
from threading import Thread
from src.utils.boto3_singleton import (
    Boto3SessionSingleton,
    get_boto3_session,
    get_boto3_client,
    get_boto3_resource,
)

@pytest.fixture(autouse=True)
def reset_singleton():
    Boto3SessionSingleton._instance = None


@pytest.fixture
def mock_boto3_session():
    with patch("src.utils.boto3_singleton.boto3.Session") as mock_session_class:
        mock_session_instance = MagicMock()
        mock_session_class.return_value = mock_session_instance
        yield mock_session_instance


def test_singleton_instance_creation(mock_boto3_session):
    instance1 = Boto3SessionSingleton(profile_name="test-profile")
    instance2 = Boto3SessionSingleton()

    assert instance1 is instance2
    assert instance1.session is mock_boto3_session


def test_thread_safe_singleton(mock_boto3_session):
    instances = []

    def create_instance():
        instance = Boto3SessionSingleton(profile_name="test-thread")
        instances.append(instance)

    threads = [Thread(target=create_instance) for _ in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert all(instance is instances[0] for instance in instances)


def test_get_client(mock_boto3_session):
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    instance = Boto3SessionSingleton()
    client = instance.get_client("s3")

    mock_boto3_session.client.assert_called_once_with("s3")
    assert client is mock_client


def test_get_resource(mock_boto3_session):
    mock_resource = MagicMock()
    mock_boto3_session.resource.return_value = mock_resource

    instance = Boto3SessionSingleton()
    resource = instance.get_resource("dynamodb")

    mock_boto3_session.resource.assert_called_once_with("dynamodb")
    assert resource is mock_resource


def test_get_boto3_session(mock_boto3_session):
    session = get_boto3_session()
    assert isinstance(session, Boto3SessionSingleton)


def test_get_boto3_client_global(mock_boto3_session):
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    client = get_boto3_client("ec2")

    mock_boto3_session.client.assert_called_once_with("ec2")
    assert client is mock_client


def test_get_boto3_resource_global(mock_boto3_session):
    mock_resource = MagicMock()
    mock_boto3_session.resource.return_value = mock_resource

    resource = get_boto3_resource("sqs")

    mock_boto3_session.resource.assert_called_once_with("sqs")
    assert resource is mock_resource
