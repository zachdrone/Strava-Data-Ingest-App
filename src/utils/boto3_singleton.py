import boto3
from threading import Lock

class Boto3SessionSingleton:
    _instance = None
    _lock = Lock()

    def __new__(cls, profile_name=None, region_name='us-east-1'):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialize_session(profile_name, region_name)
        return cls._instance

    def _initialize_session(self, profile_name=None, region_name='us-east-1'):
        self.session = boto3.Session(profile_name=profile_name, region_name=region_name)

    def get_client(self, service_name):
        return self.session.client(service_name)

    def get_resource(self, service_name):
        return self.session.resource(service_name)

# Global access functions
def get_boto3_session():
    return Boto3SessionSingleton()

def get_boto3_client(service_name):
    return Boto3SessionSingleton().get_client(service_name)

def get_boto3_resource(service_name):
    return Boto3SessionSingleton().get_resource(service_name)
