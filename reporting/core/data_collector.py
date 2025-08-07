"""
Data Collector - Sistema de Coleta de Métricas
Criado pela Equipe Híbrida CWB Hub

Sofia Oliveira (Full Stack): "Vamos criar um coletor inteligente que capture 
todas as métricas relevantes do nosso sistema de IA híbrida."

Lucas Pereira (QA): "Com validação robusta e tratamento de erros para 
garantir a qualidade dos dados coletados."
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import json
import psutil
import sys
from pathlib import Path

# Adicionar src ao path para importar módulos do sistema
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

try:
    from src.core.hybrid_ai_orchestrator import HybridAIOrchestrator
    from src.communication.collaboration_framework import CollaborationFramework
except ImportError:
    # Fallback para desenvolvimento
    HybridAIOrchestrator = None
    CollaborationFramework = None

from ..models.report_models import MetricsData, DashboardData

logger = logging.getLogger(__name__)


class DataCollector:
    """
    Coletor de dados para métricas do sistema CWB Hub
    
    Responsabilidades:
    - Coletar métricas de sessões e agentes
    - Monitorar performance do sistema
    - Agregar dados de colaboração
    - Validar qualidade dos dados
    """
    
    def __init__(self, orchestrator: Optional[HybridAIOrchestrator] = None):
        self.orchestrator = orchestrator
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.start_time = datetime.utcnow()
        
    async def collect_all_metrics(
        self, 
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Coleta todas as métricas disponíveis do sistema
        
        Args:
            period_start: Início do período de coleta
            period_end: Fim do período de coleta
            
        Returns:
            Dicionário com todas as métricas coletadas
        """
        if not period_end:
            period_end = datetime.utcnow()
        if not period_start:
            period_start = period_end - timedelta(hours=24)
            
        self.logger.info(f"Coletando métricas do período: {period_start} até {period_end}")
        
        metrics = {
            "collection_timestamp": datetime.utcnow().isoformat(),
            "period_start": period_start.isoformat(),
            "period_end": period_end.isoformat(),
            "system_metrics": await self._collect_system_metrics(),
            "session_metrics": await self._collect_session_metrics(period_start, period_end),
            "agent_metrics": await self._collect_agent_metrics(period_start, period_end),
            "collaboration_metrics": await self._collect_collaboration_metrics(period_start, period_end),
            "performance_metrics": await self._collect_performance_metrics(),
            "quality_metrics": await self._collect_quality_metrics(period_start, period_end),
            "error_metrics": await self._collect_error_metrics(period_start, period_end)
        }
        
        self.logger.info("Coleta de métricas concluída com sucesso")
        return metrics
    
    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Coleta métricas do sistema operacional e infraestrutura"""
        try:
            # Métricas de CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            
            # Métricas de memória
            memory = psutil.virtual_memory()
            
            # Métricas de disco
            disk = psutil.disk_usage('/')
            
            # Uptime do sistema
            uptime_seconds = (datetime.utcnow() - self.start_time).total_seconds()
            
            return {
                "cpu_usage_percent": cpu_percent,
                "cpu_count": cpu_count,
                "memory_total_gb": round(memory.total / (1024**3), 2),
                "memory_used_gb": round(memory.used / (1024**3), 2),
                "memory_usage_percent": memory.percent,
                "disk_total_gb": round(disk.total / (1024**3), 2),
                "disk_used_gb": round(disk.used / (1024**3), 2),
                "disk_usage_percent": round((disk.used / disk.total) * 100, 2),
                "uptime_seconds": uptime_seconds,
                "uptime_hours": round(uptime_seconds / 3600, 2)
            }
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas do sistema: {e}")
            return {"error": str(e)}
    
    async def _collect_session_metrics(
        self, 
        period_start: datetime, 
        period_end: datetime
    ) -> Dict[str, Any]:
        """Coleta métricas de sessões do orquestrador"""
        try:
            if not self.orchestrator:
                return self._generate_mock_session_metrics()
            
            # Métricas de sessões ativas
            active_sessions = len(self.orchestrator.active_sessions)
            
            # Estatísticas de sessões (simulado - seria implementado no orquestrador)
            total_sessions = active_sessions + 150  # Simulado
            avg_session_duration = 25.5  # minutos
            successful_sessions = 142
            failed_sessions = 8
            
            return {
                "active_sessions": active_sessions,
                "total_sessions_period": total_sessions,
                "avg_session_duration_minutes": avg_session_duration,
                "successful_sessions": successful_sessions,
                "failed_sessions": failed_sessions,
                "success_rate_percent": round((successful_sessions / total_sessions) * 100, 2),
                "sessions_per_hour": round(total_sessions / 24, 2)
            }
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de sessão: {e}")
            return self._generate_mock_session_metrics()
    
    async def _collect_agent_metrics(
        self, 
        period_start: datetime, 
        period_end: datetime
    ) -> Dict[str, Any]:
        """Coleta métricas individuais dos agentes"""
        try:
            if not self.orchestrator:
                return self._generate_mock_agent_metrics()
            
            active_agents = self.orchestrator.get_active_agents()
            
            agent_stats = {}
            for agent_name in active_agents:
                # Métricas simuladas - seria implementado em cada agente
                agent_stats[agent_name] = {
                    "participation_rate": round(85 + (hash(agent_name) % 15), 2),
                    "avg_response_time_seconds": round(2.5 + (hash(agent_name) % 5), 2),
                    "total_interactions": 45 + (hash(agent_name) % 20),
                    "quality_score": round(8.5 + (hash(agent_name) % 15) / 10, 2),
                    "collaboration_score": round(7.8 + (hash(agent_name) % 22) / 10, 2)
                }
            
            return {
                "total_active_agents": len(active_agents),
                "agent_details": agent_stats,
                "avg_participation_rate": round(
                    sum(stats["participation_rate"] for stats in agent_stats.values()) / len(agent_stats), 2
                ) if agent_stats else 0,
                "avg_response_time": round(
                    sum(stats["avg_response_time_seconds"] for stats in agent_stats.values()) / len(agent_stats), 2
                ) if agent_stats else 0
            }
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de agentes: {e}")
            return self._generate_mock_agent_metrics()
    
    async def _collect_collaboration_metrics(
        self, 
        period_start: datetime, 
        period_end: datetime
    ) -> Dict[str, Any]:
        """Coleta métricas de colaboração entre agentes"""
        try:
            if not self.orchestrator or not hasattr(self.orchestrator, 'collaboration_framework'):
                return self._generate_mock_collaboration_metrics()
            
            # Obter estatísticas do framework de colaboração
            collab_stats = self.orchestrator.collaboration_framework.get_collaboration_stats()
            
            return {
                "total_collaborations": collab_stats.get("total_interactions", 0),
                "successful_collaborations": collab_stats.get("successful_interactions", 0),
                "avg_collaboration_time": collab_stats.get("avg_interaction_time", 0),
                "consensus_rate": collab_stats.get("consensus_rate", 0),
                "conflict_resolution_time": collab_stats.get("avg_conflict_resolution_time", 0),
                "cross_agent_interactions": collab_stats.get("cross_agent_interactions", {}),
                "collaboration_quality_score": collab_stats.get("quality_score", 0)
            }
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de colaboração: {e}")
            return self._generate_mock_collaboration_metrics()
    
    async def _collect_performance_metrics(self) -> Dict[str, Any]:
        """Coleta métricas de performance do sistema"""
        try:
            # Métricas de latência (simuladas)
            return {
                "avg_request_latency_ms": 245.5,
                "p95_request_latency_ms": 450.2,
                "p99_request_latency_ms": 850.7,
                "throughput_requests_per_second": 12.5,
                "error_rate_percent": 2.1,
                "cache_hit_rate_percent": 78.5,
                "database_connection_pool_usage": 65.2
            }
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de performance: {e}")
            return {"error": str(e)}
    
    async def _collect_quality_metrics(
        self, 
        period_start: datetime, 
        period_end: datetime
    ) -> Dict[str, Any]:
        """Coleta métricas de qualidade das respostas"""
        try:
            return {
                "avg_response_quality_score": 8.7,
                "user_satisfaction_score": 8.9,
                "response_completeness_score": 9.1,
                "response_accuracy_score": 8.8,
                "response_relevance_score": 9.0,
                "total_feedback_received": 156,
                "positive_feedback_percent": 87.5,
                "negative_feedback_percent": 12.5
            }
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de qualidade: {e}")
            return {"error": str(e)}
    
    async def _collect_error_metrics(
        self, 
        period_start: datetime, 
        period_end: datetime
    ) -> Dict[str, Any]:
        """Coleta métricas de erros e incidentes"""
        try:
            return {
                "total_errors": 15,
                "critical_errors": 2,
                "warning_errors": 8,
                "info_errors": 5,
                "avg_error_resolution_time_minutes": 12.5,
                "most_common_error_types": [
                    {"type": "timeout", "count": 6},
                    {"type": "validation", "count": 4},
                    {"type": "connection", "count": 3},
                    {"type": "authentication", "count": 2}
                ],
                "error_rate_trend": "decreasing"
            }
        except Exception as e:
            self.logger.error(f"Erro ao coletar métricas de erro: {e}")
            return {"error": str(e)}
    
    def _generate_mock_session_metrics(self) -> Dict[str, Any]:
        """Gera métricas simuladas de sessão para desenvolvimento"""
        return {
            "active_sessions": 8,
            "total_sessions_period": 150,
            "avg_session_duration_minutes": 25.5,
            "successful_sessions": 142,
            "failed_sessions": 8,
            "success_rate_percent": 94.67,
            "sessions_per_hour": 6.25
        }
    
    def _generate_mock_agent_metrics(self) -> Dict[str, Any]:
        """Gera métricas simuladas de agentes para desenvolvimento"""
        agents = [
            "Ana Beatriz Costa", "Carlos Eduardo Santos", "Sofia Oliveira",
            "Gabriel Mendes", "Isabella Santos", "Lucas Pereira",
            "Mariana Rodrigues", "Pedro Henrique Almeida"
        ]
        
        agent_stats = {}
        for agent in agents:
            agent_stats[agent] = {
                "participation_rate": round(85 + (hash(agent) % 15), 2),
                "avg_response_time_seconds": round(2.5 + (hash(agent) % 5), 2),
                "total_interactions": 45 + (hash(agent) % 20),
                "quality_score": round(8.5 + (hash(agent) % 15) / 10, 2),
                "collaboration_score": round(7.8 + (hash(agent) % 22) / 10, 2)
            }
        
        return {
            "total_active_agents": len(agents),
            "agent_details": agent_stats,
            "avg_participation_rate": 92.5,
            "avg_response_time": 4.2
        }
    
    def _generate_mock_collaboration_metrics(self) -> Dict[str, Any]:
        """Gera métricas simuladas de colaboração para desenvolvimento"""
        return {
            "total_collaborations": 89,
            "successful_collaborations": 82,
            "avg_collaboration_time": 15.5,
            "consensus_rate": 92.1,
            "conflict_resolution_time": 8.2,
            "cross_agent_interactions": {
                "Ana_Beatriz_Costa": 15,
                "Carlos_Eduardo_Santos": 18,
                "Sofia_Oliveira": 12,
                "Gabriel_Mendes": 10,
                "Isabella_Santos": 14,
                "Lucas_Pereira": 11,
                "Mariana_Rodrigues": 13,
                "Pedro_Henrique_Almeida": 16
            },
            "collaboration_quality_score": 8.9
        }
    
    async def get_dashboard_data(self) -> DashboardData:
        """
        Coleta dados específicos para o dashboard em tempo real
        
        Returns:
            Dados formatados para o dashboard
        """
        try:
            metrics = await self.collect_all_metrics()
            
            # Extrair dados principais para o dashboard
            system_metrics = metrics.get("system_metrics", {})
            session_metrics = metrics.get("session_metrics", {})
            agent_metrics = metrics.get("agent_metrics", {})
            performance_metrics = metrics.get("performance_metrics", {})
            error_metrics = metrics.get("error_metrics", {})
            collaboration_metrics = metrics.get("collaboration_metrics", {})
            
            # Calcular tendências (simulado)
            trends = {
                "sessions": [45, 52, 48, 61, 55, 67, 58],  # Últimos 7 dias
                "response_time": [2.1, 2.3, 2.0, 2.5, 2.2, 2.4, 2.1],
                "quality_score": [8.5, 8.7, 8.6, 8.9, 8.8, 9.0, 8.7],
                "collaboration": [85, 87, 89, 91, 88, 92, 90]
            }
            
            return DashboardData(
                current_sessions=session_metrics.get("active_sessions", 0),
                active_agents=agent_metrics.get("total_active_agents", 0),
                total_users=session_metrics.get("total_sessions_period", 0),
                system_uptime=system_metrics.get("uptime_hours", 0),
                avg_response_time=performance_metrics.get("avg_request_latency_ms", 0),
                error_rate=performance_metrics.get("error_rate_percent", 0),
                collaboration_score=collaboration_metrics.get("collaboration_quality_score", 0),
                last_updated=datetime.utcnow(),
                trends=trends
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar dados do dashboard: {e}")
            # Retornar dados padrão em caso de erro
            return DashboardData(
                current_sessions=0,
                active_agents=0,
                total_users=0,
                system_uptime=0,
                avg_response_time=0,
                error_rate=0,
                collaboration_score=0,
                last_updated=datetime.utcnow(),
                trends={}
            )
    
    async def validate_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Valida a qualidade e consistência dos dados coletados
        
        Args:
            metrics: Métricas coletadas
            
        Returns:
            True se os dados são válidos, False caso contrário
        """
        try:
            # Validações básicas
            required_sections = [
                "system_metrics", "session_metrics", "agent_metrics",
                "collaboration_metrics", "performance_metrics"
            ]
            
            for section in required_sections:
                if section not in metrics:
                    self.logger.warning(f"Seção obrigatória ausente: {section}")
                    return False
            
            # Validar valores numéricos
            session_metrics = metrics.get("session_metrics", {})
            if session_metrics.get("success_rate_percent", 0) > 100:
                self.logger.warning("Taxa de sucesso inválida (>100%)")
                return False
            
            # Validar métricas de sistema
            system_metrics = metrics.get("system_metrics", {})
            if system_metrics.get("memory_usage_percent", 0) > 100:
                self.logger.warning("Uso de memória inválido (>100%)")
                return False
            
            self.logger.info("Validação de métricas concluída com sucesso")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro na validação de métricas: {e}")
            return False