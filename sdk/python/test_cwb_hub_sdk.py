"""
Testes automatizados para o SDK Python do CWB Hub Hybrid AI System
"""
import unittest
from unittest.mock import patch, MagicMock
from cwb_hub_sdk import CWBHubClient

class TestCWBHubClient(unittest.TestCase):
    def setUp(self):
        self.api_url = "http://localhost:8000"
        self.api_key = "test_key"
        self.client = CWBHubClient(self.api_url, self.api_key)

    @patch('cwb_hub_sdk.requests.Session')
    def test_health(self, mock_session):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "ok"}
        mock_resp.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_resp
        client = CWBHubClient(self.api_url, self.api_key)
        self.assertEqual(client.health(), {"status": "ok"})

    @patch('cwb_hub_sdk.requests.Session')
    def test_analyze(self, mock_session):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"result": "analyzed"}
        mock_resp.raise_for_status.return_value = None
        mock_session.return_value.post.return_value = mock_resp
        client = CWBHubClient(self.api_url, self.api_key)
        self.assertEqual(client.analyze({"title": "test"}), {"result": "analyzed"})

    @patch('cwb_hub_sdk.requests.Session')
    def test_iterate(self, mock_session):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"result": "iterated"}
        mock_resp.raise_for_status.return_value = None
        mock_session.return_value.post.return_value = mock_resp
        client = CWBHubClient(self.api_url, self.api_key)
        self.assertEqual(client.iterate("abc123", "feedback"), {"result": "iterated"})

    @patch('cwb_hub_sdk.requests.Session')
    def test_status(self, mock_session):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"status": "session_status"}
        mock_resp.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_resp
        client = CWBHubClient(self.api_url, self.api_key)
        self.assertEqual(client.status("abc123"), {"status": "session_status"})

    @patch('cwb_hub_sdk.requests.Session')
    def test_sessions(self, mock_session):
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"sessions": [1,2,3]}
        mock_resp.raise_for_status.return_value = None
        mock_session.return_value.get.return_value = mock_resp
        client = CWBHubClient(self.api_url, self.api_key)
        self.assertEqual(client.sessions(), {"sessions": [1,2,3]})

if __name__ == "__main__":
    unittest.main()
