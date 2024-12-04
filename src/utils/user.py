from datetime import datetime
from botocore.exceptions import ClientError
from cryptography.fernet import Fernet
from src.utils.ssm import get_parameter
from src.utils.boto3_singleton import get_boto3_client, get_boto3_resource
from src.utils.strava import Strava


class User:

    def __init__(self, id=None, table_name="users"):
        self.id = id
        self.username = None
        self._access_token = None
        self.token_expires_at = None
        self._refresh_token = None
        self._scope = None
        self.children = None
        self.table_name = table_name

        self.dynamodb = get_boto3_resource("dynamodb")
        self.table = self.dynamodb.Table(self.table_name)

        self.ssm = get_boto3_client("ssm")

        self._client_secret = None
        self._client_id = None

        self._cipher = None
        self._encryption_key = None

        self.strava = Strava(
            self,
            get_parameter("strava_client_id", False, self.ssm),
            get_parameter("strava_client_secret", True, self.ssm),
        )

    @property
    def scope(self):
        return self._scope

    @scope.setter
    def scope(self, value):
        self._scope = value

    @property
    def access_token(self):
        if self._access_token is None:
            return None
        return self.cipher.decrypt(self._access_token).decode()

    @access_token.setter
    def access_token(self, value):
        if value is None:
            self._access_token = None
        else:
            self._access_token = self.cipher.encrypt(value.encode())

    @property
    def refresh_token(self):
        if self._refresh_token is None:
            return None
        return self.cipher.decrypt(self._refresh_token).decode()

    @refresh_token.setter
    def refresh_token(self, value):
        if value is None:
            self._refresh_token = None
        else:
            self._refresh_token = self.cipher.encrypt(value.encode())

    @property
    def encryption_key(self):
        if not self._encryption_key:
            self._encryption_key = get_parameter("encryption_key", True, self.ssm)
        return self._encryption_key

    @property
    def cipher(self):
        if not self._cipher:
            self._cipher = Fernet(self.encryption_key)
        return self._cipher

    def load_from_db(self):
        if not self.id:
            raise ValueError("User ID must be set to load data from DB.")

        try:
            response = self.table.get_item(Key={"id": self.id})
            print("DynamoDB Response:", response)  # Debugging output
        except ClientError as e:
            print(f"Error fetching user data from DynamoDB: {e}")
            return False

        if "Item" in response:
            user_data = response["Item"]
            self.username = user_data.get("username")
            self.access_token = user_data.get("access_token")
            self.token_expires_at = user_data.get("token_expires_at")
            self.refresh_token = user_data.get("refresh_token")
            self.scope = user_data.get("scope")
            self.children = user_data.get("children")
            return True
        else:
            print(f"No data found for user ID: {self.id}")
            return False

    def save_to_db(self):
        if not self.id:
            raise ValueError("User ID must be set to save data to DB.")

        user_data = {
            "id": self.id,
            "username": self.username,
            "access_token": self.access_token,
            "token_expires_at": self.token_expires_at,
            "refresh_token": self.refresh_token,
            "scope": self.scope,
            "children": self.children,
        }

        try:
            self.table.put_item(Item=user_data)
            return True
        except ClientError as e:
            print(f"Error saving user data to DynamoDB: {e}")
            return False

    def delete_from_db(self):
        try:
            self.table.delete_item(Key={"id": self.id})
            return True
        except ClientError as e:
            print(f"Error deleting user data to DynamoDB: {e}")
            return False

    def is_token_expired(self):
        return self.token_expires_at < int(datetime.now().timestamp())

    def refresh_tokens(self):
        if not self.is_token_expired():
            return True

        self.strava.refresh_tokens()

        self.save_to_db()

        return True

    def load_from_auth_code(self, auth_code):
        self.strava.exchange_auth_code(auth_code)

        self.save_to_db()
