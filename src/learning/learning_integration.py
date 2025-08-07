"""
Integração do Sistema de Aprendizado Contínuo
Melhoria #7 - Ponte entre aprendizado e sistema principal

Integra o sistema de aprendizado com:
- Orquestrador principal
- Agentes CWB Hub
- Sistema de persistência
- APIs externas
- Interface web

Criado por: David Simer
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json

# Importações do sistema CWB Hub
try:
    from ..core.hybrid_ai_orchestrator import HybridAIOrchestrator, CollaborationSession
    from ..agents.base_agent import BaseAgent
    from .continuous_learning_system import learning_system, LearningEventType, FeedbackType
    from .pattern_analyzer import pattern_analyzer
    from .feedback_processor import feedback_processor
except ImportError:
    # Fallback para desenvolvimento
    pass


class LearningIntegration:
    """
    Integração do Sistema de Aprendizado Contínuo
    
    Responsabilidades:
    1. Conectar aprendizado com orquestrador
    2. Capturar eventos de aprendizado automaticamente
    3. Aplicar insights em tempo real
    4. Sincronizar com persistência
    5. Expor APIs de aprendizado
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_active = False
        self.orchestrator: Optional[Any] = None  # HybridAIOrchestrator
        
        # Configurações de integração
        self.integration_config = {
            "auto_capture_events": True,
            "real_time_adaptation": True,
            "feedback_auto_processing": True,
            "pattern_analysis_interval": 3600,  # 1 hora
            "learning_sync_interval": 300,      # 5 minutos
            "max_auto_adaptations_per_hour": 5
        }
        
        # Contadores para controle
        self.adaptations_this_hour = 0
        self.last_adaptation_reset = datetime.now()
        
        self.logger.info("🔗 Integração de Aprendizado CWB Hub inicializada")
    
    async def initialize(self, orchestrator: Any):  # HybridAIOrchestrator
        """
        Inicializa a integração com o orquestrador
        
        Args:
            orchestrator: Instância do orquestrador principal
        """
        self.orchestrator = orchestrator
        
        # Inicializar sistemas de aprendizado
        await learning_system.initialize(orchestrator.agents)
        
        # Configurar hooks no orquestrador
        await self._setup_orchestrator_hooks()
        
        # Iniciar tarefas de background
        if self.integration_config["auto_capture_events"]:
            asyncio.create_task(self._auto_capture_loop())
        
        if self.integration_config["real_time_adaptation"]:
            asyncio.create_task(self._adaptation_loop())
        
        self.is_active = True
        self.logger.info("🔗 Integração ativada com sucesso")
    
    async def _setup_orchestrator_hooks(self):
        """Configura hooks no orquestrador para captura automática"""
        # Monkey patch para capturar eventos automaticamente
        original_process_request = self.orchestrator.process_request
        
        async def enhanced_process_request(user_request: str, session_id: Optional[str] = None):
            # Processar requisição normalmente
            result = await original_process_request(user_request, session_id)
            
            # Capturar evento de aprendizado
            if self.integration_config["auto_capture_events"]:
                await self._capture_session_event(session_id or "unknown", user_request, result)
            
            return result
        
        # Substituir método
        self.orchestrator.process_request = enhanced_process_request
        
        self.logger.info("🔗 Hooks configurados no orquestrador")
    
    async def _capture_session_event(self, session_id: str, request: str, result: str):
        """Captura evento de sessão para aprendizado"""
        try:
            # Obter sessão ativa
            session = self.orchestrator.active_sessions.get(session_id)
            if not session:
                return
            
            # Analisar performance da sessão
            performance_analysis = await learning_system.analyze_session_performance(session)
            
            # Registrar eventos para cada agente envolvido
            for agent_response in session.agent_responses:
                await learning_system.record_learning_event(
                    LearningEventType.PERFORMANCE_OPTIMIZATION,
                    agent_response.agent_id,
                    session_id,
                    {
                        "request": request[:200],  # Primeiros 200 chars
                        "response_confidence": agent_response.confidence,
                        "session_iterations": session.iterations,
                        "performance_analysis": performance_analysis
                    },
                    impact_score=agent_response.confidence
                )
            
            # Analisar padrões se houver dados suficientes
            if len(self.orchestrator.active_sessions) >= 5:
                await self._trigger_pattern_analysis()
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao capturar evento de sessão: {e}")
    
    async def _trigger_pattern_analysis(self):
        """Dispara análise de padrões"""
        try:
            sessions = list(self.orchestrator.active_sessions.values())
            analysis_result = await pattern_analyzer.analyze_session_patterns(sessions)
            
            # Aplicar insights automaticamente
            if self.integration_config["real_time_adaptation"]:
                await self._apply_pattern_insights(analysis_result)
            
        except Exception as e:
            self.logger.error(f"❌ Erro na análise de padrões: {e}")
    
    async def _apply_pattern_insights(self, analysis_result):
        """Aplica insights de padrões automaticamente"""
        if not self._can_apply_adaptation():
            return
        
        for pattern in analysis_result.patterns_found:
            if pattern.confidence > 0.8:
                # Aplicar adaptação baseada no padrão
                if pattern.pattern_type.value == "success_collaboration":
                    await self._apply_collaboration_optimization(pattern)
                elif pattern.pattern_type.value == "user_preference":
                    await self._apply_preference_optimization(pattern)
        
        self.adaptations_this_hour += 1
    
    async def _apply_collaboration_optimization(self, pattern):
        """Aplica otimização de colaboração"""
        for agent_id in pattern.agents_involved:
            adaptation_data = {
                "collaboration_style": "enhanced_synergy",
                "preferred_partners": pattern.agents_involved
            }
            
            success = await learning_system.adapt_agent_behavior(agent_id, adaptation_data)
            if success:
                self.logger.info(f"🔄 Colaboração otimizada para {agent_id}")
    
    async def _apply_preference_optimization(self, pattern):
        """Aplica otimização de preferências"""
        relevant_agents = pattern.agents_involved
        
        for agent_id in relevant_agents:
            adaptation_data = {
                "expertise_focus": [pattern.context.split()[-1]],  # Última palavra como foco
                "communication_style": "user_preference_aligned"
            }
            
            success = await learning_system.adapt_agent_behavior(agent_id, adaptation_data)
            if success:
                self.logger.info(f"🎯 Preferência otimizada para {agent_id}")
    
    def _can_apply_adaptation(self) -> bool:
        """Verifica se pode aplicar adaptação (controle de rate limiting)"""
        now = datetime.now()
        
        # Reset contador a cada hora
        if now - self.last_adaptation_reset > timedelta(hours=1):
            self.adaptations_this_hour = 0
            self.last_adaptation_reset = now
        
        return self.adaptations_this_hour < self.integration_config["max_auto_adaptations_per_hour"]
    
    async def _auto_capture_loop(self):
        """Loop de captura automática de eventos"""
        while self.is_active:
            try:
                # Capturar métricas dos agentes
                if self.orchestrator and self.orchestrator.agents:
                    await self._capture_agent_metrics()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.integration_config["learning_sync_interval"])
                
            except Exception as e:
                self.logger.error(f"❌ Erro no loop de captura: {e}")
                await asyncio.sleep(60)
    
    async def _adaptation_loop(self):
        """Loop de adaptação em tempo real"""
        while self.is_active:
            try:
                # Verificar se há adaptações pendentes
                insights = await learning_system.get_system_learning_status()
                
                # Aplicar adaptações baseadas em insights
                if insights.get("learning_metrics", {}).get("avg_improvement_rate", 0) < 0:
                    await self._trigger_improvement_adaptations()
                
                # Aguardar próximo ciclo
                await asyncio.sleep(self.integration_config["pattern_analysis_interval"])
                
            except Exception as e:
                self.logger.error(f"❌ Erro no loop de adaptação: {e}")
                await asyncio.sleep(300)
    
    async def _capture_agent_metrics(self):
        """Captura métricas dos agentes"""
        for agent_id, agent in self.orchestrator.agents.items():
            # Capturar métricas de saúde do LLM
            llm_health = await agent.get_llm_health_status()
            
            # Registrar evento de monitoramento
            await learning_system.record_learning_event(
                LearningEventType.PERFORMANCE_OPTIMIZATION,
                agent_id,
                f"health_check_{datetime.now().strftime('%Y%m%d_%H%M')}",
                {
                    "llm_health": llm_health,
                    "interactions_count": len(agent.context.previous_interactions),
                    "collaborations_count": len(agent.context.collaboration_history)
                },
                impact_score=0.3
            )
    
    async def _trigger_improvement_adaptations(self):
        """Dispara adaptações de melhoria"""
        if not self._can_apply_adaptation():
            return
        
        # Identificar agentes com performance baixa
        status = await learning_system.get_system_learning_status()
        
        for agent_id, metrics in status.get("agent_metrics", {}).items():
            if metrics.get("performance", 0.5) < 0.6:
                # Aplicar adaptação de melhoria
                adaptation_data = {
                    "communication_style": "more_detailed",
                    "collaboration_style": "more_supportive"
                }
                
                await learning_system.adapt_agent_behavior(agent_id, adaptation_data)
                self.adaptations_this_hour += 1
    
    # APIs públicas para integração externa
    
    async def process_user_feedback(
        self,
        feedback_text: str,
        session_id: str,
        user_id: Optional[str] = None,
        rating: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Processa feedback do usuário
        
        Args:
            feedback_text: Texto do feedback
            session_id: ID da sessão
            user_id: ID do usuário
            rating: Rating (1-5)
            
        Returns:
            Resultado do processamento
        """
        try:
            # Processar feedback
            processed = await feedback_processor.process_feedback(
                feedback_text, session_id, user_id, rating=rating
            )
            
            # Registrar no sistema de aprendizado
            feedback_type = FeedbackType.POSITIVE if processed.sentiment_level.value > 0 else FeedbackType.NEGATIVE
            
            feedback_id = await learning_system.record_feedback(
                session_id,
                feedback_type,
                processed.rating_inferred,
                feedback_text,
                processed.mentioned_agents[0] if processed.mentioned_agents else None,
                user_id
            )
            
            # Analisar sessão se feedback for significativo
            if processed.priority.value >= 3:  # HIGH ou CRITICAL
                session = self.orchestrator.active_sessions.get(session_id)
                if session:
                    user_satisfaction = processed.rating_inferred / 5.0 if processed.rating_inferred else None
                    await learning_system.analyze_session_performance(session, user_satisfaction)
            
            return {
                "feedback_id": feedback_id,
                "processed_feedback": {
                    "sentiment": processed.sentiment_level.name,
                    "confidence": processed.confidence,
                    "priority": processed.priority.name,
                    "categories": [cat.value for cat in processed.categories],
                    "mentioned_agents": processed.mentioned_agents
                },
                "learning_impact": "registered"
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar feedback: {e}")
            return {"error": str(e)}
    
    async def get_learning_insights(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtém insights de aprendizado
        
        Args:
            agent_id: ID do agente específico (opcional)
            
        Returns:
            Insights de aprendizado
        """
        try:
            if agent_id:
                return await learning_system.get_agent_learning_insights(agent_id)
            else:
                return await learning_system.get_system_learning_status()
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter insights: {e}")
            return {"error": str(e)}
    
    async def trigger_manual_adaptation(
        self,
        agent_id: str,
        adaptation_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Dispara adaptação manual
        
        Args:
            agent_id: ID do agente
            adaptation_type: Tipo de adaptação
            parameters: Parâmetros da adaptação
            
        Returns:
            Resultado da adaptação
        """
        try:
            success = await learning_system.adapt_agent_behavior(agent_id, parameters)
            
            return {
                "success": success,
                "agent_id": agent_id,
                "adaptation_type": adaptation_type,
                "parameters": parameters,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro na adaptação manual: {e}")
            return {"error": str(e)}
    
    async def get_feedback_analytics(self, days: int = 7) -> Dict[str, Any]:
        """
        Obtém analytics de feedback
        
        Args:
            days: Período em dias
            
        Returns:
            Analytics de feedback
        """
        try:
            # Obter resumo de feedback
            summary = await feedback_processor.get_feedback_summary(days)
            
            # Obter tendências
            trends = await feedback_processor.analyze_feedback_trends(days)
            
            # Obter insights
            insights = await feedback_processor.generate_feedback_insights()
            
            return {
                "summary": summary,
                "trends": [
                    {
                        "type": trend.trend_type,
                        "direction": trend.direction,
                        "current_value": trend.current_value,
                        "change_rate": trend.change_rate,
                        "significance": trend.significance
                    }
                    for trend in trends
                ],
                "insights": [
                    {
                        "type": insight.insight_type,
                        "description": insight.description,
                        "confidence": insight.confidence,
                        "affected_agents": insight.affected_agents,
                        "recommendations": insight.recommended_actions
                    }
                    for insight in insights
                ]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao obter analytics: {e}")
            return {"error": str(e)}
    
    async def export_learning_data(self, format_type: str = "json") -> str:
        """
        Exporta dados de aprendizado
        
        Args:
            format_type: Formato de exportação
            
        Returns:
            Dados exportados
        """
        try:
            # Obter status do sistema
            system_status = await learning_system.get_system_learning_status()
            
            # Obter padrões
            patterns = await pattern_analyzer.export_patterns(format_type)
            
            # Obter analytics de feedback
            feedback_analytics = await self.get_feedback_analytics(30)
            
            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "system_status": system_status,
                "patterns": json.loads(patterns) if format_type == "json" else patterns,
                "feedback_analytics": feedback_analytics,
                "integration_config": self.integration_config
            }
            
            if format_type == "json":
                return json.dumps(export_data, indent=2)
            else:
                return str(export_data)
                
        except Exception as e:
            self.logger.error(f"❌ Erro ao exportar dados: {e}")
            return json.dumps({"error": str(e)})
    
    async def shutdown(self):
        """Encerra a integração de aprendizado"""
        self.is_active = False
        await learning_system.shutdown()
        self.logger.info("🛑 Integração de Aprendizado encerrada")


# Instância global da integração
learning_integration = LearningIntegration()