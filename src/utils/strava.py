from src.utils.requests_wrapper import make_request


class Strava:
    STRAVA_BASE_URL = "https://www.strava.com"

    def __init__(
        self,
        user,
        client_id,
        client_secret,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user = user

    def list_activities(self):
        response = make_request(
            url=f"{self.STRAVA_BASE_URL}/api/v3/athlete/activities",
            method="GET",
            headers={"Authorization": f"Bearer {self.user.access_token}"},
        )
        return response

    def get_activity(self, id):
        headers = {"Authorization": f"Bearer {self.user.access_token}"}

        response = make_request(
            url=f"{self.STRAVA_BASE_URL}/api/v3/activities/{id}",
            method="GET",
            headers=headers,
        )
        return response

    def refresh_tokens(self):
        if not self.user.is_token_expired():
            return True

        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.user.refresh_token,
        }

        response = make_request(
            url=f"{self.STRAVA_BASE_URL}/oauth/token", method="POST", data=params
        )

        self.user.access_token = response.get("access_token")
        self.user.expires_at = response.get("expires_at")
        self.user.refresh_token = response.get("refresh_token")

        return True

    def exchange_auth_code(self, auth_code):
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "grant_type": "authorization_code",
        }

        response = make_request(
            url=f"{self.STRAVA_BASE_URL}/oauth/token", method="POST", data=params
        )

        self.user.access_token = response["access_token"]
        self.user.refresh_token = response["refresh_token"]
        self.user.token_expires_at = response["expires_at"]
        self.user.id = response["athlete"]["id"]
        self.user.username = response["athlete"]["username"]
        self.user.firstname = response["athlete"]["firstname"]
        self.user.lastname = response["athlete"]["lastname"]

    def get_activity_streams(self, id):
        headers = {"Authorization": f"Bearer {self.user.access_token}"}

        params = {
            "keys": "latlng,time,altitude,velocity_smooth,time,distance,cadence,heartrate",
            "key_by_type": "true",
        }

        response = make_request(
            url=f"{self.STRAVA_BASE_URL}/api/v3/activities/{id}/streams",
            method="GET",
            headers=headers,
            params=params,
        )

        return response

    def upload_activity_file(self, data, data_type="gpx", name="My activity"):
        headers = {"Authorization": f"Bearer {self.user.access_token}"}

        files = {
            "file": ("activity.gpx", data),
            "data_type": (None, data_type),
            "name": (None, name),
        }

        response = make_request(
            url=f"{self.STRAVA_BASE_URL}/api/v3/uploads",
            method="POST",
            headers=headers,
            files=files,
        )

        return response

    def get_upload(self, upload_id):
        headers = {"Authorization": f"Bearer {self.user.access_token}"}

        response = make_request(
            url=f"{self.STRAVA_BASE_URL}/api/v3/uploads/{upload_id}",
            method="GET",
            headers=headers,
        )

        return response
