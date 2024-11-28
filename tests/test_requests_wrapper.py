import unittest
from unittest.mock import patch, MagicMock
from src.utils.requests_wrapper import make_request
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException

class TestMakeRequest(unittest.TestCase):
    @patch('requests.get')
    def test_make_request_get_success(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        response = make_request("http://example.com", method="GET")
        mock_get.assert_called_once_with("http://example.com")
        self.assertEqual(response, {"key": "value"})

    @patch('requests.post')
    def test_make_request_post_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        response = make_request("http://example.com", method="POST", data={"key": "value"})
        mock_post.assert_called_once_with("http://example.com", data={"key": "value"})
        self.assertEqual(response, {"key": "value"})

    @patch('requests.put')
    def test_make_request_put_success(self, mock_put):
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status.return_value = None
        mock_put.return_value = mock_response

        response = make_request("http://example.com", method="PUT", json={"key": "value"})
        mock_put.assert_called_once_with("http://example.com", json={"key": "value"})
        self.assertEqual(response, {"key": "value"})

    @patch('requests.delete')
    def test_make_request_delete_success(self, mock_delete):
        mock_response = MagicMock()
        mock_response.json.return_value = {"key": "value"}
        mock_response.raise_for_status.return_value = None
        mock_delete.return_value = mock_response

        response = make_request("http://example.com", method="DELETE")
        mock_delete.assert_called_once_with("http://example.com")
        self.assertEqual(response, {"key": "value"})

    def test_make_request_invalid_method(self):
        response = make_request("http://example.com", method="PATCH")
        self.assertIsNone(response)

    @patch('requests.get')
    def test_make_request_http_error(self, mock_get):
        mock_get.side_effect = HTTPError("HTTP Error occurred")
        with patch('builtins.print') as mock_print:
            response = make_request("http://example.com", method="GET")
            self.assertIsNone(response)
            mock_print.assert_called_with("HTTP error occurred: HTTP Error occurred")

    @patch('requests.get')
    def test_make_request_connection_error(self, mock_get):
        mock_get.side_effect = ConnectionError("Connection Error occurred")
        with patch('builtins.print') as mock_print:
            response = make_request("http://example.com", method="GET")
            self.assertIsNone(response)
            mock_print.assert_called_with("Connection error occurred: Connection Error occurred")

    @patch('requests.get')
    def test_make_request_timeout_error(self, mock_get):
        mock_get.side_effect = Timeout("Timeout Error occurred")
        with patch('builtins.print') as mock_print:
            response = make_request("http://example.com", method="GET")
            self.assertIsNone(response)
            mock_print.assert_called_with("Timeout error occurred: Timeout Error occurred")

    @patch('requests.get')
    def test_make_request_request_exception(self, mock_get):
        mock_get.side_effect = RequestException("Request Exception occurred")
        with patch('builtins.print') as mock_print:
            response = make_request("http://example.com", method="GET")
            self.assertIsNone(response)
            mock_print.assert_called_with("An error occurred: Request Exception occurred")