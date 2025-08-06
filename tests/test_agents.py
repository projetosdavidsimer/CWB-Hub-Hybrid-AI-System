"""
Testes para os agentes individuais
"""

import pytest
from src.agents.ana_beatriz_costa import AnaBeatrizCosta
from src.agents.carlos_eduardo_santos import CarlosEduardoSantos
from src.agents.sofia_oliveira import SofiaOliveira
from src.agents.isabella_santos import IsabellaSantos


class TestAgents:
    """Testes para agentes individuais"""
    
    @pytest.mark.asyncio
    async def test_ana_beatriz_costa_analysis(self):
        """Testa análise da CTO"""
        agent = AnaBeatrizCosta()
        
        request = "Desenvolver uma plataforma SaaS para gestão de projetos"
        analysis = await agent.analyze_request(request)
        
        assert analysis is not None
        assert "Análise Estratégica" in analysis
        assert "CTO" in analysis
        assert len(analysis) > 100
    
    @pytest.mark.asyncio
    async def test_carlos_eduardo_santos_analysis(self):
        """Testa análise do Arquiteto"""
        agent = CarlosEduardoSantos()
        
        request = "Sistema de e-commerce com alta disponibilidade"
        analysis = await agent.analyze_request(request)
        
        assert analysis is not None
        assert "Análise Arquitetural" in analysis
        assert "Arquiteto" in analysis
        assert "arquitetura" in analysis.lower()
    
    @pytest.mark.asyncio
    async def test_sofia_oliveira_analysis(self):
        """Testa análise da Full Stack"""
        agent = SofiaOliveira()
        
        request = "API REST para aplicativo mobile"
        analysis = await agent.analyze_request(request)
        
        assert analysis is not None
        assert "Implementação" in analysis
        assert "Full Stack" in analysis
    
    @pytest.mark.asyncio
    async def test_isabella_santos_analysis(self):
        """Testa análise da Designer"""
        agent = IsabellaSantos()
        
        request = "Interface para dashboard administrativo"
        analysis = await agent.analyze_request(request)
        
        assert analysis is not None
        assert "UX/UI" in analysis
        assert "Designer" in analysis
    
    @pytest.mark.asyncio
    async def test_agent_collaboration(self):
        """Testa colaboração entre agentes"""
        cto = AnaBeatrizCosta()
        architect = CarlosEduardoSantos()
        
        context = "Arquitetura de microserviços para e-commerce"
        
        # CTO colaborando com Arquiteto
        collaboration = await cto.collaborate_with("carlos_eduardo_santos", context)
        
        assert collaboration is not None
        assert len(collaboration) > 50
        assert "Carlos" in collaboration or "Arquitetura" in collaboration
    
    @pytest.mark.asyncio
    async def test_agent_solution_proposal(self):
        """Testa proposta de solução dos agentes"""
        agent = CarlosEduardoSantos()
        
        problem = "Sistema de pagamentos online seguro"
        constraints = ["PCI compliance", "Alta disponibilidade", "Baixa latência"]
        
        solution = await agent.propose_solution(problem, constraints)
        
        assert solution is not None
        assert "Proposta" in solution
        assert len(solution) > 100
    
    def test_agent_info(self):
        """Testa informações dos agentes"""
        agent = AnaBeatrizCosta()
        info = agent.get_agent_info()
        
        assert "profile" in info
        assert "status" in info
        assert "collaboration" in info
        
        profile = info["profile"]
        assert profile["name"] == "Dra. Ana Beatriz Costa"
        assert profile["role"] == "Chief Technology Officer (CTO)"
        assert len(profile["skills"]) > 0
        assert len(profile["responsibilities"]) > 0
    
    def test_collaboration_preferences(self):
        """Testa preferências de colaboração"""
        agent = IsabellaSantos()
        
        style = agent.get_collaboration_style()
        communication = agent.get_communication_style()
        
        assert style is not None
        assert communication is not None
        assert len(style) > 0
        assert len(communication) > 0