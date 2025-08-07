#!/usr/bin/env python3
"""
CWB Hub Metrics Aggregator - Sistema de Agregação de Métricas
Melhoria #8 - Dashboard de Monitoramento Avançado
"""

import asyncio
import logging
import time
import psutil
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class MetricType(Enum):
    """Tipos de métricas disponíveis"""
    SYSTEM = "system"
    CACHE = "cache"
    LEARNING = "learning"
    AGENTS = "agents"
    LLM = "llm"
    SESSIONS = "sessions"
    API = "api"
    BUSINESS = "business"

class AlertLevel(Enum):
    """Níveis de alerta"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class MetricPoint:
    """Ponto de métrica individual"""
    timestamp: datetime
    metric_type: MetricType
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str]
    metadata: Dict[str, Any]

@dataclass
class SystemHealth:
    """Status de saúde do sistema"""
    overall_status: str  # healthy, degraded, critical
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    uptime: float
    active_sessions: int
    response_time: float
    error_rate: float
    last_updated: datetime

@dataclass
class Alert:
    """Alerta do sistema"""
    alert_id: str
    level: AlertLevel
    title: str
    description: str
    metric_type: MetricType
    threshold_value: float
    current_value: float
    timestamp: datetime
    resolved: bool
    resolution_time: Optional[datetime]

class MetricsAggregator:
    """
    Agregador de Métricas do CWB Hub
    
    Funcionalidades:
    - Coleta métricas de todos os sistemas
    - Armazena histórico de métricas
    - Calcula estatísticas e tendências
    - Gera alertas automáticos
    - Fornece APIs para dashboard
    - Análise preditiva básica
    """
    
    def __init__(self, retention_hours: int = 168):  # 7 dias
        self.retention_hours = retention_hours
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10000))
        self.current_metrics: Dict[str, MetricPoint] = {}
        self.alerts: List[Alert] = []
        self.alert_thresholds: Dict[str, Dict[str, float]] = {}
        
        # Sistema de saúde
        self.system_health = SystemHealth(
            overall_status="healthy",
            cpu_usage=0.0,
            memory_usage=0.0,
            disk_usage=0.0,
            uptime=0.0,
            active_sessions=0,
            response_time=0.0,
            error_rate=0.0,
            last_updated=datetime.now()
        )
        
        # Configurar thresholds padrão
        self._setup_default_thresholds()
        
        # Estatísticas
        self.collection_stats = {
            "total_metrics_collected": 0,
            "alerts_generated": 0,
            "system_uptime": time.time(),
            "last_collection": None
        }
        
        logger.info("📊 Metrics Aggregator inicializado")
    
    def _setup_default_thresholds(self):
        """Configura thresholds padrão para alertas"""
        self.alert_thresholds = {
            "system": {
                "cpu_usage": 80.0,  # %
                "memory_usage": 85.0,  # %
                "disk_usage": 90.0,  # %
                "response_time": 5000.0  # ms
            },
            "cache": {
                "hit_rate": 50.0,  # % mínimo
                "memory_usage": 100.0  # MB máximo
            },
            "learning": {
                "satisfaction_rate": 70.0,  # % mínimo
                "evolution_success_rate": 80.0  # % mínimo
            },
            "llm": {
                "cost_per_hour": 100.0,  # $ máximo
                "error_rate": 5.0  # % máximo
            },
            "sessions": {
                "average_duration": 1800.0,  # segundos máximo
                "error_rate": 10.0  # % máximo
            }
        }
    
    async def collect_system_metrics(self) -> None:
        """Coleta métricas do sistema operacional"""
        try:
            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            await self._add_metric(
                MetricType.SYSTEM, "cpu_usage", cpu_percent, "%",
                {"component": "system"}, {"cores": psutil.cpu_count()}
            )
            
            # Memória
            memory = psutil.virtual_memory()
            await self._add_metric(
                MetricType.SYSTEM, "memory_usage", memory.percent, "%",
                {"component": "system"}, {"total_gb": memory.total / (1024**3)}
            )
            
            # Disco
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            await self._add_metric(
                MetricType.SYSTEM, "disk_usage", disk_percent, "%",
                {"component": "system"}, {"total_gb": disk.total / (1024**3)}
            )
            
            # Uptime
            uptime = time.time() - self.collection_stats["system_uptime"]
            await self._add_metric(
                MetricType.SYSTEM, "uptime", uptime, "seconds",
                {"component": "system"}, {}
            )
            
            # Atualizar saúde do sistema
            self.system_health.cpu_usage = cpu_percent
            self.system_health.memory_usage = memory.percent
            self.system_health.disk_usage = disk_percent
            self.system_health.uptime = uptime
            self.system_health.last_updated = datetime.now()
            
            # Verificar alertas
            await self._check_system_alerts()
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar métricas do sistema: {e}")
    
    async def collect_cache_metrics(self) -> None:
        """Coleta métricas do sistema de cache"""
        try:
            # Importar cache manager
            from ..utils.advanced_cache import cache_manager
            
            # Obter estatísticas do cache
            cache_stats = cache_manager.get_stats()
            
            # Hit rate
            await self._add_metric(
                MetricType.CACHE, "hit_rate", cache_stats.hit_rate * 100, "%",
                {"component": "cache"}, {"total_requests": cache_stats.total_requests}
            )
            
            # Hits e misses
            await self._add_metric(
                MetricType.CACHE, "hits", cache_stats.hits, "count",
                {"component": "cache"}, {}
            )
            
            await self._add_metric(
                MetricType.CACHE, "misses", cache_stats.misses, "count",
                {"component": "cache"}, {}
            )
            
            # Uso de memória
            await self._add_metric(
                MetricType.CACHE, "memory_usage", cache_stats.memory_usage / (1024*1024), "MB",
                {"component": "cache"}, {}
            )
            
            # Economia de custos
            await self._add_metric(
                MetricType.CACHE, "cost_savings", cache_stats.cost_savings, "$",
                {"component": "cache"}, {}
            )
            
            # Verificar alertas de cache
            await self._check_cache_alerts(cache_stats)
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar métricas de cache: {e}")
    
    async def collect_learning_metrics(self) -> None:
        """Coleta métricas do sistema de aprendizado"""
        try:
            # Importar sistema de aprendizado
            from ..learning.continuous_learning_engine import learning_engine
            from ..learning.agent_evolution import agent_evolution_system
            
            # Insights de aprendizado
            learning_insights = await learning_engine.get_learning_insights()
            learning_metrics = learning_insights.get("learning_metrics", {})
            
            # Total de interações
            await self._add_metric(
                MetricType.LEARNING, "total_interactions", 
                learning_metrics.get("total_interactions", 0), "count",
                {"component": "learning"}, {}
            )
            
            # Satisfação média
            await self._add_metric(
                MetricType.LEARNING, "average_satisfaction", 
                learning_metrics.get("average_satisfaction", 0) * 100, "%",
                {"component": "learning"}, {}
            )
            
            # Padrões identificados
            await self._add_metric(
                MetricType.LEARNING, "patterns_identified", 
                learning_metrics.get("patterns_identified", 0), "count",
                {"component": "learning"}, {}
            )
            
            # Otimizações aplicadas
            await self._add_metric(
                MetricType.LEARNING, "optimizations_applied", 
                learning_metrics.get("optimizations_applied", 0), "count",
                {"component": "learning"}, {}
            )
            
            # Métricas de evolução
            evolution_analytics = await agent_evolution_system.get_evolution_analytics()
            experiment_metrics = evolution_analytics.get("experiment_metrics", {})
            
            # Taxa de sucesso das evoluções
            await self._add_metric(
                MetricType.LEARNING, "evolution_success_rate", 
                experiment_metrics.get("success_rate", 0) * 100, "%",
                {"component": "evolution"}, {}
            )
            
            # Experimentos ativos
            await self._add_metric(
                MetricType.LEARNING, "active_experiments", 
                experiment_metrics.get("active_experiments", 0), "count",
                {"component": "evolution"}, {}
            )
            
            # Verificar alertas de aprendizado
            await self._check_learning_alerts(learning_metrics, experiment_metrics)
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar métricas de aprendizado: {e}")
    
    async def collect_llm_metrics(self) -> None:
        """Coleta métricas do sistema LLM"""
        try:
            # Importar LLM manager
            from ..llm_integration.llm_manager import LLMManager
            
            # Simular métricas LLM (em implementação real, viria do LLM manager)
            # Por enquanto, usar dados simulados baseados no cache
            from ..utils.advanced_cache import cache_manager
            cache_stats = cache_manager.get_stats()
            
            # Estimativa de custos baseada em cache savings
            estimated_cost_per_hour = cache_stats.cost_savings * 10  # Estimativa
            await self._add_metric(
                MetricType.LLM, "cost_per_hour", estimated_cost_per_hour, "$",
                {"component": "llm"}, {}
            )
            
            # Tokens processados (estimativa)
            estimated_tokens = cache_stats.total_requests * 500  # Estimativa
            await self._add_metric(
                MetricType.LLM, "tokens_processed", estimated_tokens, "count",
                {"component": "llm"}, {}
            )
            
            # Taxa de erro (simulada)
            error_rate = max(0, 5 - cache_stats.hit_rate * 5)  # Inversamente proporcional ao hit rate
            await self._add_metric(
                MetricType.LLM, "error_rate", error_rate, "%",
                {"component": "llm"}, {}
            )
            
            # Verificar alertas LLM
            await self._check_llm_alerts(estimated_cost_per_hour, error_rate)
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar métricas LLM: {e}")
    
    async def collect_session_metrics(self) -> None:
        """Coleta métricas de sessões"""
        try:
            # Importar feedback collector
            from ..learning.feedback_collector import feedback_collector
            
            # Analytics de feedback
            feedback_analytics = await feedback_collector.get_feedback_analytics()
            collection_stats = feedback_analytics.get("collection_stats", {})
            
            # Sessões ativas
            active_sessions = feedback_analytics.get("active_sessions", 0)
            await self._add_metric(
                MetricType.SESSIONS, "active_sessions", active_sessions, "count",
                {"component": "sessions"}, {}
            )
            
            # Total de eventos de feedback
            await self._add_metric(
                MetricType.SESSIONS, "total_feedback_events", 
                collection_stats.get("total_feedback_events", 0), "count",
                {"component": "sessions"}, {}
            )
            
            # Rating médio
            await self._add_metric(
                MetricType.SESSIONS, "average_rating", 
                collection_stats.get("average_rating", 0), "rating",
                {"component": "sessions"}, {}
            )
            
            # Atualizar saúde do sistema
            self.system_health.active_sessions = active_sessions
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar métricas de sessões: {e}")
    
    async def _add_metric(self, 
                         metric_type: MetricType, 
                         name: str, 
                         value: float, 
                         unit: str,
                         tags: Dict[str, str], 
                         metadata: Dict[str, Any]) -> None:
        """Adiciona uma métrica ao sistema"""
        
        metric_point = MetricPoint(
            timestamp=datetime.now(),
            metric_type=metric_type,
            metric_name=name,
            value=value,
            unit=unit,
            tags=tags,
            metadata=metadata
        )
        
        # Adicionar ao histórico
        metric_key = f"{metric_type.value}.{name}"
        self.metrics_history[metric_key].append(metric_point)
        self.current_metrics[metric_key] = metric_point
        
        # Atualizar estatísticas
        self.collection_stats["total_metrics_collected"] += 1
        self.collection_stats["last_collection"] = datetime.now()
        
        # Limpar métricas antigas
        await self._cleanup_old_metrics()
    
    async def _cleanup_old_metrics(self) -> None:
        """Remove métricas antigas baseado no retention period"""
        cutoff_time = datetime.now() - timedelta(hours=self.retention_hours)
        
        for metric_key, history in self.metrics_history.items():
            # Remover pontos antigos
            while history and history[0].timestamp < cutoff_time:
                history.popleft()
    
    async def _check_system_alerts(self) -> None:
        """Verifica alertas do sistema"""
        thresholds = self.alert_thresholds.get("system", {})
        
        # CPU
        if self.system_health.cpu_usage > thresholds.get("cpu_usage", 80):
            await self._create_alert(
                AlertLevel.WARNING, "High CPU Usage",
                f"CPU usage is {self.system_health.cpu_usage:.1f}%",
                MetricType.SYSTEM, thresholds["cpu_usage"], self.system_health.cpu_usage
            )
        
        # Memória
        if self.system_health.memory_usage > thresholds.get("memory_usage", 85):
            await self._create_alert(
                AlertLevel.WARNING, "High Memory Usage",
                f"Memory usage is {self.system_health.memory_usage:.1f}%",
                MetricType.SYSTEM, thresholds["memory_usage"], self.system_health.memory_usage
            )
        
        # Disco
        if self.system_health.disk_usage > thresholds.get("disk_usage", 90):
            await self._create_alert(
                AlertLevel.ERROR, "High Disk Usage",
                f"Disk usage is {self.system_health.disk_usage:.1f}%",
                MetricType.SYSTEM, thresholds["disk_usage"], self.system_health.disk_usage
            )
    
    async def _check_cache_alerts(self, cache_stats) -> None:
        """Verifica alertas do cache"""
        thresholds = self.alert_thresholds.get("cache", {})
        
        # Hit rate baixo
        hit_rate_percent = cache_stats.hit_rate * 100
        if hit_rate_percent < thresholds.get("hit_rate", 50):
            await self._create_alert(
                AlertLevel.WARNING, "Low Cache Hit Rate",
                f"Cache hit rate is {hit_rate_percent:.1f}%",
                MetricType.CACHE, thresholds["hit_rate"], hit_rate_percent
            )
    
    async def _check_learning_alerts(self, learning_metrics, experiment_metrics) -> None:
        """Verifica alertas do sistema de aprendizado"""
        thresholds = self.alert_thresholds.get("learning", {})
        
        # Satisfação baixa
        satisfaction_percent = learning_metrics.get("average_satisfaction", 0) * 100
        if satisfaction_percent < thresholds.get("satisfaction_rate", 70):
            await self._create_alert(
                AlertLevel.WARNING, "Low User Satisfaction",
                f"Average satisfaction is {satisfaction_percent:.1f}%",
                MetricType.LEARNING, thresholds["satisfaction_rate"], satisfaction_percent
            )
    
    async def _check_llm_alerts(self, cost_per_hour, error_rate) -> None:
        """Verifica alertas do sistema LLM"""
        thresholds = self.alert_thresholds.get("llm", {})
        
        # Custo alto
        if cost_per_hour > thresholds.get("cost_per_hour", 100):
            await self._create_alert(
                AlertLevel.ERROR, "High LLM Costs",
                f"LLM cost is ${cost_per_hour:.2f}/hour",
                MetricType.LLM, thresholds["cost_per_hour"], cost_per_hour
            )
        
        # Taxa de erro alta
        if error_rate > thresholds.get("error_rate", 5):
            await self._create_alert(
                AlertLevel.ERROR, "High LLM Error Rate",
                f"LLM error rate is {error_rate:.1f}%",
                MetricType.LLM, thresholds["error_rate"], error_rate
            )
    
    async def _create_alert(self, 
                          level: AlertLevel, 
                          title: str, 
                          description: str,
                          metric_type: MetricType, 
                          threshold: float, 
                          current_value: float) -> None:
        """Cria um novo alerta"""
        
        alert = Alert(
            alert_id=f"alert_{int(time.time())}_{metric_type.value}",
            level=level,
            title=title,
            description=description,
            metric_type=metric_type,
            threshold_value=threshold,
            current_value=current_value,
            timestamp=datetime.now(),
            resolved=False,
            resolution_time=None
        )
        
        self.alerts.append(alert)
        self.collection_stats["alerts_generated"] += 1
        
        logger.warning(f"🚨 Alerta gerado: {title} - {description}")
    
    async def collect_all_metrics(self) -> None:
        """Coleta todas as métricas de todos os sistemas"""
        try:
            await asyncio.gather(
                self.collect_system_metrics(),
                self.collect_cache_metrics(),
                self.collect_learning_metrics(),
                self.collect_llm_metrics(),
                self.collect_session_metrics()
            )
            
            # Atualizar status geral de saúde
            await self._update_overall_health()
            
        except Exception as e:
            logger.error(f"❌ Erro ao coletar métricas: {e}")
    
    async def _update_overall_health(self) -> None:
        """Atualiza status geral de saúde do sistema"""
        # Determinar status baseado em métricas críticas
        critical_issues = len([a for a in self.alerts if a.level == AlertLevel.CRITICAL and not a.resolved])
        error_issues = len([a for a in self.alerts if a.level == AlertLevel.ERROR and not a.resolved])
        warning_issues = len([a for a in self.alerts if a.level == AlertLevel.WARNING and not a.resolved])
        
        if critical_issues > 0:
            self.system_health.overall_status = "critical"
        elif error_issues > 0:
            self.system_health.overall_status = "degraded"
        elif warning_issues > 2:
            self.system_health.overall_status = "degraded"
        else:
            self.system_health.overall_status = "healthy"
        
        # Calcular taxa de erro geral
        total_alerts = len([a for a in self.alerts if not a.resolved])
        self.system_health.error_rate = min(100, total_alerts * 5)  # Estimativa
        
        # Tempo de resposta médio (simulado)
        self.system_health.response_time = 1000 + (self.system_health.cpu_usage * 10)  # ms
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Retorna métricas atuais"""
        return {
            "system_health": asdict(self.system_health),
            "current_metrics": {
                key: asdict(metric) for key, metric in self.current_metrics.items()
            },
            "collection_stats": self.collection_stats.copy(),
            "active_alerts": len([a for a in self.alerts if not a.resolved])
        }
    
    def get_historical_metrics(self, 
                             metric_type: Optional[MetricType] = None,
                             hours: int = 24) -> Dict[str, List[Dict[str, Any]]]:
        """Retorna métricas históricas"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        historical = {}
        
        for metric_key, history in self.metrics_history.items():
            if metric_type and not metric_key.startswith(metric_type.value):
                continue
            
            # Filtrar por tempo
            filtered_history = [
                asdict(point) for point in history 
                if point.timestamp >= cutoff_time
            ]
            
            if filtered_history:
                historical[metric_key] = filtered_history
        
        return historical
    
    def get_alerts(self, resolved: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Retorna alertas"""
        alerts = self.alerts
        
        if resolved is not None:
            alerts = [a for a in alerts if a.resolved == resolved]
        
        return [asdict(alert) for alert in alerts]
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve um alerta"""
        for alert in self.alerts:
            if alert.alert_id == alert_id and not alert.resolved:
                alert.resolved = True
                alert.resolution_time = datetime.now()
                logger.info(f"✅ Alerta resolvido: {alert_id}")
                return True
        
        return False
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas resumidas"""
        return {
            "system_health": self.system_health.overall_status,
            "total_metrics": self.collection_stats["total_metrics_collected"],
            "active_alerts": len([a for a in self.alerts if not a.resolved]),
            "uptime_hours": (time.time() - self.collection_stats["system_uptime"]) / 3600,
            "cache_hit_rate": self.current_metrics.get("cache.hit_rate", {}).get("value", 0),
            "average_satisfaction": self.current_metrics.get("learning.average_satisfaction", {}).get("value", 0),
            "active_sessions": self.system_health.active_sessions,
            "cpu_usage": self.system_health.cpu_usage,
            "memory_usage": self.system_health.memory_usage
        }

# Instância global do agregador de métricas
metrics_aggregator = MetricsAggregator()

if __name__ == "__main__":
    # Teste básico do agregador
    async def test_metrics_aggregator():
        print("🧪 Testando Agregador de Métricas...")
        
        # Coletar métricas
        await metrics_aggregator.collect_all_metrics()
        
        # Obter métricas atuais
        current = metrics_aggregator.get_current_metrics()
        print(f"📊 Status do sistema: {current['system_health']['overall_status']}")
        print(f"💾 CPU: {current['system_health']['cpu_usage']:.1f}%")
        print(f"🧠 Memória: {current['system_health']['memory_usage']:.1f}%")
        
        # Estatísticas resumidas
        summary = metrics_aggregator.get_summary_stats()
        print(f"📈 Resumo: {summary}")
        
        # Alertas
        alerts = metrics_aggregator.get_alerts(resolved=False)
        print(f"🚨 Alertas ativos: {len(alerts)}")
        
        print("✅ Teste concluído!")
    
    asyncio.run(test_metrics_aggregator())