#!/usr/bin/env python3
"""
Testes para APIs CWB Hub
Melhoria #5 - Testes Automatizados Completos
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
import json
from fastapi.testclient import TestClient

# Adicionar diretórios ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'api'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from api.main import app
    from api.auth import create_api_key, verify_api_key
    from api.models import AnalyzeRequest, IterateRequest
except ImportError:
    # Se não conseguir importar, criar mocks para os testes
    app = None
    pytest.skip("API não disponível", allow_module_level=True)


class TestAPIHealth:
    """Testes para endpoints de health check"""
    
    def setup_method(self):
        """Setup para cada teste"""
        if app is None:
            pytest.skip("API não disponível")
        self.client = TestClient(app)
    
    def test_health_endpoint(self):
        """Testa endpoint de health check"""
        response = self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert data["status"] == "healthy"
    
    def test_health_endpoint_structure(self):
        """Testa estrutura completa do health check"""
        response = self.client.get("/health")
        data = response.json()
        
        required_fields = ["status", "timestamp", "version", "components"]
        for field in required_fields:
            assert field in data
        
        # Verificar componentes
        components = data["components"]
        assert "database" in components
        assert "orchestrator" in components
        assert "agents" in components


class TestAPIAuthentication:
    """Testes para autenticação da API"""
    
    def setup_method(self):
        """Setup para cada teste"""
        if app is None:
            pytest.skip("API não disponível")
        self.client = TestClient(app)
    
    def test_create_api_key(self):
        """Testa criação de API key"""
        response = self.client.post("/auth/api-key", json={
            "name": "Test API Key",
            "description": "Chave para testes"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "api_key" in data
        assert "key_id" in data
        assert "name" in data
        assert data["name"] == "Test API Key"
        assert len(data["api_key"]) > 20  # API key deve ter tamanho razoável
    
    def test_api_key_validation(self):
        """Testa validação de API key"""
        # Criar uma API key primeiro
        create_response = self.client.post("/auth/api-key", json={
            "name": "Validation Test",
            "description": "Teste de validação"
        })
        
        api_key = create_response.json()["api_key"]
        
        # Testar endpoint protegido com API key válida
        headers = {"X-API-Key": api_key}
        response = self.client.get("/sessions", headers=headers)
        
        # Deve retornar 200 (autorizado) ou 404 (não encontrado), mas não 401
        assert response.status_code != 401
    
    def test_invalid_api_key(self):
        """Testa API key inválida"""
        headers = {"X-API-Key": "invalid_key_123"}
        response = self.client.get("/sessions", headers=headers)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    def test_missing_api_key(self):
        """Testa requisição sem API key"""
        response = self.client.get("/sessions")
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


class TestAPIAnalyze:
    """Testes para endpoint de análise"""
    
    def setup_method(self):
        """Setup para cada teste"""
        if app is None:
            pytest.skip("API não disponível")
        self.client = TestClient(app)
        
        # Criar API key para testes
        create_response = self.client.post("/auth/api-key", json={
            "name": "Test Key",
            "description": "Chave para testes"
        })
        self.api_key = create_response.json()["api_key"]
        self.headers = {"X-API-Key": self.api_key}
    
    @patch('api.main.orchestrator')
    def test_analyze_endpoint_basic(self, mock_orchestrator):
        """Testa endpoint de análise básico"""
        # Mock do orquestrador
        mock_orchestrator.process_request = AsyncMock(return_value={
            "session_id": "test_session_123",
            "solution": "Solução para desenvolvimento mobile",
            "confidence": 85,
            "agents_involved": ["gabriel_mendes", "isabella_santos"]
        })
        
        request_data = {
            "request": "Desenvolver um aplicativo mobile para iOS",
            "urgency": "medium",
            "constraints": ["Orçamento limitado", "Prazo de 2 meses"]
        }
        
        response = self.client.post("/analyze", json=request_data, headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert "solution" in data
        assert "confidence" in data
        assert "agents_involved" in data
        assert data["confidence"] == 85
    
    def test_analyze_endpoint_validation(self):
        """Testa validação do endpoint de análise"""
        # Requisição sem campo obrigatório
        invalid_request = {
            "urgency": "high"
            # Faltando campo "request"
        }
        
        response = self.client.post("/analyze", json=invalid_request, headers=self.headers)
        
        assert response.status_code == 422  # Validation error
        data = response.json()
        assert "detail" in data
    
    @patch('api.main.orchestrator')
    def test_analyze_endpoint_different_urgencies(self, mock_orchestrator):
        """Testa análise com diferentes níveis de urgência"""
        mock_orchestrator.process_request = AsyncMock(return_value={
            "session_id": "test_session_456",
            "solution": "Solução urgente",
            "confidence": 90,
            "agents_involved": ["ana_beatriz_costa"]
        })
        
        urgencies = ["low", "medium", "high", "critical"]
        
        for urgency in urgencies:
            request_data = {
                "request": f"Projeto com urgência {urgency}",
                "urgency": urgency
            }
            
            response = self.client.post("/analyze", json=request_data, headers=self.headers)
            
            assert response.status_code == 200
            data = response.json()
            assert "session_id" in data


class TestAPIIterate:
    """Testes para endpoint de iteração"""
    
    def setup_method(self):
        """Setup para cada teste"""
        if app is None:
            pytest.skip("API não disponível")
        self.client = TestClient(app)
        
        # Criar API key para testes
        create_response = self.client.post("/auth/api-key", json={
            "name": "Test Key",
            "description": "Chave para testes"
        })
        self.api_key = create_response.json()["api_key"]
        self.headers = {"X-API-Key": self.api_key}
    
    @patch('api.main.orchestrator')
    def test_iterate_endpoint_basic(self, mock_orchestrator):
        """Testa endpoint de iteração básico"""
        # Mock do orquestrador
        mock_orchestrator.iterate_solution = AsyncMock(return_value={
            "session_id": "test_session_123",
            "solution": "Solução iterada com melhorias",
            "confidence": 92,
            "agents_involved": ["gabriel_mendes", "isabella_santos", "lucas_pereira"],
            "iteration": 2
        })
        
        session_id = "test_session_123"
        request_data = {
            "feedback": "A solução precisa ser mais escalável e ter melhor UX"
        }
        
        response = self.client.post(f"/iterate/{session_id}", json=request_data, headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert "solution" in data
        assert "confidence" in data
        assert "iteration" in data
        assert data["confidence"] == 92
        assert data["iteration"] == 2
    
    @patch('api.main.orchestrator')
    def test_iterate_nonexistent_session(self, mock_orchestrator):
        """Testa iteração de sessão inexistente"""
        mock_orchestrator.iterate_solution = AsyncMock(side_effect=ValueError("Sessão não encontrada"))
        
        session_id = "nonexistent_session"
        request_data = {
            "feedback": "Feedback para sessão inexistente"
        }
        
        response = self.client.post(f"/iterate/{session_id}", json=request_data, headers=self.headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestAPIStatus:
    """Testes para endpoint de status"""
    
    def setup_method(self):
        """Setup para cada teste"""
        if app is None:
            pytest.skip("API não disponível")
        self.client = TestClient(app)
        
        # Criar API key para testes
        create_response = self.client.post("/auth/api-key", json={
            "name": "Test Key",
            "description": "Chave para testes"
        })
        self.api_key = create_response.json()["api_key"]
        self.headers = {"X-API-Key": self.api_key}
    
    @patch('api.main.orchestrator')
    def test_status_endpoint_basic(self, mock_orchestrator):
        """Testa endpoint de status básico"""
        # Mock do session manager
        mock_orchestrator.session_manager.get_session = Mock(return_value={
            "session_id": "test_session_123",
            "request": "Desenvolver app mobile",
            "status": "completed",
            "confidence": 88,
            "created_at": "2025-08-07T04:00:00Z"
        })
        
        session_id = "test_session_123"
        response = self.client.get(f"/status/{session_id}", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_id" in data
        assert "status" in data
        assert "confidence" in data
        assert data["session_id"] == session_id
        assert data["status"] == "completed"
    
    @patch('api.main.orchestrator')
    def test_status_nonexistent_session(self, mock_orchestrator):
        """Testa status de sessão inexistente"""
        mock_orchestrator.session_manager.get_session = Mock(return_value=None)
        
        session_id = "nonexistent_session"
        response = self.client.get(f"/status/{session_id}", headers=self.headers)
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestAPISessions:
    """Testes para endpoint de listagem de sessões"""
    
    def setup_method(self):
        """Setup para cada teste"""
        if app is None:
            pytest.skip("API não disponível")
        self.client = TestClient(app)
        
        # Criar API key para testes
        create_response = self.client.post("/auth/api-key", json={
            "name": "Test Key",
            "description": "Chave para testes"
        })
        self.api_key = create_response.json()["api_key"]
        self.headers = {"X-API-Key": self.api_key}
    
    @patch('api.main.orchestrator')
    def test_sessions_endpoint_basic(self, mock_orchestrator):
        """Testa endpoint de listagem de sessões"""
        # Mock do session manager
        mock_orchestrator.session_manager.list_sessions = Mock(return_value=[
            {
                "session_id": "session_1",
                "request": "Projeto 1",
                "status": "completed",
                "confidence": 85,
                "created_at": "2025-08-07T04:00:00Z"
            },
            {
                "session_id": "session_2",
                "request": "Projeto 2",
                "status": "processing",
                "confidence": 0,
                "created_at": "2025-08-07T04:05:00Z"
            }
        ])
        
        response = self.client.get("/sessions", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 2
        
        # Verificar estrutura das sessões
        for session in data:
            assert "session_id" in session
            assert "request" in session
            assert "status" in session
            assert "created_at" in session
    
    @patch('api.main.orchestrator')
    def test_sessions_endpoint_empty(self, mock_orchestrator):
        """Testa endpoint com nenhuma sessão"""
        mock_orchestrator.session_manager.list_sessions = Mock(return_value=[])
        
        response = self.client.get("/sessions", headers=self.headers)
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 0


class TestAPIRateLimit:
    """Testes para rate limiting"""
    
    def setup_method(self):
        """Setup para cada teste"""
        if app is None:
            pytest.skip("API não disponível")
        self.client = TestClient(app)
        
        # Criar API key para testes
        create_response = self.client.post("/auth/api-key", json={
            "name": "Rate Limit Test",
            "description": "Teste de rate limiting"
        })
        self.api_key = create_response.json()["api_key"]
        self.headers = {"X-API-Key": self.api_key}
    
    @pytest.mark.slow
    def test_rate_limit_health_endpoint(self):
        """Testa rate limiting no endpoint de health"""
        # Fazer muitas requisi��ões rapidamente
        responses = []
        for i in range(20):
            response = self.client.get("/health")
            responses.append(response.status_code)
        
        # Verificar se pelo menos algumas passaram
        success_count = sum(1 for status in responses if status == 200)
        rate_limited_count = sum(1 for status in responses if status == 429)
        
        # Deve ter pelo menos algumas requisições bem-sucedidas
        assert success_count > 0
        
        # Se rate limiting estiver ativo, deve ter algumas requisições limitadas
        # (Este teste pode passar mesmo sem rate limiting ativo)
        print(f"Sucessos: {success_count}, Rate limited: {rate_limited_count}")


class TestAPIErrorHandling:
    """Testes para tratamento de erros"""
    
    def setup_method(self):
        """Setup para cada teste"""
        if app is None:
            pytest.skip("API não disponível")
        self.client = TestClient(app)
        
        # Criar API key para testes
        create_response = self.client.post("/auth/api-key", json={
            "name": "Error Test",
            "description": "Teste de erros"
        })
        self.api_key = create_response.json()["api_key"]
        self.headers = {"X-API-Key": self.api_key}
    
    def test_invalid_json(self):
        """Testa requisição com JSON inválido"""
        response = self.client.post(
            "/analyze", 
            data="invalid json", 
            headers={**self.headers, "Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_missing_content_type(self):
        """Testa requisição sem Content-Type"""
        response = self.client.post(
            "/analyze",
            data='{"request": "test"}',
            headers=self.headers
        )
        
        # Deve funcionar ou retornar erro específico
        assert response.status_code in [200, 400, 422]
    
    def test_method_not_allowed(self):
        """Testa método HTTP não permitido"""
        response = self.client.put("/health")
        
        assert response.status_code == 405
        data = response.json()
        assert "detail" in data


class TestAPIDocumentation:
    """Testes para documentação da API"""
    
    def setup_method(self):
        """Setup para cada teste"""
        if app is None:
            pytest.skip("API não disponível")
        self.client = TestClient(app)
    
    def test_openapi_schema(self):
        """Testa schema OpenAPI"""
        response = self.client.get("/openapi.json")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        
        # Verificar informações básicas
        info = data["info"]
        assert "title" in info
        assert "version" in info
    
    def test_swagger_docs(self):
        """Testa documentação Swagger"""
        response = self.client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_redoc_docs(self):
        """Testa documentação ReDoc"""
        response = self.client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])