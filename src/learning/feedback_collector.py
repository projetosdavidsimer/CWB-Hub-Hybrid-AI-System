#!/usr/bin/env python3
"""
CWB Hub Feedback Collector - Sistema de Coleta de Feedback
Melhoria #7 - Coleta inteligente de feedback para aprendizado contínuo
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from .continuous_learning_engine import (
    InteractionRecord, 
    InteractionType, 
    FeedbackType,
    learning_engine
)

logger = logging.getLogger(__name__)

class FeedbackSource(Enum):
    """Fontes de feedback"""
    USER_EXPLICIT = "user_explicit"  # Feedback direto do usuário
    SYSTEM_IMPLICIT = "system_implicit"  # Comportamento inferido
    API_METRICS = "api_metrics"  # Métricas de API
    SESSION_ANALYSIS = "session_analysis"  # Análise de sessão
    AGENT_CONFIDENCE = "agent_confidence"  # Confiança dos agentes

@dataclass
class FeedbackEvent:
    """Evento de feedback coletado"""
    event_id: str
    session_id: str
    interaction_id: str
    source: FeedbackSource
    feedback_type: FeedbackType
    value: Any
    metadata: Dict[str, Any]
    timestamp: datetime

class FeedbackCollector:
    """
    Coletor de Feedback Inteligente
    
    Coleta feedback de múltiplas fontes:
    - Ratings explícitos do usuário
    - Comportamento implícito (tempo, iterações)
    - Métricas de sistema (performance, confiança)
    - Análise de sessão (duração, engajamento)
    """
    
    def __init__(self):
        self.feedback_events: List[FeedbackEvent] = []
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.feedback_handlers: Dict[FeedbackType, List[Callable]] = {}
        
        # Configurações
        self.implicit_feedback_enabled = True
        self.real_time_analysis = True
        self.feedback_aggregation_window = 300  # 5 minutos
        
        # Métricas
        self.collection_stats = {
            "total_feedback_events": 0,
            "explicit_feedback_count": 0,
            "implicit_feedback_count": 0,
            "average_rating": 0.0,
            "feedback_velocity": 0.0
        }
        
        logger.info("📊 Feedback Collector inicializado")
    
    async def start_session_tracking(self, session_id: str, user_id: str, context: Dict[str, Any]) -> None:
        """Inicia rastreamento de uma sessão"""
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "start_time": datetime.now(),
            "context": context,
            "interactions": [],
            "feedback_events": [],
            "implicit_metrics": {
                "total_interactions": 0,
                "total_iterations": 0,
                "session_duration": 0.0,
                "engagement_score": 0.0
            }
        }
        
        logger.debug(f"📝 Sessão iniciada: {session_id}")
    
    async def track_interaction(self, 
                              session_id: str,
                              interaction_id: str,
                              interaction_type: InteractionType,
                              user_request: str,
                              response: str,
                              agents_involved: List[str],
                              response_time: float,
                              confidence_score: float) -> None:
        """Rastreia uma interação para coleta de feedback"""
        
        if session_id not in self.active_sessions:
            await self.start_session_tracking(session_id, "unknown", {})
        
        session = self.active_sessions[session_id]
        
        # Criar registro de interação
        interaction_record = InteractionRecord(
            interaction_id=interaction_id,
            session_id=session_id,
            user_id=session["user_id"],
            interaction_type=interaction_type,
            timestamp=datetime.now(),
            user_request=user_request,
            context=session["context"],
            agents_involved=agents_involved,
            response=response,
            response_time=response_time,
            confidence_score=confidence_score
        )
        
        # Adicionar à sessão
        session["interactions"].append(interaction_record)
        session["implicit_metrics"]["total_interactions"] += 1
        
        # Coletar feedback implícito imediatamente
        if self.implicit_feedback_enabled:
            await self._collect_implicit_feedback(interaction_record)
        
        # Análise em tempo real
        if self.real_time_analysis:
            await self._analyze_interaction_real_time(interaction_record)
        
        logger.debug(f"🔍 Interação rastreada: {interaction_id}")
    
    async def collect_explicit_feedback(self,
                                      session_id: str,
                                      interaction_id: str,
                                      rating: float,
                                      comments: Optional[str] = None,
                                      categories: Optional[List[str]] = None) -> None:
        """Coleta feedback explícito do usuário"""
        
        feedback_event = FeedbackEvent(
            event_id=f"explicit_{int(time.time())}",
            session_id=session_id,
            interaction_id=interaction_id,
            source=FeedbackSource.USER_EXPLICIT,
            feedback_type=FeedbackType.EXPLICIT_RATING,
            value=rating,
            metadata={
                "comments": comments,
                "categories": categories or [],
                "timestamp": datetime.now().isoformat()
            },
            timestamp=datetime.now()
        )
        
        await self._process_feedback_event(feedback_event)
        
        # Atualizar interação correspondente
        await self._update_interaction_with_feedback(interaction_id, rating, comments)
        
        logger.info(f"⭐ Feedback explícito coletado: {rating}/5.0 para {interaction_id}")
    
    async def _collect_implicit_feedback(self, interaction: InteractionRecord) -> None:
        """Coleta feedback implícito baseado no comportamento"""
        
        # Feedback baseado em tempo de resposta
        if interaction.response_time < 2.0:
            await self._create_implicit_feedback(
                interaction, 
                FeedbackType.IMPLICIT_BEHAVIOR,
                "fast_response",
                {"response_time": interaction.response_time, "quality": "good"}
            )
        elif interaction.response_time > 10.0:
            await self._create_implicit_feedback(
                interaction,
                FeedbackType.IMPLICIT_BEHAVIOR,
                "slow_response", 
                {"response_time": interaction.response_time, "quality": "poor"}
            )
        
        # Feedback baseado em confiança
        if interaction.confidence_score > 0.9:
            await self._create_implicit_feedback(
                interaction,
                FeedbackType.IMPLICIT_BEHAVIOR,
                "high_confidence",
                {"confidence": interaction.confidence_score, "quality": "excellent"}
            )
        elif interaction.confidence_score < 0.5:
            await self._create_implicit_feedback(
                interaction,
                FeedbackType.IMPLICIT_BEHAVIOR,
                "low_confidence",
                {"confidence": interaction.confidence_score, "quality": "poor"}
            )
    
    async def _create_implicit_feedback(self,
                                      interaction: InteractionRecord,
                                      feedback_type: FeedbackType,
                                      behavior: str,
                                      metadata: Dict[str, Any]) -> None:
        """Cria evento de feedback implícito"""
        
        feedback_event = FeedbackEvent(
            event_id=f"implicit_{behavior}_{int(time.time())}",
            session_id=interaction.session_id,
            interaction_id=interaction.interaction_id,
            source=FeedbackSource.SYSTEM_IMPLICIT,
            feedback_type=feedback_type,
            value=behavior,
            metadata=metadata,
            timestamp=datetime.now()
        )
        
        await self._process_feedback_event(feedback_event)
    
    async def track_iteration(self, session_id: str, interaction_id: str) -> None:
        """Rastreia uma iteração (refinamento) de resposta"""
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            session["implicit_metrics"]["total_iterations"] += 1
            
            # Encontrar interação correspondente
            for interaction in session["interactions"]:
                if interaction.interaction_id == interaction_id:
                    interaction.iteration_count += 1
                    
                    # Feedback implícito para múltiplas iterações
                    if interaction.iteration_count > 2:
                        await self._create_implicit_feedback(
                            interaction,
                            FeedbackType.ITERATION_COUNT,
                            "multiple_iterations",
                            {"iteration_count": interaction.iteration_count, "satisfaction": "low"}
                        )
                    
                    break
        
        logger.debug(f"🔄 Iteração rastreada para {interaction_id}")
    
    async def track_follow_up_question(self, session_id: str, interaction_id: str, question: str) -> None:
        """Rastreia pergunta de follow-up"""
        
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            
            # Encontrar interação correspondente
            for interaction in session["interactions"]:
                if interaction.interaction_id == interaction_id:
                    interaction.follow_up_questions += 1
                    
                    # Feedback implícito para muitas perguntas
                    if interaction.follow_up_questions > 1:
                        await self._create_implicit_feedback(
                            interaction,
                            FeedbackType.FOLLOW_UP_QUESTIONS,
                            "multiple_questions",
                            {"question_count": interaction.follow_up_questions, "clarity": "low"}
                        )
                    
                    break
        
        logger.debug(f"❓ Follow-up rastreado para {interaction_id}")
    
    async def end_session_tracking(self, session_id: str) -> Dict[str, Any]:
        """Finaliza rastreamento de sessão e gera análise"""
        
        if session_id not in self.active_sessions:
            return {}
        
        session = self.active_sessions[session_id]
        end_time = datetime.now()
        session_duration = (end_time - session["start_time"]).total_seconds()
        
        # Atualizar métricas da sessão
        session["implicit_metrics"]["session_duration"] = session_duration
        session["implicit_metrics"]["engagement_score"] = self._calculate_engagement_score(session)
        
        # Coletar feedback de duração da sessão
        await self._collect_session_duration_feedback(session_id, session_duration)
        
        # Processar todas as interações da sessão para aprendizado
        for interaction in session["interactions"]:
            interaction.session_duration = session_duration
            await learning_engine.record_interaction(interaction)
        
        # Gerar análise da sessão
        session_analysis = await self._generate_session_analysis(session)
        
        # Remover da lista de sessões ativas
        del self.active_sessions[session_id]
        
        logger.info(f"📊 Sessão finalizada: {session_id} (duração: {session_duration:.1f}s)")
        
        return session_analysis
    
    def _calculate_engagement_score(self, session: Dict[str, Any]) -> float:
        """Calcula score de engajamento da sessão"""
        metrics = session["implicit_metrics"]
        
        # Fatores de engajamento
        interaction_factor = min(1.0, metrics["total_interactions"] / 5.0)  # Normalizar por 5 interações
        duration_factor = min(1.0, metrics["session_duration"] / 300.0)  # Normalizar por 5 minutos
        iteration_penalty = max(0.0, 1.0 - (metrics["total_iterations"] * 0.1))  # Penalizar muitas iterações
        
        engagement_score = (interaction_factor + duration_factor + iteration_penalty) / 3.0
        
        return max(0.0, min(1.0, engagement_score))
    
    async def _collect_session_duration_feedback(self, session_id: str, duration: float) -> None:
        """Coleta feedback baseado na duração da sessão"""
        
        feedback_value = "optimal"
        quality = "good"
        
        if duration < 30:  # Muito curta
            feedback_value = "too_short"
            quality = "poor"
        elif duration > 1800:  # Muito longa (30 min)
            feedback_value = "too_long"
            quality = "poor"
        elif 60 <= duration <= 600:  # Duração ideal (1-10 min)
            feedback_value = "optimal"
            quality = "excellent"
        
        feedback_event = FeedbackEvent(
            event_id=f"session_duration_{int(time.time())}",
            session_id=session_id,
            interaction_id="session_level",
            source=FeedbackSource.SESSION_ANALYSIS,
            feedback_type=FeedbackType.SESSION_DURATION,
            value=feedback_value,
            metadata={
                "duration": duration,
                "quality": quality,
                "optimal_range": "60-600 seconds"
            },
            timestamp=datetime.now()
        )
        
        await self._process_feedback_event(feedback_event)
    
    async def _analyze_interaction_real_time(self, interaction: InteractionRecord) -> None:
        """Análise em tempo real da interação"""
        
        # Detectar problemas imediatos
        issues = []
        
        if interaction.response_time > 15.0:
            issues.append("slow_response")
        
        if interaction.confidence_score < 0.4:
            issues.append("low_confidence")
        
        if len(interaction.response) < 50:
            issues.append("short_response")
        
        # Criar feedback para problemas detectados
        for issue in issues:
            await self._create_implicit_feedback(
                interaction,
                FeedbackType.IMPLICIT_BEHAVIOR,
                issue,
                {"severity": "high", "requires_attention": True}
            )
    
    async def _process_feedback_event(self, event: FeedbackEvent) -> None:
        """Processa um evento de feedback"""
        
        # Adicionar à lista de eventos
        self.feedback_events.append(event)
        
        # Atualizar estatísticas
        self.collection_stats["total_feedback_events"] += 1
        
        if event.source == FeedbackSource.USER_EXPLICIT:
            self.collection_stats["explicit_feedback_count"] += 1
            
            # Atualizar rating médio
            if isinstance(event.value, (int, float)):
                current_avg = self.collection_stats["average_rating"]
                explicit_count = self.collection_stats["explicit_feedback_count"]
                new_avg = ((current_avg * (explicit_count - 1)) + event.value) / explicit_count
                self.collection_stats["average_rating"] = new_avg
        else:
            self.collection_stats["implicit_feedback_count"] += 1
        
        # Executar handlers registrados
        if event.feedback_type in self.feedback_handlers:
            for handler in self.feedback_handlers[event.feedback_type]:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"❌ Erro no handler de feedback: {e}")
        
        logger.debug(f"📊 Evento de feedback processado: {event.event_id}")
    
    async def _update_interaction_with_feedback(self, 
                                              interaction_id: str, 
                                              rating: float, 
                                              comments: Optional[str]) -> None:
        """Atualiza interação com feedback explícito"""
        
        # Encontrar interação em sessões ativas
        for session in self.active_sessions.values():
            for interaction in session["interactions"]:
                if interaction.interaction_id == interaction_id:
                    interaction.explicit_rating = rating
                    # Adicionar comentários aos metadados se necessário
                    break
    
    async def _generate_session_analysis(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Gera análise completa da sessão"""
        
        interactions = session["interactions"]
        metrics = session["implicit_metrics"]
        
        if not interactions:
            return {"error": "No interactions in session"}
        
        # Calcular métricas agregadas
        avg_response_time = sum(i.response_time for i in interactions) / len(interactions)
        avg_confidence = sum(i.confidence_score for i in interactions) / len(interactions)
        total_iterations = sum(i.iteration_count for i in interactions)
        
        # Identificar agentes mais utilizados
        agent_usage = {}
        for interaction in interactions:
            for agent in interaction.agents_involved:
                agent_usage[agent] = agent_usage.get(agent, 0) + 1
        
        # Calcular satisfação geral
        explicit_ratings = [i.explicit_rating for i in interactions if i.explicit_rating is not None]
        implicit_satisfactions = [i.implicit_satisfaction for i in interactions if i.implicit_satisfaction is not None]
        
        analysis = {
            "session_id": session["interactions"][0].session_id,
            "duration": metrics["session_duration"],
            "total_interactions": len(interactions),
            "total_iterations": total_iterations,
            "engagement_score": metrics["engagement_score"],
            "performance_metrics": {
                "avg_response_time": avg_response_time,
                "avg_confidence": avg_confidence,
                "iterations_per_interaction": total_iterations / len(interactions)
            },
            "satisfaction_metrics": {
                "explicit_ratings": explicit_ratings,
                "avg_explicit_rating": sum(explicit_ratings) / len(explicit_ratings) if explicit_ratings else None,
                "implicit_satisfactions": implicit_satisfactions,
                "avg_implicit_satisfaction": sum(implicit_satisfactions) / len(implicit_satisfactions) if implicit_satisfactions else None
            },
            "agent_usage": agent_usage,
            "interaction_types": [i.interaction_type.value for i in interactions],
            "quality_assessment": self._assess_session_quality(session),
            "recommendations": self._generate_session_recommendations(session)
        }
        
        return analysis
    
    def _assess_session_quality(self, session: Dict[str, Any]) -> str:
        """Avalia qualidade geral da sessão"""
        
        metrics = session["implicit_metrics"]
        engagement = metrics["engagement_score"]
        
        if engagement > 0.8:
            return "excellent"
        elif engagement > 0.6:
            return "good"
        elif engagement > 0.4:
            return "fair"
        else:
            return "poor"
    
    def _generate_session_recommendations(self, session: Dict[str, Any]) -> List[str]:
        """Gera recomendações baseadas na análise da sessão"""
        
        recommendations = []
        interactions = session["interactions"]
        metrics = session["implicit_metrics"]
        
        # Recomendações baseadas em performance
        avg_response_time = sum(i.response_time for i in interactions) / len(interactions)
        if avg_response_time > 8.0:
            recommendations.append("Otimizar tempo de resposta dos agentes")
        
        # Recomendações baseadas em iterações
        if metrics["total_iterations"] > len(interactions) * 2:
            recommendations.append("Melhorar precisão das respostas iniciais")
        
        # Recomendações baseadas em confiança
        avg_confidence = sum(i.confidence_score for i in interactions) / len(interactions)
        if avg_confidence < 0.7:
            recommendations.append("Aumentar confiança dos agentes nas respostas")
        
        # Recomendações baseadas em engajamento
        if metrics["engagement_score"] < 0.5:
            recommendations.append("Melhorar engajamento e relevância das respostas")
        
        return recommendations
    
    def register_feedback_handler(self, feedback_type: FeedbackType, handler: Callable) -> None:
        """Registra handler para tipo específico de feedback"""
        
        if feedback_type not in self.feedback_handlers:
            self.feedback_handlers[feedback_type] = []
        
        self.feedback_handlers[feedback_type].append(handler)
        logger.info(f"📝 Handler registrado para {feedback_type.value}")
    
    async def get_feedback_analytics(self) -> Dict[str, Any]:
        """Retorna analytics do sistema de feedback"""
        
        recent_events = [
            e for e in self.feedback_events 
            if e.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        return {
            "collection_stats": self.collection_stats.copy(),
            "recent_events_count": len(recent_events),
            "active_sessions": len(self.active_sessions),
            "feedback_sources": {
                source.value: len([e for e in recent_events if e.source == source])
                for source in FeedbackSource
            },
            "feedback_types": {
                ftype.value: len([e for e in recent_events if e.feedback_type == ftype])
                for ftype in FeedbackType
            }
        }

# Instância global do coletor de feedback
feedback_collector = FeedbackCollector()

if __name__ == "__main__":
    # Teste básico do coletor de feedback
    async def test_feedback_collector():
        print("🧪 Testando Coletor de Feedback...")
        
        # Iniciar sessão
        await feedback_collector.start_session_tracking(
            "test_session", 
            "test_user", 
            {"domain": "test"}
        )
        
        # Rastrear interação
        await feedback_collector.track_interaction(
            "test_session",
            "test_interaction",
            InteractionType.PROJECT_ANALYSIS,
            "Teste de requisição",
            "Resposta de teste",
            ["ana_beatriz_costa"],
            3.5,
            0.8
        )
        
        # Coletar feedback explícito
        await feedback_collector.collect_explicit_feedback(
            "test_session",
            "test_interaction",
            4.5,
            "Ótima resposta!"
        )
        
        # Finalizar sessão
        analysis = await feedback_collector.end_session_tracking("test_session")
        print(f"📊 Análise da sessão: {analysis}")
        
        # Analytics
        analytics = await feedback_collector.get_feedback_analytics()
        print(f"📈 Analytics: {analytics}")
        
        print("✅ Teste concluído!")
    
    asyncio.run(test_feedback_collector())