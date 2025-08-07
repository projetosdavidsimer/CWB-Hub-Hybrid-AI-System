#!/usr/bin/env python3
"""
Testes unitários para todos os agentes CWB Hub
Melhoria #5 - Testes Automatizados Completos
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os

# Adicionar o diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.base_agent import BaseAgent, AgentProfile
from agents.ana_beatriz_costa import AnaBeatrizCosta
from agents.carlos_eduardo_santos import CarlosEduardoSantos
from agents.sofia_oliveira import SofiaOliveira
from agents.gabriel_mendes import GabrielMendes
from agents.isabella_santos import IsabellaSantos
from agents.lucas_pereira import LucasPereira
from agents.mariana_rodrigues import MarianaRodrigues
from agents.pedro_henrique_almeida import PedroHenriqueAlmeida


class TestBaseAgent:
    """Testes para a classe base BaseAgent"""
    
    def test_agent_profile_creation(self):
        """Testa criação de perfil de agente"""
        profile = AgentProfile(
            agent_id="test_agent",
            name="Test Agent",
            role="Test Role",
            description="Test Description",
            skills=["Test Skill"],
            responsibilities=["Test Responsibility"],
            personality_traits=["Test Trait"],
            expertise_areas=["Test Area"]
        )
        
        assert profile.agent_id == "test_agent"
        assert profile.name == "Test Agent"
        assert profile.role == "Test Role"
        assert len(profile.skills) == 1
        assert len(profile.responsibilities) == 1
        assert len(profile.personality_traits) == 1
        assert len(profile.expertise_areas) == 1
    
    def test_agent_context_initialization(self):
        """Testa inicialização do contexto do agente"""
        profile = AgentProfile(
            agent_id="test_agent",
            name="Test Agent",
            role="Test Role",
            description="Test Description",
            skills=[],
            responsibilities=[],
            personality_traits=[],
            expertise_areas=[]
        )
        
        # Criar uma implementação concreta para teste
        class TestAgent(BaseAgent):
            async def analyze_request(self, request: str) -> str:
                return "Test analysis"
            
            async def collaborate_with(self, other_agent_id: str, context: str) -> str:
                return "Test collaboration"
            
            async def propose_solution(self, problem: str, constraints: list) -> str:
                return "Test solution"
            
            def _define_collaboration_preferences(self) -> dict:
                return {"style": "test"}
            
            async def _generate_expertise_response(self, topic: str) -> str:
                return "Test expertise"
            
            async def _generate_review_response(self, solution: str, criteria: list) -> str:
                return "Test review"
        
        agent = TestAgent(profile)
        
        assert agent.profile.agent_id == "test_agent"
        assert agent.context.current_project is None
        assert len(agent.context.previous_interactions) == 0
        assert len(agent.context.collaboration_history) == 0
        assert agent.is_active is True


class TestAnaBeatrizCosta:
    """Testes para Ana Beatriz Costa - CTO"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.agent = AnaBeatrizCosta()
    
    def test_agent_initialization(self):
        """Testa inicialização do agente"""
        assert self.agent.profile.agent_id == "ana_beatriz_costa"
        assert self.agent.profile.name == "Dra. Ana Beatriz Costa"
        assert self.agent.profile.role == "Chief Technology Officer (CTO)"
        assert "Liderança estratégica" in self.agent.profile.skills
        assert "Estratégia tecnológica" in self.agent.profile.expertise_areas
    
    @pytest.mark.asyncio
    async def test_analyze_request(self):
        """Testa análise de requisito"""
        request = "Preciso de uma estratégia tecnológica para escalar minha startup"
        result = await self.agent.analyze_request(request)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "estratégia" in result.lower() or "tecnológica" in result.lower()
    
    @pytest.mark.asyncio
    async def test_collaborate_with(self):
        """Testa colaboração com outro agente"""
        result = await self.agent.collaborate_with("carlos_eduardo_santos", "Arquitetura de sistema")
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_propose_solution(self):
        """Testa proposta de solução"""
        problem = "Como implementar uma arquitetura escalável?"
        constraints = ["Orçamento limitado", "Prazo de 3 meses"]
        result = await self.agent.propose_solution(problem, constraints)
        
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_collaboration_preferences(self):
        """Testa preferências de colaboração"""
        prefs = self.agent.collaboration_preferences
        assert isinstance(prefs, dict)
        assert "style" in prefs
        assert "communication" in prefs


class TestCarlosEduardoSantos:
    """Testes para Carlos Eduardo Santos - Arquiteto de Software"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.agent = CarlosEduardoSantos()
    
    def test_agent_initialization(self):
        """Testa inicialização do agente"""
        assert self.agent.profile.agent_id == "carlos_eduardo_santos"
        assert self.agent.profile.name == "Dr. Carlos Eduardo Santos"
        assert self.agent.profile.role == "Arquiteto de Software Sênior"
        assert "Arquitetura de Sistemas" in self.agent.profile.skills
        assert "Arquitetura de software" in self.agent.profile.expertise_areas
    
    @pytest.mark.asyncio
    async def test_analyze_request_architecture(self):
        """Testa análise de requisito de arquitetura"""
        request = "Preciso de uma arquitetura de microsserviços para e-commerce"
        result = await self.agent.analyze_request(request)
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert "microsserviços" in result.lower() or "arquitetura" in result.lower()


class TestSofiaOliveira:
    """Testes para Sofia Oliveira - Engenheira Full Stack"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.agent = SofiaOliveira()
    
    def test_agent_initialization(self):
        """Testa inicialização do agente"""
        assert self.agent.profile.agent_id == "sofia_oliveira"
        assert self.agent.profile.name == "Sofia Oliveira"
        assert self.agent.profile.role == "Engenheira Full Stack"
        assert "React/Vue.js" in self.agent.profile.skills
        assert "Desenvolvimento web" in self.agent.profile.expertise_areas
    
    @pytest.mark.asyncio
    async def test_analyze_request_fullstack(self):
        """Testa análise de requisito full stack"""
        request = "Preciso desenvolver uma aplicação web com React e Node.js"
        result = await self.agent.analyze_request(request)
        
        assert isinstance(result, str)
        assert len(result) > 0


class TestGabrielMendes:
    """Testes para Gabriel Mendes - Engenheiro Mobile"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.agent = GabrielMendes()
    
    def test_agent_initialization(self):
        """Testa inicialização do agente"""
        assert self.agent.profile.agent_id == "gabriel_mendes"
        assert self.agent.profile.name == "Gabriel Mendes"
        assert self.agent.profile.role == "Engenheiro Mobile"
        assert "iOS (Swift)" in self.agent.profile.skills
        assert "Desenvolvimento mobile" in self.agent.profile.expertise_areas


class TestIsabellaSantos:
    """Testes para Isabella Santos - Designer UX/UI"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.agent = IsabellaSantos()
    
    def test_agent_initialization(self):
        """Testa inicialização do agente"""
        assert self.agent.profile.agent_id == "isabella_santos"
        assert self.agent.profile.name == "Isabella Santos"
        assert self.agent.profile.role == "Designer UX/UI Sênior"
        assert "Pesquisa de Usuário" in self.agent.profile.skills
        assert "User Experience" in self.agent.profile.expertise_areas


class TestLucasPereira:
    """Testes para Lucas Pereira - Engenheiro de QA"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.agent = LucasPereira()
    
    def test_agent_initialization(self):
        """Testa inicialização do agente"""
        assert self.agent.profile.agent_id == "lucas_pereira"
        assert self.agent.profile.name == "Lucas Pereira"
        assert self.agent.profile.role == "Engenheiro de QA"
        assert "Testes Automatizados" in self.agent.profile.skills
        assert "Qualidade de software" in self.agent.profile.expertise_areas


class TestMarianaRodrigues:
    """Testes para Mariana Rodrigues - Engenheira DevOps"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.agent = MarianaRodrigues()
    
    def test_agent_initialization(self):
        """Testa inicialização do agente"""
        assert self.agent.profile.agent_id == "mariana_rodrigues"
        assert self.agent.profile.name == "Mariana Rodrigues"
        assert self.agent.profile.role == "Engenheira DevOps"
        assert "Docker" in self.agent.profile.skills
        assert "DevOps" in self.agent.profile.expertise_areas


class TestPedroHenriqueAlmeida:
    """Testes para Pedro Henrique Almeida - Agile Project Manager"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.agent = PedroHenriqueAlmeida()
    
    def test_agent_initialization(self):
        """Testa inicialização do agente"""
        assert self.agent.profile.agent_id == "pedro_henrique_almeida"
        assert self.agent.profile.name == "Pedro Henrique Almeida"
        assert self.agent.profile.role == "Agile Project Manager"
        assert "Scrum" in self.agent.profile.skills
        assert "Metodologias ágeis" in self.agent.profile.expertise_areas


class TestAllAgentsIntegration:
    """Testes de integração para todos os agentes"""
    
    def setup_method(self):
        """Setup para cada teste"""
        self.agents = [
            AnaBeatrizCosta(),
            CarlosEduardoSantos(),
            SofiaOliveira(),
            GabrielMendes(),
            IsabellaSantos(),
            LucasPereira(),
            MarianaRodrigues(),
            PedroHenriqueAlmeida()
        ]
    
    def test_all_agents_unique_ids(self):
        """Testa se todos os agentes têm IDs únicos"""
        agent_ids = [agent.profile.agent_id for agent in self.agents]
        assert len(agent_ids) == len(set(agent_ids)), "IDs de agentes devem ser únicos"
    
    def test_all_agents_have_required_attributes(self):
        """Testa se todos os agentes têm atributos obrigatórios"""
        for agent in self.agents:
            assert hasattr(agent.profile, 'agent_id')
            assert hasattr(agent.profile, 'name')
            assert hasattr(agent.profile, 'role')
            assert hasattr(agent.profile, 'skills')
            assert hasattr(agent.profile, 'expertise_areas')
            assert len(agent.profile.skills) > 0
            assert len(agent.profile.expertise_areas) > 0
    
    @pytest.mark.asyncio
    async def test_all_agents_can_analyze(self):
        """Testa se todos os agentes podem analisar requisitos"""
        test_request = "Preciso desenvolver um sistema completo"
        
        for agent in self.agents:
            result = await agent.analyze_request(test_request)
            assert isinstance(result, str)
            assert len(result) > 0
    
    def test_all_agents_collaboration_preferences(self):
        """Testa se todos os agentes têm preferências de colaboração"""
        for agent in self.agents:
            prefs = agent.collaboration_preferences
            assert isinstance(prefs, dict)
            assert len(prefs) > 0


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])