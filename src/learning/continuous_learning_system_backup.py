"""
Sistema de Aprendizado Contínuo CWB Hub
Melhoria #7 - IA que aprende e evolui

Sistema que permite aos 8 agentes CWB Hub evoluírem através de:
- Feedback dos usuários
- Análise de padrões de sucesso
- Aprendizado por reforço
- Adaptação personalizada
- Evolução contínua das capacidades

Criado por: David Simer
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
from collections import defaultdict, deque
import pickle
import os

# Importações do sistema CWB Hub
try:
    from ..agents.base_agent import BaseAgent
    from ..core.hybrid_ai_orchestrator import CollaborationSession, AgentResponse
    from ..database.models import Session, Agent, LearningEvent, FeedbackData
    from ..database.connection import get_db_connection
except ImportError:
    # Fallback para desenvolvimento
    pass


class LearningEventType(Enum):
    """Tipos de eventos de aprendizado"""
    USER_FEEDBACK = "user_feedback"
    SUCCESS_PATTERN = "success_pattern"
    FAILURE_ANALYSIS = "failure_analysis"
    COLLABORATION_IMPROVEMENT = "collaboration_improvement"
    PERFORMANCE_OPTIMIZATION = "performance_optimization"
    KNOWLEDGE_UPDATE = "knowledge_update"
    ADAPTATION_TRIGGER = "adaptation_trigger"


class FeedbackType(Enum):
    """Tipos de feedback do usuário"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    SUGGESTION = "suggestion"
    CORRECTION = "correction"


class LearningStrategy(Enum):
    """Estratégias de aprendizado"""
    REINFORCEMENT = "reinforcement"
    PATTERN_RECOGNITION = "pattern_recognition"
    COLLABORATIVE_FILTERING = "collaborative_filtering"
    KNOWLEDGE_DISTILLATION = "knowledge_distillation"
    ADAPTIVE_PERSONALIZATION = "adaptive_personalization"


@dataclass
class LearningEvent:
    """Evento de aprendizado"""
    event_id: str
    event_type: LearningEventType
    agent_id: str
    session_id: str
    timestamp: datetime
    data: Dict[str, Any]
    impact_score: float = 0.0
    processed: bool = False


@dataclass
class FeedbackEvent:
    """Evento de feedback do usuário"""
    feedback_id: str
    session_id: str
    user_id: Optional[str]
    feedback_type: FeedbackType
    rating: Optional[int]  # 1-5 escala
    comment: Optional[str]
    specific_agent: Optional[str]
    timestamp: datetime
    processed: bool = False


@dataclass
class LearningMetrics:
    """Métricas de aprendizado"""
    agent_id: str
    performance_score: float
    improvement_rate: float
    feedback_score: float
    collaboration_effectiveness: float
    knowledge_growth: float
    adaptation_speed: float
    last_updated: datetime


@dataclass
class KnowledgePattern:
    """Padrão de conhecimento identificado"""
    pattern_id: str
    pattern_type: str
    context: str
    success_rate: float
    usage_count: int
    agents_involved: List[str]
    created_at: datetime
    last_used: datetime


class ContinuousLearningSystem:
    """
    Sistema de Aprendizado Contínuo CWB Hub
    
    Funcionalidades principais:
    1. Coleta e análise de feedback
    2. Identificação de padrões de sucesso
    3. Aprendizado por reforço
    4. Adaptação personalizada
    5. Evolução contínua dos agentes
    """
    
    def __init__(self, data_dir: str = "data/learning"):
        self.data_dir = data_dir
        self.logger = logging.getLogger(__name__)
        
        # Estruturas de dados em memória
        self.learning_events: deque = deque(maxlen=10000)
        self.feedback_events: deque = deque(maxlen=5000)
        self.agent_metrics: Dict[str, LearningMetrics] = {}
        self.knowledge_patterns: Dict[str, KnowledgePattern] = {}
        
        # Configurações de aprendizado
        self.learning_config = {
            "feedback_weight": 0.3,
            "success_pattern_weight": 0.4,
            "collaboration_weight": 0.2,
            "performance_weight": 0.1,
            "min_events_for_learning": 5,
            "pattern_confidence_threshold": 0.7,
            "adaptation_threshold": 0.6,
            "learning_rate": 0.01
        }
        
        # Cache de aprendizado
        self.learning_cache: Dict[str, Any] = {}
        self.pattern_cache: Dict[str, List[KnowledgePattern]] = {}
        
        # Estado do sistema
        self.is_learning_active = True
        self.last_learning_cycle = None
        
        # Criar diretório de dados
        os.makedirs(data_dir, exist_ok=True)
        
        self.logger.info("🧠 Sistema de Aprendizado Contínuo CWB Hub inicializado")
    
    async def initialize(self, agents: Dict[str, BaseAgent]):
        """
        Inicializa o sistema de aprendizado com os agentes
        
        Args:
            agents: Dicionário de agentes CWB Hub
        """
        self.agents = agents
        
        # Inicializar métricas para cada agente
        for agent_id, agent in agents.items():
            if agent_id not in self.agent_metrics:
                self.agent_metrics[agent_id] = LearningMetrics(
                    agent_id=agent_id,
                    performance_score=0.5,  # Baseline
                    improvement_rate=0.0,
                    feedback_score=0.5,
                    collaboration_effectiveness=0.5,
                    knowledge_growth=0.0,
                    adaptation_speed=0.5,
                    last_updated=datetime.now()
                )
        
        # Carregar dados persistidos
        await self._load_learning_data()
        
        # Iniciar ciclo de aprendizado
        asyncio.create_task(self._learning_cycle())
        
        self.logger.info(f"🧠 Sistema inicializado para {len(agents)} agentes")
    
    async def record_feedback(
        self,
        session_id: str,
        feedback_type: FeedbackType,
        rating: Optional[int] = None,
        comment: Optional[str] = None,
        specific_agent: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """
        Registra feedback do usuário
        
        Args:
            session_id: ID da sessão
            feedback_type: Tipo de feedback
            rating: Avaliação (1-5)
            comment: Comentário do usuário
            specific_agent: Agente específico (opcional)
            user_id: ID do usuário (opcional)
            
        Returns:
            ID do evento de feedback
        """
        feedback_id = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        feedback_event = FeedbackEvent(
            feedback_id=feedback_id,
            session_id=session_id,
            user_id=user_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment,
            specific_agent=specific_agent,
            timestamp=datetime.now(),
            processed=False
        )
        
        self.feedback_events.append(feedback_event)
        
        # Processar feedback imediatamente se crítico
        if feedback_type in [FeedbackType.NEGATIVE, FeedbackType.CORRECTION]:
            await self._process_critical_feedback(feedback_event)
        
        self.logger.info(f"📝 Feedback registrado: {feedback_id} ({feedback_type.value})")
        return feedback_id
    
    async def record_learning_event(
        self,
        event_type: LearningEventType,
        agent_id: str,
        session_id: str,
        data: Dict[str, Any],
        impact_score: float = 0.0
    ) -> str:
        """
        Registra evento de aprendizado
        
        Args:
            event_type: Tipo do evento
            agent_id: ID do agente
            session_id: ID da sessão
            data: Dados do evento
            impact_score: Pontuação de impacto
            
        Returns:
            ID do evento
        """
        event_id = f"event_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        learning_event = LearningEvent(
            event_id=event_id,
            event_type=event_type,
            agent_id=agent_id,
            session_id=session_id,
            timestamp=datetime.now(),
            data=data,
            impact_score=impact_score,
            processed=False
        )
        
        self.learning_events.append(learning_event)
        
        self.logger.debug(f"🎯 Evento de aprendizado: {event_id} ({event_type.value})")
        return event_id
    
    async def analyze_session_performance(
        self,
        session: CollaborationSession,
        user_satisfaction: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Analisa performance de uma sessão para aprendizado
        
        Args:
            session: Sessão de colaboração
            user_satisfaction: Satisfação do usuário (0-1)
            
        Returns:
            Análise de performance
        """
        analysis = {
            "session_id": session.session_id,
            "performance_metrics": {},
            "learning_opportunities": [],
            "success_patterns": [],
            "improvement_areas": []
        }
        
        # Analisar performance por agente
        agent_performances = {}
        for response in session.agent_responses:
            agent_id = response.agent_id
            
            if agent_id not in agent_performances:
                agent_performances[agent_id] = {
                    "response_count": 0,
                    "avg_confidence": 0.0,
                    "collaboration_score": 0.0,
                    "response_quality": 0.0
                }
            
            perf = agent_performances[agent_id]
            perf["response_count"] += 1
            perf["avg_confidence"] += response.confidence
        
        # Calcular métricas finais
        for agent_id, perf in agent_performances.items():
            if perf["response_count"] > 0:
                perf["avg_confidence"] /= perf["response_count"]
                
                # Calcular score de colaboração baseado em dependências
                collaboration_responses = [
                    r for r in session.agent_responses 
                    if r.agent_id == agent_id and r.dependencies
                ]
                perf["collaboration_score"] = len(collaboration_responses) / perf["response_count"]
                
                # Score de qualidade baseado em satisfação do usuário
                if user_satisfaction is not None:
                    perf["response_quality"] = user_satisfaction * perf["avg_confidence"]
                else:
                    perf["response_quality"] = perf["avg_confidence"]
        
        analysis["performance_metrics"] = agent_performances
        
        # Identificar padrões de sucesso
        if user_satisfaction and user_satisfaction > 0.7:
            success_pattern = await self._identify_success_pattern(session, agent_performances)
            if success_pattern:
                analysis["success_patterns"].append(success_pattern)
        
        # Identificar oportunidades de melhoria
        for agent_id, perf in agent_performances.items():
            if perf["response_quality"] < 0.6:
                analysis["improvement_areas"].append({
                    "agent_id": agent_id,
                    "area": "response_quality",
                    "current_score": perf["response_quality"],
                    "target_score": 0.8
                })
        
        # Registrar eventos de aprendizado
        for agent_id in agent_performances.keys():
            await self.record_learning_event(
                LearningEventType.PERFORMANCE_OPTIMIZATION,
                agent_id,
                session.session_id,
                {
                    "performance": agent_performances[agent_id],
                    "user_satisfaction": user_satisfaction,
                    "session_duration": (datetime.now() - session.created_at).total_seconds()
                },
                impact_score=user_satisfaction or 0.5
            )
        
        return analysis
    
    async def get_agent_learning_insights(self, agent_id: str) -> Dict[str, Any]:
        """
        Obtém insights de aprendizado para um agente específico
        
        Args:
            agent_id: ID do agente
            
        Returns:
            Insights de aprendizado
        """
        if agent_id not in self.agent_metrics:
            return {"error": "Agente não encontrado"}
        
        metrics = self.agent_metrics[agent_id]
        
        # Coletar eventos recentes do agente
        recent_events = [
            event for event in self.learning_events
            if event.agent_id == agent_id and 
            event.timestamp > datetime.now() - timedelta(days=7)
        ]
        
        # Coletar feedback recente
        recent_feedback = [
            feedback for feedback in self.feedback_events
            if feedback.specific_agent == agent_id and
            feedback.timestamp > datetime.now() - timedelta(days=7)
        ]
        
        # Calcular tendências
        performance_trend = await self._calculate_performance_trend(agent_id)
        learning_velocity = await self._calculate_learning_velocity(agent_id)
        
        # Identificar padrões de conhecimento
        agent_patterns = [
            pattern for pattern in self.knowledge_patterns.values()
            if agent_id in pattern.agents_involved
        ]
        
        insights = {
            "agent_id": agent_id,
            "current_metrics": {
                "performance_score": metrics.performance_score,
                "improvement_rate": metrics.improvement_rate,
                "feedback_score": metrics.feedback_score,
                "collaboration_effectiveness": metrics.collaboration_effectiveness,
                "knowledge_growth": metrics.knowledge_growth,
                "adaptation_speed": metrics.adaptation_speed
            },
            "trends": {
                "performance_trend": performance_trend,
                "learning_velocity": learning_velocity
            },
            "recent_activity": {
                "learning_events": len(recent_events),
                "feedback_received": len(recent_feedback),
                "knowledge_patterns": len(agent_patterns)
            },
            "recommendations": await self._generate_learning_recommendations(agent_id),
            "next_learning_goals": await self._suggest_learning_goals(agent_id)
        }
        
        return insights
    
    async def adapt_agent_behavior(
        self,
        agent_id: str,
        adaptation_data: Dict[str, Any]
    ) -> bool:
        """
        Adapta comportamento de um agente baseado no aprendizado
        
        Args:
            agent_id: ID do agente
            adaptation_data: Dados para adaptação
            
        Returns:
            True se adaptação foi aplicada
        """
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        
        try:
            # Aplicar adaptações baseadas no tipo
            adaptations_applied = []
            
            # Adaptação de colaboração
            if "collaboration_style" in adaptation_data:
                new_style = adaptation_data["collaboration_style"]
                agent.collaboration_preferences["style"] = new_style
                adaptations_applied.append("collaboration_style")
            
            # Adaptação de comunicação
            if "communication_style" in adaptation_data:
                new_comm = adaptation_data["communication_style"]
                agent.collaboration_preferences["communication"] = new_comm
                adaptations_applied.append("communication_style")
            
            # Adaptação de expertise
            if "expertise_focus" in adaptation_data:
                focus_areas = adaptation_data["expertise_focus"]
                # Reordenar áreas de expertise baseado no foco
                agent.profile.expertise_areas = focus_areas + [
                    area for area in agent.profile.expertise_areas 
                    if area not in focus_areas
                ]
                adaptations_applied.append("expertise_focus")
            
            # Registrar evento de adaptação
            await self.record_learning_event(
                LearningEventType.ADAPTATION_TRIGGER,
                agent_id,
                f"adaptation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                {
                    "adaptations": adaptations_applied,
                    "adaptation_data": adaptation_data
                },
                impact_score=0.8
            )
            
            # Atualizar métricas
            metrics = self.agent_metrics[agent_id]
            metrics.adaptation_speed += 0.1
            metrics.last_updated = datetime.now()
            
            self.logger.info(f"🔄 Agente {agent_id} adaptado: {adaptations_applied}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao adaptar agente {agent_id}: {e}")
            return False
    
    async def get_system_learning_status(self) -> Dict[str, Any]:
        """
        Obtém status geral do sistema de aprendizado
        
        Returns:
            Status do sistema
        """
        total_events = len(self.learning_events)
        total_feedback = len(self.feedback_events)
        
        # Calcular métricas agregadas
        avg_performance = np.mean([
            metrics.performance_score 
            for metrics in self.agent_metrics.values()
        ]) if self.agent_metrics else 0.0
        
        avg_improvement = np.mean([
            metrics.improvement_rate 
            for metrics in self.agent_metrics.values()
        ]) if self.agent_metrics else 0.0
        
        # Eventos recentes (última semana)
        recent_events = [
            event for event in self.learning_events
            if event.timestamp > datetime.now() - timedelta(days=7)
        ]
        
        # Padrões ativos
        active_patterns = [
            pattern for pattern in self.knowledge_patterns.values()
            if pattern.last_used > datetime.now() - timedelta(days=30)
        ]
        
        return {
            "system_status": {
                "is_active": self.is_learning_active,
                "last_cycle": self.last_learning_cycle.isoformat() if self.last_learning_cycle else None,
                "agents_count": len(self.agents) if hasattr(self, 'agents') else 0
            },
            "learning_metrics": {
                "total_events": total_events,
                "total_feedback": total_feedback,
                "recent_events": len(recent_events),
                "active_patterns": len(active_patterns),
                "avg_performance": avg_performance,
                "avg_improvement_rate": avg_improvement
            },
            "agent_metrics": {
                agent_id: {
                    "performance": metrics.performance_score,
                    "improvement": metrics.improvement_rate,
                    "feedback": metrics.feedback_score
                }
                for agent_id, metrics in self.agent_metrics.items()
            },
            "learning_config": self.learning_config
        }
    
    async def _learning_cycle(self):
        """Ciclo principal de aprendizado (executa continuamente)"""
        while self.is_learning_active:
            try:
                self.last_learning_cycle = datetime.now()
                
                # Processar eventos de feedback pendentes
                await self._process_pending_feedback()
                
                # Processar eventos de aprendizado pendentes
                await self._process_pending_learning_events()
                
                # Identificar novos padrões
                await self._identify_new_patterns()
                
                # Atualizar métricas dos agentes
                await self._update_agent_metrics()
                
                # Aplicar adaptações automáticas
                await self._apply_automatic_adaptations()
                
                # Persistir dados
                await self._save_learning_data()
                
                # Aguardar próximo ciclo (5 minutos)
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"❌ Erro no ciclo de aprendizado: {e}")
                await asyncio.sleep(60)  # Aguardar 1 minuto em caso de erro
    
    async def _process_critical_feedback(self, feedback: FeedbackEvent):
        """Processa feedback crítico imediatamente"""
        if feedback.feedback_type == FeedbackType.NEGATIVE and feedback.rating and feedback.rating <= 2:
            # Feedback muito negativo - ação imediata
            if feedback.specific_agent:
                await self.record_learning_event(
                    LearningEventType.FAILURE_ANALYSIS,
                    feedback.specific_agent,
                    feedback.session_id,
                    {
                        "feedback": feedback.comment,
                        "rating": feedback.rating,
                        "urgency": "high"
                    },
                    impact_score=1.0
                )
        
        feedback.processed = True
    
    async def _identify_success_pattern(
        self,
        session: CollaborationSession,
        performances: Dict[str, Any]
    ) -> Optional[KnowledgePattern]:
        """Identifica padrão de sucesso em uma sessão"""
        # Implementação simplificada - pode ser expandida
        high_performers = [
            agent_id for agent_id, perf in performances.items()
            if perf["response_quality"] > 0.8
        ]
        
        if len(high_performers) >= 2:
            pattern_id = f"success_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            return KnowledgePattern(
                pattern_id=pattern_id,
                pattern_type="collaboration_success",
                context=session.user_request[:100],
                success_rate=0.9,
                usage_count=1,
                agents_involved=high_performers,
                created_at=datetime.now(),
                last_used=datetime.now()
            )
        
        return None
    
    async def _calculate_performance_trend(self, agent_id: str) -> str:
        """Calcula tendência de performance de um agente"""
        # Implementação simplificada
        metrics = self.agent_metrics.get(agent_id)
        if not metrics:
            return "unknown"
        
        if metrics.improvement_rate > 0.1:
            return "improving"
        elif metrics.improvement_rate < -0.1:
            return "declining"
        else:
            return "stable"
    
    async def _calculate_learning_velocity(self, agent_id: str) -> float:
        """Calcula velocidade de aprendizado de um agente"""
        # Eventos de aprendizado recentes
        recent_events = [
            event for event in self.learning_events
            if event.agent_id == agent_id and 
            event.timestamp > datetime.now() - timedelta(days=7)
        ]
        
        return len(recent_events) / 7.0  # Eventos por dia
    
    async def _generate_learning_recommendations(self, agent_id: str) -> List[str]:
        """Gera recomendações de aprendizado para um agente"""
        recommendations = []
        metrics = self.agent_metrics.get(agent_id)
        
        if not metrics:
            return recommendations
        
        if metrics.collaboration_effectiveness < 0.6:
            recommendations.append("Melhorar habilidades de colaboração")
        
        if metrics.feedback_score < 0.6:
            recommendations.append("Focar em qualidade das respostas")
        
        if metrics.adaptation_speed < 0.5:
            recommendations.append("Aumentar flexibilidade e adaptabilidade")
        
        return recommendations
    
    async def _suggest_learning_goals(self, agent_id: str) -> List[str]:
        """Sugere objetivos de aprendizado para um agente"""
        goals = []
        metrics = self.agent_metrics.get(agent_id)
        
        if not metrics:
            return goals
        
        if metrics.performance_score < 0.8:
            goals.append("Alcançar 80% de performance score")
        
        if metrics.knowledge_growth < 0.1:
            goals.append("Aumentar taxa de crescimento de conhecimento")
        
        return goals
    
    async def _process_pending_feedback(self):
        """Processa feedback pendente"""
        pending_feedback = [f for f in self.feedback_events if not f.processed]
        
        for feedback in pending_feedback:
            # Processar feedback e atualizar métricas
            if feedback.specific_agent and feedback.rating:
                agent_id = feedback.specific_agent
                if agent_id in self.agent_metrics:
                    metrics = self.agent_metrics[agent_id]
                    
                    # Atualizar score de feedback (média móvel)
                    new_score = feedback.rating / 5.0
                    metrics.feedback_score = (metrics.feedback_score * 0.9) + (new_score * 0.1)
                    metrics.last_updated = datetime.now()
            
            feedback.processed = True
    
    async def _process_pending_learning_events(self):
        """Processa eventos de aprendizado pendentes"""
        pending_events = [e for e in self.learning_events if not e.processed]
        
        for event in pending_events:
            # Processar evento baseado no tipo
            if event.event_type == LearningEventType.SUCCESS_PATTERN:
                await self._process_success_pattern_event(event)
            elif event.event_type == LearningEventType.FAILURE_ANALYSIS:
                await self._process_failure_event(event)
            
            event.processed = True
    
    async def _process_success_pattern_event(self, event: LearningEvent):
        """Processa evento de padrão de sucesso"""
        agent_id = event.agent_id
        if agent_id in self.agent_metrics:
            metrics = self.agent_metrics[agent_id]
            metrics.performance_score += 0.05
            metrics.improvement_rate += 0.02
            metrics.last_updated = datetime.now()
    
    async def _process_failure_event(self, event: LearningEvent):
        """Processa evento de falha"""
        agent_id = event.agent_id
        if agent_id in self.agent_metrics:
            metrics = self.agent_metrics[agent_id]
            metrics.performance_score = max(0.1, metrics.performance_score - 0.03)
            metrics.last_updated = datetime.now()
    
    async def _identify_new_patterns(self):
        """Identifica novos padrões de conhecimento"""
        # Implementação simplificada - pode ser expandida com ML
        pass
    
    async def _update_agent_metrics(self):
        """Atualiza métricas dos agentes"""
        for agent_id, metrics in self.agent_metrics.items():
            # Calcular crescimento de conhecimento baseado em eventos recentes
            recent_events = [
                e for e in self.learning_events
                if e.agent_id == agent_id and 
                e.timestamp > datetime.now() - timedelta(days=1)
            ]
            
            metrics.knowledge_growth = len(recent_events) * 0.01
            
            # Normalizar scores
            metrics.performance_score = max(0.0, min(1.0, metrics.performance_score))
            metrics.feedback_score = max(0.0, min(1.0, metrics.feedback_score))
            metrics.collaboration_effectiveness = max(0.0, min(1.0, metrics.collaboration_effectiveness))
    
    async def _apply_automatic_adaptations(self):
        """Aplica adaptações automáticas baseadas no aprendizado"""
        for agent_id, metrics in self.agent_metrics.items():
            # Se performance está baixa, sugerir adaptação
            if metrics.performance_score < 0.4:
                adaptation_data = {
                    "collaboration_style": "more_supportive",
                    "communication_style": "more_detailed"
                }
                await self.adapt_agent_behavior(agent_id, adaptation_data)
    
    async def _load_learning_data(self):
        """Carrega dados de aprendizado persistidos"""
        try:
            # Carregar métricas dos agentes
            metrics_file = os.path.join(self.data_dir, "agent_metrics.pkl")
            if os.path.exists(metrics_file):
                with open(metrics_file, 'rb') as f:
                    self.agent_metrics = pickle.load(f)
            
            # Carregar padrões de conhecimento
            patterns_file = os.path.join(self.data_dir, "knowledge_patterns.pkl")
            if os.path.exists(patterns_file):
                with open(patterns_file, 'rb') as f:
                    self.knowledge_patterns = pickle.load(f)
            
            self.logger.info("📚 Dados de aprendizado carregados")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro ao carregar dados: {e}")
    
    async def _save_learning_data(self):
        """Salva dados de aprendizado"""
        try:
            # Salvar métricas dos agentes
            metrics_file = os.path.join(self.data_dir, "agent_metrics.pkl")
            with open(metrics_file, 'wb') as f:
                pickle.dump(self.agent_metrics, f)
            
            # Salvar padrões de conhecimento
            patterns_file = os.path.join(self.data_dir, "knowledge_patterns.pkl")
            with open(patterns_file, 'wb') as f:
                pickle.dump(self.knowledge_patterns, f)
            
            self.logger.debug("💾 Dados de aprendizado salvos")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao salvar dados: {e}")
    
    async def shutdown(self):
        """Encerra o sistema de aprendizado"""
        self.is_learning_active = False
        await self._save_learning_data()
        self.logger.info("🛑 Sistema de Aprendizado Contínuo encerrado")


# Instância global do sistema de aprendizado
learning_system = ContinuousLearningSystem()