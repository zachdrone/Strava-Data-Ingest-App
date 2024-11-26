from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import datetime, timedelta, timezone
from lambdas.helpers.requests_wrapper import make_request

class Strava():
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
            method='GET',
            headers={
                "Authorization": f"Bearer {self.user.access_token}"
            }
        )
        return response
    
    def get_activity(self, id):
        headers = {
            "Authorization": f"Bearer {self.user.access_token}"
        }

        response = make_request(
            url=f"{self.STRAVA_BASE_URL}/activities/{id}",
            method='GET',
            headers=headers
        )
        return response

    def refresh_tokens(self):
        if not self.is_token_expired():
            return True
        
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": self.user.refresh_token,
        }
        
        response = make_request(
            url=f"{self.STRAVA_BASE_URL}/oauth/token",
            method='POST',
            data=params
        )

        self.user.access_token = response.get('access_token')
        self.user.expires_at = response.get('expires_at')
        self.user.refresh_token = response.get('refresh_token')

        return True
    
    def exchange_auth_code(self, auth_code):
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": auth_code,
            "grant_type": "authorization_code"
        }

        response = make_request(
            url=f"{self.STRAVA_BASE_URL}/oauth/token",
            method='POST',
            data=params
        )

        self.user.access_token = response['access_token']
        self.user.refresh_token = response['refresh_token']
        self.user.token_expires_at = response['expires_at']
        self.user.id = response['athlete']['id']
        self.user.username = response['athlete']['username']

    def get_activity_streams(self, id):
        headers = {
            "Authorization": f"Bearer {self.user.access_token}"
        }
        
        params = {
            "keys": "latlng,time,altitude,velocity_smooth,time,distance,cadence",
            "key_by_type": "true"
        }

        response = make_request(
            url=f"{self.STRAVA_BASE_URL}/activities/{id}/streams",
            method='GET',
            headers=headers,
            params=params
        )
                
        return response
        
    def create_gpx_from_streams(self, stream_data, activity):
        latlng = stream_data.get("latlng", {}).get("data", [])
        altitude = stream_data.get("altitude", {}).get("data", [])
        elapsed_time = stream_data.get("time", {}).get("data", [])        
        distance = stream_data.get("distance", {}).get("data", [])
        cadence = stream_data.get("cadence", {}).get("data", [])

        activity_start_time_utc = activity.get("start_date")

        start_datetime = datetime.strptime(activity_start_time_utc, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc)

        gpx = Element('gpx', version="1.1", creator="Strava Project")
        trk = SubElement(gpx, 'trk')
        name = SubElement(trk, 'name')
        name.text = "Downloaded Activity"
        trkseg = SubElement(trk, 'trkseg')

        for i in range(len(latlng)):
            trkpt = SubElement(trkseg, 'trkpt', lat=str(latlng[i][0]), lon=str(latlng[i][1]))
            if i < len(altitude):
                ele = SubElement(trkpt, 'ele')
                ele.text = str(altitude[i])
            if i < len(elapsed_time):
                timestamp = (start_datetime + timedelta(seconds=elapsed_time[i])).isoformat()
                time_elem = SubElement(trkpt, 'time')
                time_elem.text = timestamp
            if i < len(distance):
                extensions = SubElement(trkpt, 'extensions')
                distance_elem = SubElement(extensions, 'distance')
                distance_elem.text = str(distance[i])
            if i < len(cadence):
                extensions = SubElement(trkpt, 'extensions')
                cadence_elem = SubElement(extensions, 'cadence')
                cadence_elem.text = str(cadence[i])
        
        gpx_data = tostring(gpx, encoding='utf-8', method='xml')
        return gpx_data

    def upload_gpx(self, gpx_data, name="Duplicated Activity"):
        headers = {
            "Authorization": f"Bearer {self.user.access_token}"
        }
        
        files = {
            "file": ("activity.gpx", gpx_data),
            "data_type": (None, "gpx"),
            "name": (None, name),
        }
                
        response = make_request(
            url=f"{self.STRAVA_BASE_URL}/uploads",
            method='POST',
            headers=headers,
            files=files
        )
        
        return response
    
    def get_upload(self, upload_id):
        headers = {
            "Authorization": f"Bearer {self.user.access_token}"
        }

        response = make_request(
            url=f"{self.STRAVA_BASE_URL}/uploads/{upload_id}",
            method='GET',
            headers=headers,
        )

        return response
