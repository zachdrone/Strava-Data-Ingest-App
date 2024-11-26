import requests
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring
from datetime import datetime, timedelta, timezone

class Strava():
    API_BASE_URL = "https://www.strava.com/api/v3"

    def __init__(
            self,
            client_id,
            client_secret
        ):
        self.client_id = client_id
        self.client_secret = client_secret

    def list_activities(self, access_token):
        r = requests.get(
            f"{self.API_BASE_URL}/athlete/activities",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )
        return r.json()
    
    def get_activity(self, id, access_token):
        r = requests.get(
            f"{self.API_BASE_URL}/activities/{id}",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )
        return r.json()

    def refresh_tokens(self, refresh_token):
        if not self.is_token_expired():
            return True
        
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        r = requests.post(
            "https://www.strava.com/oauth/token",
            data=params,
        )

        data = r.json()

        return {
            "access_token": data.get('access_token'),
            "expires_at": data.get('expires_at'),
            "refresh_token": data.get('refresh_token')
        }
    
    def exchange_auth_code(self, auth_code):
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
        user = auth['athlete']
        return  {
            "access_token": auth['access_token'],
            "refresh_token": auth['refresh_token'],
            "token_expires_at": auth['expires_at'],
            "id": user['id'],
            "username": user['username']
        }

    def get_activity_streams(self, id, access_token):
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        params = {
            "keys": "latlng,time,altitude,velocity_smooth,time,distance,cadence",
            "key_by_type": "true"
        }
        
        response = requests.get(f"{self.API_BASE_URL}/activities/{id}/streams", headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error retrieving activity streams: {response.status_code}")
            print(response.text)
            return None
        
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

    def upload_gpx(self, gpx_data, access_token, name="Duplicated Activity"):
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        files = {
            "file": ("activity.gpx", gpx_data),
            "data_type": (None, "gpx"),
            "name": (None, name),
        }
        
        upload_url = f"{self.API_BASE_URL}/uploads"
        response = requests.post(upload_url, headers=headers, files=files)
        
        if response.status_code == 201:
            print("GPX uploaded successfully.")
            return response.json()
        else:
            print(f"Error uploading GPX: {response.status_code}")
            print(response.text)
        
        return None
    
    def get_upload(self, upload_id, access_token):
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        upload_url = f"{self.API_BASE_URL}/uploads/{upload_id}"
        response = requests.get(upload_url, headers=headers)
        return response.json()
