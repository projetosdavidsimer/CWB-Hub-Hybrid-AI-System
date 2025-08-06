"""
CWB Hub Hybrid AI Orchestrator
Sistema principal que gerencia a consciência coletiva dos 8 profissionais sênior
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

from ..agents.base_agent import BaseAgent
from ..communication.collaboration_framework import CollaborationFramework
from ..utils.requirement_analyzer import RequirementAnalyzer
from ..utils.response_synthesizer import ResponseSynthesizer


class ProcessPhase(Enum):
    ANALYSIS = "analysis"
    COLLABORATION = "collaboration"
    SOLUTION_PROPOSAL = "solution_proposal"
    COMMUNICATION = "communication"
    ITERATION = "iteration"


@dataclass
class AgentResponse:
    agent_id: str
    agent_name: str
    phase: ProcessPhase
    content: str
    confidence: float
    dependencies: List[str]
    timestamp: datetime


@dataclass
class CollaborationSession:
    session_id: str
    user_request: str
    current_phase: ProcessPhase
    agent_responses: List[AgentResponse]
    iterations: int
    final_solution: Optional[str]
    created_at: datetime


class HybridAIOrchestrator:
    """
    Orquestrador principal da IA Híbrida CWB Hub
    
    Gerencia a consciência coletiva dos 8 profissionais sênior:
    - Ana Beatriz Costa (CTO)
    - Carlos Eduardo Santos (Arquiteto de Software)
    - Gabriel Mendes (Engenheiro Mobile)
    - Isabella Santos (Designer UX/UI)
    - Lucas Pereira (QA Automation)
    - Mariana Rodrigues (DevOps/Dados)
    - Pedro Henrique Almeida (Agile PM)
    - Sofia Oliveira (Full Stack)
    """
    
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.collaboration_framework = CollaborationFramework()
        self.requirement_analyzer = RequirementAnalyzer()
        self.response_synthesizer = ResponseSynthesizer()
        self.active_sessions: Dict[str, CollaborationSession] = {}
        self.logger = logging.getLogger(__name__)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    async def initialize_agents(self):
        """Inicializa todos os agentes da equipe CWB Hub"""
        from ..agents.ana_beatriz_costa import AnaBeatrizCosta
        from ..agents.carlos_eduardo_santos import CarlosEduardoSantos
        from ..agents.gabriel_mendes import GabrielMendes
        from ..agents.isabella_santos import IsabellaSantos
        from ..agents.lucas_pereira import LucasPereira
        from ..agents.mariana_rodrigues import MarianaRodrigues
        from ..agents.pedro_henrique_almeida import PedroHenriqueAlmeida
        from ..agents.sofia_oliveira import SofiaOliveira
        
        # Instanciar todos os agentes
        self.agents = {
            "ana_beatriz_costa": AnaBeatrizCosta(),
            "carlos_eduardo_santos": CarlosEduardoSantos(),
            "gabriel_mendes": GabrielMendes(),
            "isabella_santos": IsabellaSantos(),
            "lucas_pereira": LucasPereira(),
            "mariana_rodrigues": MarianaRodrigues(),
            "pedro_henrique_almeida": PedroHenriqueAlmeida(),
            "sofia_oliveira": SofiaOliveira()
        }
        
        # Configurar framework de colaboração
        await self.collaboration_framework.initialize(self.agents)
        
        self.logger.info("Todos os agentes da CWB Hub foram inicializados com sucesso")
    
    async def process_request(self, user_request: str, session_id: Optional[str] = None) -> str:
        """
        Processa uma solicitação do usuário seguindo o processo de 5 etapas:
        1. Analisar o Requisito
        2. Colaborar e Interagir
        3. Propor Soluções Integradas
        4. Comunicação Clara
        5. Iteração
        """
        if not session_id:
            session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Criar nova sessão de colaboração
        session = CollaborationSession(
            session_id=session_id,
            user_request=user_request,
            current_phase=ProcessPhase.ANALYSIS,
            agent_responses=[],
            iterations=0,
            final_solution=None,
            created_at=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        
        try:
            # Fase 1: Analisar o Requisito
            await self._phase_1_analyze_requirement(session)
            
            # Fase 2: Colaborar e Interagir
            await self._phase_2_collaborate_and_interact(session)
            
            # Fase 3: Propor Soluções Integradas
            await self._phase_3_propose_integrated_solutions(session)
            
            # Fase 4: Comunicação Clara
            final_response = await self._phase_4_clear_communication(session)
            
            # Fase 5: Preparar para Iteração (se necessário)
            session.final_solution = final_response
            
            self.logger.info(f"Sessão {session_id} processada com sucesso")
            return final_response
            
        except Exception as e:
            self.logger.error(f"Erro ao processar sessão {session_id}: {str(e)}")
            raise
    
    async def _phase_1_analyze_requirement(self, session: CollaborationSession):
        """Fase 1: Cada agente analisa o requisito sob sua perspectiva"""
        session.current_phase = ProcessPhase.ANALYSIS
        
        # Analisar requisito e determinar agentes relevantes
        relevant_agents = await self.requirement_analyzer.analyze(
            session.user_request, 
            list(self.agents.keys())
        )
        
        # Cada agente relevante analisa o requisito
        analysis_tasks = []
        for agent_id in relevant_agents:
            if agent_id in self.agents:
                task = self._get_agent_analysis(agent_id, session.user_request)
                analysis_tasks.append(task)
        
        # Executar análises em paralelo
        analyses = await asyncio.gather(*analysis_tasks)
        
        # Armazenar respostas
        for agent_id, analysis in zip(relevant_agents, analyses):
            response = AgentResponse(
                agent_id=agent_id,
                agent_name=self.agents[agent_id].name,
                phase=ProcessPhase.ANALYSIS,
                content=analysis,
                confidence=0.8,  # Será calculado dinamicamente no futuro
                dependencies=[],
                timestamp=datetime.now()
            )
            session.agent_responses.append(response)
        
        self.logger.info(f"Fase 1 concluída: {len(analyses)} análises realizadas")
    
    async def _phase_2_collaborate_and_interact(self, session: CollaborationSession):
        """Fase 2: Agentes colaboram e interagem entre si"""
        session.current_phase = ProcessPhase.COLLABORATION
        
        # Facilitar colaboração entre agentes
        collaboration_results = await self.collaboration_framework.facilitate_collaboration(
            session.agent_responses,
            session.user_request
        )
        
        # Adicionar resultados da colaboração
        for result in collaboration_results:
            session.agent_responses.append(result)
        
        self.logger.info(f"Fase 2 concluída: {len(collaboration_results)} interações de colaboração")
    
    async def _phase_3_propose_integrated_solutions(self, session: CollaborationSession):
        """Fase 3: Propor soluções integradas"""
        session.current_phase = ProcessPhase.SOLUTION_PROPOSAL
        
        # Sintetizar soluções integradas
        integrated_solutions = await self.response_synthesizer.synthesize_solutions(
            session.agent_responses,
            session.user_request
        )
        
        # Adicionar soluções propostas
        for solution in integrated_solutions:
            session.agent_responses.append(solution)
        
        self.logger.info(f"Fase 3 concluída: {len(integrated_solutions)} soluções integradas propostas")
    
    async def _phase_4_clear_communication(self, session: CollaborationSession) -> str:
        """Fase 4: Comunicação clara e estruturada"""
        session.current_phase = ProcessPhase.COMMUNICATION
        
        # Sintetizar resposta final
        final_response = await self.response_synthesizer.create_final_response(
            session.agent_responses,
            session.user_request
        )
        
        self.logger.info("Fase 4 concluída: Resposta final sintetizada")
        return final_response
    
    async def iterate_solution(self, session_id: str, feedback: str) -> str:
        """Fase 5: Iteração baseada em feedback"""
        if session_id not in self.active_sessions:
            raise ValueError(f"Sessão {session_id} não encontrada")
        
        session = self.active_sessions[session_id]
        session.current_phase = ProcessPhase.ITERATION
        session.iterations += 1
        
        # Processar feedback e iterar
        refined_request = f"{session.user_request}\n\nFeedback para iteração: {feedback}"
        
        # Reprocessar com o feedback
        return await self.process_request(refined_request, session_id)
    
    async def _get_agent_analysis(self, agent_id: str, request: str) -> str:
        """Obtém análise de um agente específico"""
        agent = self.agents[agent_id]
        return await agent.analyze_request(request)
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Retorna o status de uma sessão"""
        if session_id not in self.active_sessions:
            return {"error": "Sessão não encontrada"}
        
        session = self.active_sessions[session_id]
        return {
            "session_id": session.session_id,
            "current_phase": session.current_phase.value,
            "iterations": session.iterations,
            "agent_responses_count": len(session.agent_responses),
            "created_at": session.created_at.isoformat(),
            "has_final_solution": session.final_solution is not None
        }
    
    def get_active_agents(self) -> List[str]:
        """Retorna lista de agentes ativos"""
        return list(self.agents.keys())
    
    async def shutdown(self):
        """Encerra o orquestrador e limpa recursos"""
        await self.collaboration_framework.shutdown()
        self.active_sessions.clear()
        self.logger.info("Orquestrador CWB Hub encerrado")