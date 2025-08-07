#!/usr/bin/env python3
"""
Testes de integração para o Orquestrador CWB Hub
Melhoria #5 - Testes Automatizados Completos
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from orchestrator.hybrid_orchestrator import HybridOrchestrator
from orchestrator.collaboration_manager import CollaborationManager
from orchestrator.session_manager import SessionManager
from orchestrator.confidence_calculator import ConfidenceCalculator


class TestHybridOrchestrator:
    """Testes para o Orquestrador Híbrido"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.orchestrator = HybridOrchestrator()
    
    def test_orchestrator_initialization(self):
        """Testa inicialização do orquestrador"""
        assert self.orchestrator is not None
        assert hasattr(self.orchestrator, 'agents')
        assert hasattr(self.orchestrator, 'collaboration_manager')
        assert hasattr(self.orchestrator, 'session_manager')
        assert len(self.orchestrator.agents) == 8  # 8 agentes especialistas
    
    def test_agents_loaded(self):
        """Testa se todos os agentes foram carregados"""
        expected_agents = [
            "ana_beatriz_costa",
            "carlos_eduardo_santos", 
            "sofia_oliveira",
            "gabriel_mendes",
            "isabella_santos",
            "lucas_pereira",
            "mariana_rodrigues",
            "pedro_henrique_almeida"
        ]
        
        loaded_agents = list(self.orchestrator.agents.keys())
        
        for expected_agent in expected_agents:
            assert expected_agent in loaded_agents
    
    @pytest.mark.asyncio
    async def test_process_request_basic(self):
        """Testa processamento básico de requisição"""
        request = "Preciso desenvolver um aplicativo mobile para iOS"
        
        # Mock das dependências para teste isolado
        with patch.object(self.orchestrator.session_manager, 'create_session') as mock_create:
            mock_create.return_value = "test_session_123"
            
            with patch.object(self.orchestrator, '_select_relevant_agents') as mock_select:
                mock_select.return_value = ["gabriel_mendes", "isabella_santos"]
                
                with patch.object(self.orchestrator, '_coordinate_collaboration') as mock_coord:
                    mock_coord.return_value = {
                        "solution": "Solução para app iOS",
                        "confidence": 85,
                        "agents_involved": ["gabriel_mendes", "isabella_santos"]
                    }
                    
                    result = await self.orchestrator.process_request(request)
                    
                    assert isinstance(result, dict)
                    assert "session_id" in result
                    assert "solution" in result
                    assert "confidence" in result
                    assert "agents_involved" in result
    
    def test_select_relevant_agents(self):
        """Testa seleção de agentes relevantes"""
        # Teste para requisição mobile
        mobile_request = "Desenvolver aplicativo mobile para Android e iOS"
        relevant_agents = self.orchestrator._select_relevant_agents(mobile_request)
        
        assert "gabriel_mendes" in relevant_agents  # Engenheiro Mobile
        assert "isabella_santos" in relevant_agents  # Designer UX/UI
    
    def test_select_relevant_agents_web(self):
        """Testa seleção de agentes para desenvolvimento web"""
        web_request = "Criar uma aplicação web com React e Node.js"
        relevant_agents = self.orchestrator._select_relevant_agents(web_request)
        
        assert "sofia_oliveira" in relevant_agents  # Full Stack
        assert "carlos_eduardo_santos" in relevant_agents  # Arquiteto
    
    def test_select_relevant_agents_devops(self):
        """Testa seleção de agentes para DevOps"""
        devops_request = "Configurar pipeline CI/CD com Docker e Kubernetes"
        relevant_agents = self.orchestrator._select_relevant_agents(devops_request)
        
        assert "mariana_rodrigues" in relevant_agents  # DevOps
    
    @pytest.mark.asyncio
    async def test_coordinate_collaboration(self):
        """Testa coordenação de colaboração entre agentes"""
        request = "Desenvolver sistema de e-commerce"
        selected_agents = ["carlos_eduardo_santos", "sofia_oliveira", "lucas_pereira"]
        
        # Mock dos agentes para teste
        with patch.object(self.orchestrator.agents["carlos_eduardo_santos"], 'analyze_request') as mock_carlos:
            mock_carlos.return_value = "Análise de arquitetura para e-commerce"
            
            with patch.object(self.orchestrator.agents["sofia_oliveira"], 'analyze_request') as mock_sofia:
                mock_sofia.return_value = "Análise de desenvolvimento web"
                
                with patch.object(self.orchestrator.agents["lucas_pereira"], 'analyze_request') as mock_lucas:
                    mock_lucas.return_value = "Análise de qualidade e testes"
                    
                    result = await self.orchestrator._coordinate_collaboration(request, selected_agents)
                    
                    assert isinstance(result, dict)
                    assert "solution" in result
                    assert "confidence" in result
                    assert "agents_involved" in result
                    assert len(result["agents_involved"]) == 3
    
    def test_calculate_confidence(self):
        """Testa cálculo de confiança"""
        responses = [
            "Resposta detalhada com análise técnica completa",
            "Resposta básica",
            "Análise profunda com múltiplas considerações e alternativas"
        ]
        
        confidence = self.orchestrator._calculate_confidence(responses, 3)
        
        assert isinstance(confidence, int)
        assert 0 <= confidence <= 100
    
    @pytest.mark.asyncio
    async def test_iterate_solution(self):
        """Testa iteração de solução"""
        session_id = "test_session_123"
        feedback = "A solução precisa ser mais escalável"
        
        # Mock da sessão existente
        with patch.object(self.orchestrator.session_manager, 'get_session') as mock_get:
            mock_get.return_value = {
                "request": "Sistema de e-commerce",
                "agents_involved": ["carlos_eduardo_santos", "sofia_oliveira"],
                "solution": "Solução inicial"
            }
            
            with patch.object(self.orchestrator, '_coordinate_collaboration') as mock_coord:
                mock_coord.return_value = {
                    "solution": "Solução iterada com maior escalabilidade",
                    "confidence": 90,
                    "agents_involved": ["carlos_eduardo_santos", "sofia_oliveira"]
                }
                
                result = await self.orchestrator.iterate_solution(session_id, feedback)
                
                assert isinstance(result, dict)
                assert "solution" in result
                assert "confidence" in result
                assert result["confidence"] > 0


class TestCollaborationManager:
    """Testes para o Gerenciador de Colaboração"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.collaboration_manager = CollaborationManager()
    
    def test_collaboration_manager_initialization(self):
        """Testa inicialização do gerenciador de colaboração"""
        assert self.collaboration_manager is not None
        assert hasattr(self.collaboration_manager, 'collaboration_history')
        assert isinstance(self.collaboration_manager.collaboration_history, list)
    
    def test_determine_collaboration_type(self):
        """Testa determinação do tipo de colaboração"""
        # Teste para revisão por pares
        collab_type = self.collaboration_manager._determine_collaboration_type(
            "carlos_eduardo_santos", "sofia_oliveira", "Arquitetura de sistema"
        )
        assert collab_type in ["peer_review", "expertise_sharing", "joint_analysis"]
    
    @pytest.mark.asyncio
    async def test_facilitate_collaboration(self):
        """Testa facilitação de colaboração"""
        # Mock dos agentes
        agent1 = Mock()
        agent1.profile.agent_id = "carlos_eduardo_santos"
        agent1.collaborate_with = AsyncMock(return_value="Colaboração do Carlos")
        
        agent2 = Mock()
        agent2.profile.agent_id = "sofia_oliveira"
        agent2.collaborate_with = AsyncMock(return_value="Colaboração da Sofia")
        
        result = await self.collaboration_manager.facilitate_collaboration(
            agent1, agent2, "Desenvolvimento de API"
        )
        
        assert isinstance(result, dict)
        assert "type" in result
        assert "responses" in result
        assert len(result["responses"]) == 2


class TestSessionManager:
    """Testes para o Gerenciador de Sessões"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.session_manager = SessionManager()
    
    def test_session_manager_initialization(self):
        """Testa inicialização do gerenciador de sessões"""
        assert self.session_manager is not None
        assert hasattr(self.session_manager, 'sessions')
        assert isinstance(self.session_manager.sessions, dict)
    
    def test_create_session(self):
        """Testa criação de sessão"""
        request = "Desenvolver aplicativo mobile"
        session_id = self.session_manager.create_session(request)
        
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        assert session_id in self.session_manager.sessions
        
        session = self.session_manager.sessions[session_id]
        assert session["request"] == request
        assert "created_at" in session
        assert "status" in session
        assert session["status"] == "active"
    
    def test_get_session(self):
        """Testa recuperação de sessão"""
        request = "Teste de sessão"
        session_id = self.session_manager.create_session(request)
        
        retrieved_session = self.session_manager.get_session(session_id)
        
        assert retrieved_session is not None
        assert retrieved_session["request"] == request
    
    def test_get_nonexistent_session(self):
        """Testa recuperação de sessão inexistente"""
        result = self.session_manager.get_session("nonexistent_session")
        assert result is None
    
    def test_update_session(self):
        """Testa atualização de sessão"""
        request = "Teste de atualização"
        session_id = self.session_manager.create_session(request)
        
        updates = {
            "solution": "Solução teste",
            "confidence": 85,
            "agents_involved": ["agent1", "agent2"]
        }
        
        success = self.session_manager.update_session(session_id, updates)
        assert success is True
        
        updated_session = self.session_manager.get_session(session_id)
        assert updated_session["solution"] == "Solução teste"
        assert updated_session["confidence"] == 85
        assert updated_session["agents_involved"] == ["agent1", "agent2"]
    
    def test_list_sessions(self):
        """Testa listagem de sessões"""
        # Criar algumas sessões
        session1 = self.session_manager.create_session("Teste 1")
        session2 = self.session_manager.create_session("Teste 2")
        
        sessions = self.session_manager.list_sessions()
        
        assert isinstance(sessions, list)
        assert len(sessions) >= 2
        
        session_ids = [s["session_id"] for s in sessions]
        assert session1 in session_ids
        assert session2 in session_ids


class TestConfidenceCalculator:
    """Testes para o Calculador de Confiança"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.calculator = ConfidenceCalculator()
    
    def test_confidence_calculator_initialization(self):
        """Testa inicialização do calculador"""
        assert self.calculator is not None
    
    def test_calculate_response_quality(self):
        """Testa cálculo de qualidade de resposta"""
        # Resposta detalhada
        detailed_response = "Esta é uma análise detalhada com múltiplas considerações técnicas, incluindo arquitetura, performance, segurança e escalabilidade. A solução proposta considera todos os aspectos relevantes."
        quality_detailed = self.calculator._calculate_response_quality(detailed_response)
        
        # Resposta básica
        basic_response = "Solução simples"
        quality_basic = self.calculator._calculate_response_quality(basic_response)
        
        assert quality_detailed > quality_basic
        assert 0 <= quality_detailed <= 100
        assert 0 <= quality_basic <= 100
    
    def test_calculate_agent_expertise_match(self):
        """Testa cálculo de correspondência de expertise"""
        # Mock de agente com expertise relevante
        agent_mobile = Mock()
        agent_mobile.profile.expertise_areas = ["Desenvolvimento mobile", "iOS", "Android"]
        
        mobile_request = "Desenvolver aplicativo mobile para iOS"
        match_score = self.calculator._calculate_agent_expertise_match(agent_mobile, mobile_request)
        
        assert isinstance(match_score, (int, float))
        assert 0 <= match_score <= 100
    
    def test_calculate_collaboration_synergy(self):
        """Testa cálculo de sinergia de colaboração"""
        agents = ["carlos_eduardo_santos", "sofia_oliveira", "lucas_pereira"]
        synergy = self.calculator._calculate_collaboration_synergy(agents)
        
        assert isinstance(synergy, (int, float))
        assert 0 <= synergy <= 100
    
    def test_calculate_overall_confidence(self):
        """Testa cálculo de confiança geral"""
        responses = [
            "Análise detalhada de arquitetura com considerações de performance",
            "Implementação completa com testes automatizados",
            "Deploy com monitoramento e alertas"
        ]
        
        agents_count = 3
        confidence = self.calculator.calculate_confidence(responses, agents_count)
        
        assert isinstance(confidence, int)
        assert 0 <= confidence <= 100


class TestIntegrationScenarios:
    """Testes de cenários de integração completos"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.orchestrator = HybridOrchestrator()
    
    @pytest.mark.asyncio
    async def test_complete_mobile_app_scenario(self):
        """Testa cenário completo de desenvolvimento de app mobile"""
        request = "Desenvolver um aplicativo de delivery para iOS e Android com backend Node.js"
        
        # Este teste simula um fluxo completo
        with patch.object(self.orchestrator, '_select_relevant_agents') as mock_select:
            mock_select.return_value = ["gabriel_mendes", "sofia_oliveira", "isabella_santos"]
            
            with patch.object(self.orchestrator, '_coordinate_collaboration') as mock_coord:
                mock_coord.return_value = {
                    "solution": "App de delivery com React Native e backend Node.js",
                    "confidence": 88,
                    "agents_involved": ["gabriel_mendes", "sofia_oliveira", "isabella_santos"]
                }
                
                result = await self.orchestrator.process_request(request)
                
                assert result["confidence"] > 80
                assert "gabriel_mendes" in result["agents_involved"]  # Mobile
                assert "sofia_oliveira" in result["agents_involved"]   # Backend
                assert "isabella_santos" in result["agents_involved"] # UX/UI
    
    @pytest.mark.asyncio
    async def test_complete_web_system_scenario(self):
        """Testa cenário completo de sistema web"""
        request = "Criar um sistema de e-commerce completo com React, Node.js e PostgreSQL"
        
        with patch.object(self.orchestrator, '_select_relevant_agents') as mock_select:
            mock_select.return_value = ["carlos_eduardo_santos", "sofia_oliveira", "mariana_rodrigues", "lucas_pereira"]
            
            with patch.object(self.orchestrator, '_coordinate_collaboration') as mock_coord:
                mock_coord.return_value = {
                    "solution": "Sistema de e-commerce com arquitetura escalável",
                    "confidence": 92,
                    "agents_involved": ["carlos_eduardo_santos", "sofia_oliveira", "mariana_rodrigues", "lucas_pereira"]
                }
                
                result = await self.orchestrator.process_request(request)
                
                assert result["confidence"] > 85
                assert len(result["agents_involved"]) == 4
    
    @pytest.mark.asyncio
    async def test_iteration_improves_confidence(self):
        """Testa se iteração melhora a confiança"""
        # Primeira análise
        initial_request = "Sistema básico de blog"
        
        with patch.object(self.orchestrator, '_coordinate_collaboration') as mock_coord:
            # Primeira resposta com confiança baixa
            mock_coord.return_value = {
                "solution": "Blog simples com WordPress",
                "confidence": 65,
                "agents_involved": ["sofia_oliveira"]
            }
            
            initial_result = await self.orchestrator.process_request(initial_request)
            session_id = initial_result["session_id"]
            
            # Segunda resposta com confiança maior após feedback
            mock_coord.return_value = {
                "solution": "Blog customizado com React e headless CMS",
                "confidence": 85,
                "agents_involved": ["sofia_oliveira", "carlos_eduardo_santos"]
            }
            
            iterated_result = await self.orchestrator.iterate_solution(
                session_id, 
                "Precisa ser mais customizável e escalável"
            )
            
            assert iterated_result["confidence"] > initial_result["confidence"]


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])