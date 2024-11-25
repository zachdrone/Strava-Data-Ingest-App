import boto3
import requests
from datetime import datetime
from botocore.exceptions import ClientError
from lambdas.helpers.auth import get_parameter, encrypt_data, decrypt_data
from lambdas.helpers.boto3_singleton import get_boto3_client, get_boto3_resource
from lambdas.helpers.requests_wrapper import make_request

class User():

    def __init__(
            self,
            id = None,
            table_name='users'
        ):
        self.id = id
        self.username = None
        self._access_token = None
        self.token_expires_at = None
        self._refresh_token = None
        self._scope = None
        self.activity_replication = None
        self.table_name = table_name

        self.dynamodb = get_boto3_resource('dynamodb')
        self.table = self.dynamodb.Table(self.table_name)

        self.ssm = get_boto3_client('ssm')

        self._client_secret = None
        self._client_id = None

    def load_from_db(self):
        """
        Load user data from DynamoDB based on id.
        Populate instance variables with the retrieved data.
        """
        if not self.id:
            raise ValueError("User ID must be set to load data from DB.")
        
        try:
            response = self.table.get_item(Key={'id': self.id})
        except ClientError as e:
            print(f"Error fetching user data from DynamoDB: {e}")
            return False
        
        if 'Item' in response:
            user_data = response['Item']
            self.username = user_data.get('username')
            self.access_token = user_data.get('access_token')
            self.token_expires_at = user_data.get('token_expires_at')
            self.refresh_token = user_data.get('refresh_token')
            self.scope = user_data.get('scope')
            self.activity_replication = user_data.get('activity_replication')
            return True
        else:
            print(f"No data found for user ID: {self.id}")
            return False
        
    def save_to_db(self):
        """
        Save or update the current user information to DynamoDB.
        """
        if not self.id:
            raise ValueError("User ID must be set to save data to DB.")
        
        user_data = {
            'id': self.id,
            'username': self.username,
            'access_token': self.access_token,
            'token_expires_at': self.token_expires_at,
            'refresh_token': self.refresh_token,
            'scope': self.scope,
            'activity_replication': self.activity_replication
        }
        
        try:
            self.table.put_item(Item=user_data)
            return True
        except ClientError as e:
            print(f"Error saving user data to DynamoDB: {e}")
            return False

    def is_token_expired(self):
        """
        Dummy method to check if the token is expired (implement your logic).
        """
        # Add your logic to determine if the token is expired
        return self.token_expires_at < int(datetime.now().timestamp())
    
    def refresh_tokens(self):
        if not self.is_token_expired():
            return True
        
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.refresh_token,
        }

        r = requests.post(
            "https://www.strava.com/oauth/token",
            data=params,
        )

        data = r.json()
        self.access_token = data.get('access_token')
        self.expires_at = data.get('expires_at')
        self.refresh_token = data.get('refresh_token')

        self.save_to_db()

        return True
    
    def load_from_auth_code(self, auth_code):
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "grant_type": "authorization_code"
        }

        r = requests.post(
            "https://www.strava.com/oauth/token",
            data=params,
        )
        auth = r.json()

        self.access_token = auth['access_token']
        self.refresh_token = auth['refresh_token']
        self.token_expires_at = auth['expires_at']

        user = auth['athlete']
        self.id=user['id']
        self.username = user['username']
        self.activity_replication = []

        self.save_to_db()

    @property
    def scope(self):
        return self._scope
    
    @scope.setter
    def scope(self, value):
        self._scope = value

    @property
    def access_token(self):
        return decrypt_data(self._access_token)

    @access_token.setter
    def access_token(self, value):
        self._access_token = encrypt_data(value)

    @property
    def refresh_token(self):
        return decrypt_data(self._refresh_token)
    
    @refresh_token.setter
    def refresh_token(self, value):
        self._refresh_token = encrypt_data(value)

    @property
    def client_id(self):
        if not self._client_id:
            self._client_id = get_parameter('strava_client_id', False, self.ssm)
        return self._client_id
    
    @property
    def client_secret(self):
        if not self._client_secret:
            self._client_secret = get_parameter('strava_client_secret', True, self.ssm)
        return self._client_secret