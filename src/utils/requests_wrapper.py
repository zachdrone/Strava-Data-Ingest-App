import requests
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

def make_request(url, method='GET', **kwargs):
    try:
        if method == 'GET':
            response = requests.get(url, **kwargs)
        elif method == 'POST':
            response = requests.post(url, **kwargs)
        elif method == 'PUT':
            response = requests.put(url, **kwargs)
        elif method == 'DELETE':
            response = requests.delete(url, **kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

        response.raise_for_status()

        return response.json()

    except HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except ConnectionError as conn_err:
        print(f"Connection error occurred: {conn_err}")
    except Timeout as timeout_err:
        print(f"Timeout error occurred: {timeout_err}")
    except RequestException as req_err:
        print(f"An error occurred: {req_err}")
    except ValueError as val_err:
        print(f"Invalid HTTP method: {val_err}")

    return None
