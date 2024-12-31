import unittest
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from botocore.exceptions import ClientError
from cryptography.fernet import Fernet

from src.utils.ssm import get_parameter
from src.utils.boto3_singleton import get_boto3_client, get_boto3_resource
from src.utils.strava import Strava
from src.utils.user import User


class TestUser(unittest.TestCase):

    def setUp(self):
        self.mock_boto3_resource = patch("src.utils.user.get_boto3_resource").start()
        self.mock_boto3_client = patch("src.utils.user.get_boto3_client").start()
        self.mock_get_parameter = patch("src.utils.user.get_parameter").start()
        self.mock_strava = patch("src.utils.user.Strava").start()

        self.mock_dynamodb_resource = MagicMock()
        self.mock_boto3_resource.return_value = self.mock_dynamodb_resource

        self.mock_table = MagicMock()
        self.mock_dynamodb_resource.Table.return_value = self.mock_table

        self.mock_client = MagicMock()
        self.mock_boto3_client.return_value = self.mock_client

        self.mock_get_parameter.side_effect = lambda key, secure, client: (
            b"encryption_key" if key == "encryption_key" else "mock_value"
        )

        self.mock_fernet = patch("src.utils.user.Fernet").start()
        self.mock_cipher = MagicMock()
        self.mock_fernet.return_value = self.mock_cipher
        self.mock_cipher.encrypt.side_effect = lambda value: value
        self.mock_cipher.decrypt.side_effect = lambda value: value

        self.user = User(id=123456)

    def tearDown(self):
        patch.stopall()

    def test_get_access_token_none(self):
        self.user.access_token = None
        assert self.user._access_token == None

    def test_get_refresh_token_none(self):
        self.user.refresh_token = None
        assert self.user._refresh_token == None

    def test_get_access_token_not_none(self):
        self.user.access_token = "access"
        assert self.user._access_token == b"access"

    def test_get_refresh_token_not_none(self):
        self.user.refresh_token = "refresh"
        assert self.user._refresh_token == b"refresh"

    def test_load_from_db_success(self):
        mock_item = {
            "id": 123456,
            "username": "test_username",
            "access_token": "access_token",
            "token_expires_at": int((datetime.now() + timedelta(days=1)).timestamp()),
            "refresh_token": "refresh_token",
            "scope": "read",
            "children": [],
        }
        self.mock_table.get_item.return_value = {"Item": mock_item}

        result = self.user.load_from_db()

        self.assertTrue(result)
        self.assertEqual(self.user.username, "test_username")
        self.assertEqual(self.user.access_token, "access_token")
        self.assertEqual(self.user.token_expires_at, mock_item["token_expires_at"])
        self.assertEqual(self.user.refresh_token, "refresh_token")
        self.assertEqual(self.user.scope, "read")
        self.assertEqual(self.user.children, [])

    def test_load_from_db_no_data(self):
        self.mock_table.get_item.return_value = {}

        result = self.user.load_from_db()

        self.assertFalse(result)
        self.assertIsNone(self.user.username)

    def test_load_from_db_no_user_id(self):
        new_user = User(id=None)
        with pytest.raises(ValueError):
            new_user.load_from_db()

    def test_load_from_db_exception(self):
        self.mock_table.get_item.side_effect = ClientError(
            {"Error": {"Code": "ValidationError"}}, "GetItem"
        )

        result = self.user.load_from_db()

        self.assertFalse(result)

    def test_save_to_db_success(self):
        self.user.username = "test_username"
        self.user.access_token = "access_token"
        self.user.token_expires_at = int(
            (datetime.now() + timedelta(days=1)).timestamp()
        )
        self.user.refresh_token = "refresh_token"
        self.user.scope = "read"
        self.user.activity_replication = True

        self.mock_table.put_item.return_value = {}

        result = self.user.save_to_db()

        self.assertTrue(result)
        self.mock_table.put_item.assert_called_once()

    def test_save_to_db_exception(self):
        self.mock_table.put_item.side_effect = ClientError(
            {"Error": {"Code": "ValidationError"}}, "PutItem"
        )

        result = self.user.save_to_db()

        self.assertFalse(result)

    def test_save_to_db_no_user_id(self):
        new_user = User(id=None)
        with pytest.raises(ValueError):
            new_user.save_to_db()

    def test_delete_from_db_success(self):
        result = self.user.delete_from_db()

        self.assertTrue(result)
        self.mock_table.delete_item.assert_called_once()

    def test_delete_from_db_exception(self):
        self.mock_table.delete_item.side_effect = ClientError(
            {"Error": {"Code": "ValidationError"}}, "DeleteItem"
        )

        result = self.user.delete_from_db()

        self.assertFalse(result)

    def test_is_token_expired(self):
        self.user.token_expires_at = int(
            (datetime.now() - timedelta(days=1)).timestamp()
        )
        self.assertTrue(self.user.is_token_expired())

        self.user.token_expires_at = int(
            (datetime.now() + timedelta(days=1)).timestamp()
        )
        self.assertFalse(self.user.is_token_expired())

    def test_refresh_tokens(self):
        self.user.is_token_expired = MagicMock(return_value=True)
        self.user.save_to_db = MagicMock()
        self.user.strava.refresh_tokens = MagicMock()

        result = self.user.refresh_tokens()

        self.assertTrue(result)
        self.user.strava.refresh_tokens.assert_called_once()
        self.user.save_to_db.assert_called_once()

    def test_refresh_tokens_not_expired(self):
        self.user.is_token_expired = MagicMock(return_value=False)
        self.user.save_to_db = MagicMock()
        self.user.strava.refresh_tokens = MagicMock()

        result = self.user.refresh_tokens()

        self.assertTrue(result)
        assert not self.user.strava.refresh_tokens.called
        assert not self.user.save_to_db.called

    def test_load_from_auth_code(self):
        auth_code = "test_auth_code"
        self.user.save_to_db = MagicMock()
        self.user.strava.exchange_auth_code = MagicMock()

        self.user.load_from_auth_code(auth_code)

        self.user.strava.exchange_auth_code.assert_called_once_with(auth_code)
        self.user.save_to_db.assert_called_once()


if __name__ == "__main__":
    unittest.main()
