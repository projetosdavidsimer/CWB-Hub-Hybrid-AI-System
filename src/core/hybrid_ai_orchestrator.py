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
from ..utils.advanced_cache import cache_manager, cache_project_data, get_cached_project_data, cache_agent_analysis, get_cached_agent_analysis
from ..learning.continuous_learning_engine import learning_engine, InteractionType
from ..learning.feedback_collector import feedback_collector


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
        self.cache_manager = cache_manager
        self.learning_engine = learning_engine
        self.feedback_collector = feedback_collector
        self.logger = logging.getLogger(__name__)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    async def initialize_agents(self):
        """Inicializa todos os agentes da equipe CWB Hub"""
        try:
            from ..agents.ana_beatriz_costa import AnaBeatrizCosta
            from ..agents.carlos_eduardo_santos import CarlosEduardoSantos
            from ..agents.gabriel_mendes import GabrielMendes
            from ..agents.isabella_santos import IsabellaSantos
            from ..agents.lucas_pereira import LucasPereira
            from ..agents.mariana_rodrigues import MarianaRodrigues
            from ..agents.pedro_henrique_almeida import PedroHenriqueAlmeida
            from ..agents.sofia_oliveira import SofiaOliveira
        except ImportError:
            # Fallback para importação absoluta
            from agents.ana_beatriz_costa import AnaBeatrizCosta
            from agents.carlos_eduardo_santos import CarlosEduardoSantos
            from agents.gabriel_mendes import GabrielMendes
            from agents.isabella_santos import IsabellaSantos
            from agents.lucas_pereira import LucasPereira
            from agents.mariana_rodrigues import MarianaRodrigues
            from agents.pedro_henrique_almeida import PedroHenriqueAlmeida
            from agents.sofia_oliveira import SofiaOliveira
        
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
        
        self.logger.info("✅ Todos os agentes da CWB Hub foram inicializados com sucesso")
        self.logger.info(f"📊 Cache avançado ativo: {self.cache_manager.redis_available}")
        self.logger.info("🧠 Sistema de aprendizado contínuo ativo")
        
        # Log das estatísticas do cache
        cache_stats = self.cache_manager.get_stats()
        self.logger.info(f"💾 Cache stats: {cache_stats.hits} hits, {cache_stats.misses} misses, {cache_stats.hit_rate:.1%} hit rate")
    
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
        
        # Iniciar rastreamento de aprendizado
        await self.feedback_collector.start_session_tracking(
            session_id, 
            "user_default",  # TODO: Integrar com sistema de usuários
            {"request_type": "project_analysis", "timestamp": datetime.now().isoformat()}
        )
        
        # Verificar cache de projeto primeiro
        import hashlib
        request_hash = hashlib.md5(user_request.encode()).hexdigest()
        cached_response = await get_cached_project_data(request_hash)
        
        if cached_response and cached_response.get('final_solution'):
            self.logger.info(f"🎯 Cache hit para projeto: {request_hash[:8]}")
            
            # Rastrear interação de cache hit
            await self.feedback_collector.track_interaction(
                session_id,
                f"cached_{request_hash[:8]}",
                InteractionType.PROJECT_ANALYSIS,
                user_request,
                cached_response['final_solution'],
                cached_response.get('agents_involved', []),
                0.1,  # Tempo muito rápido para cache
                0.9   # Alta confiança para cache
            )
            
            return cached_response['final_solution']
        
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
            
            # Calcular métricas da sessão
            processing_time = (datetime.now() - session.created_at).total_seconds()
            agents_involved = list(set([r.agent_id for r in session.agent_responses]))
            
            # Rastrear interação principal para aprendizado
            interaction_id = f"main_{session_id}"
            await self.feedback_collector.track_interaction(
                session_id,
                interaction_id,
                InteractionType.PROJECT_ANALYSIS,
                user_request,
                final_response,
                agents_involved,
                processing_time,
                0.85  # Confiança padrão - pode ser calculada dinamicamente
            )
            
            # Cache do resultado do projeto
            project_data = {
                'session_id': session_id,
                'user_request': user_request,
                'final_solution': final_response,
                'agent_responses_count': len(session.agent_responses),
                'agents_involved': agents_involved,
                'created_at': session.created_at.isoformat(),
                'processing_time': processing_time
            }
            
            import hashlib
            request_hash = hashlib.md5(user_request.encode()).hexdigest()
            await cache_project_data(request_hash, project_data)
            
            self.logger.info(f"Sessão {session_id} processada com sucesso e cacheada")
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
                agent_name=self.agents[agent_id].profile.name,
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
        
        # Rastrear iteração para aprendizado
        if session_id in self.active_sessions:
            main_interaction_id = f"main_{session_id}"
            await self.feedback_collector.track_iteration(session_id, main_interaction_id)
        
        # Reprocessar com o feedback
        return await self.process_request(refined_request, session_id)
    
    async def _get_agent_analysis(self, agent_id: str, request: str) -> str:
        """Obtém análise de um agente específico com cache"""
        # Verificar cache de análise do agente
        import hashlib
        analysis_key = f"{agent_id}_{hashlib.md5(request.encode()).hexdigest()}"
        
        cached_analysis = await get_cached_agent_analysis(agent_id, analysis_key)
        if cached_analysis:
            self.logger.debug(f"🎯 Cache hit para análise do agente {agent_id}")
            return cached_analysis.get('content', '')
        
        # Gerar nova análise
        agent = self.agents[agent_id]
        analysis = await agent.analyze_request(request)
        
        # Cache da análise
        analysis_data = {
            'agent_id': agent_id,
            'content': analysis,
            'timestamp': datetime.now().isoformat(),
            'request_hash': hashlib.md5(request.encode()).hexdigest()
        }
        
        await cache_agent_analysis(agent_id, analysis_key, analysis_data)
        
        return analysis
    
    def get_session_status(self, session_id: str = None) -> Dict[str, Any]:
        """Retorna o status de uma sessão ou estatísticas gerais"""
        if session_id and session_id not in self.active_sessions:
            return {"error": "Sessão não encontrada"}
        
        if session_id:
            session = self.active_sessions[session_id]
            return {
                "session_id": session.session_id,
                "current_phase": session.current_phase.value,
                "iterations": session.iterations,
                "agent_responses_count": len(session.agent_responses),
                "agents_involved": list(set([r.agent_id for r in session.agent_responses])),
                "created_at": session.created_at.isoformat(),
                "has_final_solution": session.final_solution is not None
            }
        else:
            # Retornar estatísticas gerais
            return {
                "total_active_sessions": len(self.active_sessions),
                "total_agents": len(self.agents),
                "cache_stats": self.cache_manager.get_stats(),
                "agents_available": list(self.agents.keys()),
                "learning_enabled": True,
                "feedback_collection_active": True
            }
    
    def get_active_agents(self) -> List[str]:
        """Retorna lista de agentes ativos"""
        return list(self.agents.keys())
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        return {
            "cache_stats": self.cache_manager.get_stats(),
            "cache_health": await self.cache_manager.health_check()
        }
    
    async def clear_cache(self, cache_type: str = None) -> Dict[str, Any]:
        """Limpa cache específico ou todos"""
        if cache_type:
            cleared = await self.cache_manager.clear_cache_type(cache_type)
            return {"cleared_items": cleared, "cache_type": cache_type}
        else:
            # Limpar todos os tipos de cache relacionados ao orquestrador
            results = {}
            for cache_type in ["project_data", "agent_analysis", "user_sessions"]:
                cleared = await self.cache_manager.clear_cache_type(cache_type)
                results[cache_type] = cleared
            return results
    
    async def collect_user_feedback(self, 
                                   session_id: str, 
                                   rating: float, 
                                   comments: Optional[str] = None) -> None:
        """Coleta feedback explícito do usuário"""
        if session_id in self.active_sessions:
            main_interaction_id = f"main_{session_id}"
            await self.feedback_collector.collect_explicit_feedback(
                session_id, 
                main_interaction_id, 
                rating, 
                comments
            )
            self.logger.info(f"📝 Feedback coletado para sessão {session_id}: {rating}/5.0")
    
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """Finaliza uma sessão e gera análise de aprendizado"""
        session_analysis = await self.feedback_collector.end_session_tracking(session_id)
        
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        return session_analysis
    
    async def get_learning_insights(self) -> Dict[str, Any]:
        """Retorna insights do sistema de aprendizado"""
        learning_insights = await self.learning_engine.get_learning_insights()
        feedback_analytics = await self.feedback_collector.get_feedback_analytics()
        
        return {
            "learning_insights": learning_insights,
            "feedback_analytics": feedback_analytics,
            "system_performance": {
                "active_sessions": len(self.active_sessions),
                "total_agents": len(self.agents),
                "cache_performance": self.cache_manager.get_stats()
            }
        }
    
    async def shutdown(self):
        """Encerra o orquestrador e limpa recursos"""
        # Finalizar todas as sessões ativas
        for session_id in list(self.active_sessions.keys()):
            await self.end_session(session_id)
        
        await self.collaboration_framework.shutdown()
        self.active_sessions.clear()
        self.logger.info("Orquestrador CWB Hub encerrado")