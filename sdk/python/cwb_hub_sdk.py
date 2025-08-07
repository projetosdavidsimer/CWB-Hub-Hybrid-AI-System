"""
CWB Hub Python SDK
SDK oficial para integração com a API REST do CWB Hub Hybrid AI System
"""

import requests
from typing import Optional, Dict, Any

class CWBHubClient:
    """
    Cliente Python para a API REST do CWB Hub
    """
    def __init__(self, api_url: str, api_key: Optional[str] = None):
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        self.session.headers.update({"Content-Type": "application/json"})

    def health(self) -> Dict[str, Any]:
        """Verifica o status da API"""
        resp = self.session.get(f"{self.api_url}/health")
        resp.raise_for_status()
        return resp.json()

    def analyze(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Envia um projeto para análise pela equipe CWB Hub"""
        resp = self.session.post(f"{self.api_url}/analyze", json=project_data)
        resp.raise_for_status()
        return resp.json()

    def iterate(self, session_id: str, feedback: str) -> Dict[str, Any]:
        """Envia feedback para iteração de solução"""
        resp = self.session.post(f"{self.api_url}/iterate/{session_id}", json={"feedback": feedback})
        resp.raise_for_status()
        return resp.json()

    def status(self, session_id: str) -> Dict[str, Any]:
        """Consulta o status de uma sessão"""
        resp = self.session.get(f"{self.api_url}/status/{session_id}")
        resp.raise_for_status()
        return resp.json()

    def sessions(self) -> Dict[str, Any]:
        """Lista sessões recentes"""
        resp = self.session.get(f"{self.api_url}/sessions")
        resp.raise_for_status()
        return resp.json()

    def set_api_key(self, api_key: str):
        """Atualiza a API key usada nas requisições"""
        self.api_key = api_key
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})
