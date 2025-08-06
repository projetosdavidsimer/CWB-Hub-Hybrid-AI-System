"""
Testes para o Orquestrador de IA Híbrida
"""

import pytest
import asyncio
from src.core.hybrid_ai_orchestrator import HybridAIOrchestrator


class TestHybridAIOrchestrator:
    """Testes para o orquestrador principal"""
    
    @pytest.fixture
    async def orchestrator(self):
        """Fixture que cria um orquestrador para testes"""
        orch = HybridAIOrchestrator()
        await orch.initialize_agents()
        yield orch
        await orch.shutdown()
    
    @pytest.mark.asyncio
    async def test_initialization(self):
        """Testa inicialização do orquestrador"""
        orchestrator = HybridAIOrchestrator()
        await orchestrator.initialize_agents()
        
        # Verificar se todos os agentes foram inicializados
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
        
        active_agents = orchestrator.get_active_agents()
        assert len(active_agents) == 8
        
        for agent_id in expected_agents:
            assert agent_id in active_agents
        
        await orchestrator.shutdown()
    
    @pytest.mark.asyncio
    async def test_process_simple_request(self, orchestrator):
        """Testa processamento de uma solicitação simples"""
        request = "Preciso criar uma página web simples com formulário de contato"
        
        response = await orchestrator.process_request(request)
        
        assert response is not None
        assert len(response) > 0
        assert "CWB Hub" in response
    
    @pytest.mark.asyncio
    async def test_session_management(self, orchestrator):
        """Testa gerenciamento de sessões"""
        request = "Desenvolver um sistema de login"
        
        # Processar primeira solicitação
        response1 = await orchestrator.process_request(request)
        
        # Verificar se sessão foi criada
        sessions = list(orchestrator.active_sessions.keys())
        assert len(sessions) >= 1
        
        session_id = sessions[0]
        session_status = orchestrator.get_session_status(session_id)
        
        assert session_status["session_id"] == session_id
        assert session_status["agent_responses_count"] > 0
    
    @pytest.mark.asyncio
    async def test_iteration_functionality(self, orchestrator):
        """Testa funcionalidade de iteração"""
        request = "Criar um app mobile"
        
        # Primeira solicitação
        response1 = await orchestrator.process_request(request)
        
        # Obter ID da sessão
        session_id = list(orchestrator.active_sessions.keys())[0]
        
        # Iterar com feedback
        feedback = "Precisa ser mais simples e focado em iOS"
        response2 = await orchestrator.iterate_solution(session_id, feedback)
        
        assert response2 is not None
        assert response2 != response1  # Resposta deve ser diferente
        
        # Verificar se iteração foi registrada
        session_status = orchestrator.get_session_status(session_id)
        assert session_status["iterations"] > 0


@pytest.mark.asyncio
async def test_orchestrator_error_handling():
    """Testa tratamento de erros do orquestrador"""
    orchestrator = HybridAIOrchestrator()
    
    # Tentar processar sem inicializar agentes
    with pytest.raises(Exception):
        await orchestrator.process_request("test request")


@pytest.mark.asyncio 
async def test_collaboration_stats():
    """Testa estatísticas de colaboração"""
    orchestrator = HybridAIOrchestrator()
    await orchestrator.initialize_agents()
    
    # Processar uma solicitação para gerar colaborações
    await orchestrator.process_request("Desenvolver uma API REST")
    
    # Verificar estatísticas
    stats = orchestrator.collaboration_framework.get_collaboration_stats()
    assert "total_collaborations" in stats
    
    await orchestrator.shutdown()