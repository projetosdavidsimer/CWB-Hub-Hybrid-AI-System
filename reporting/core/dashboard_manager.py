"""
Dashboard Manager - Interface de Dashboard para Relatórios
Criado pela Equipe Híbrida CWB Hub

Isabella Santos (UX/UI): "Dashboard intuitivo e responsivo que transforma 
dados complexos em insights visuais claros e acionáveis."

Sofia Oliveira (Full Stack): "Interface web moderna com atualizações em 
tempo real e interatividade avançada."
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path
import uuid

from .data_collector import DataCollector
from .report_engine import ReportEngine
from .scheduler import ReportScheduler
from .error_handler import error_handler, ErrorSeverity, ErrorCategory, handle_errors
from ..models.report_models import ReportType, ReportFormat, ReportFrequency

logger = logging.getLogger(__name__)


class DashboardManager:
    """
    Gerenciador de dashboard para visualização e gestão de relatórios
    
    Responsabilidades:
    - Gerar dados para dashboard em tempo real
    - Gerenciar widgets e métricas
    - Fornecer APIs para interface web
    - Controlar atualizações automáticas
    - Integrar com sistema de relatórios
    """
    
    def __init__(
        self,
        data_collector: Optional[DataCollector] = None,
        report_engine: Optional[ReportEngine] = None,
        scheduler: Optional[ReportScheduler] = None
    ):
        self.data_collector = data_collector or DataCollector()
        self.report_engine = report_engine or ReportEngine()
        self.scheduler = scheduler
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Cache de dados do dashboard
        self.dashboard_cache = {}
        self.cache_ttl = 300  # 5 minutos
        self.last_cache_update = None
        
        # Configurações de widgets
        self.widget_configs = self._get_default_widget_configs()
        
        # Sessões ativas do dashboard
        self.active_sessions = {}
        
        self.logger.info("Dashboard Manager inicializado")
    
    @handle_errors(severity=ErrorSeverity.MEDIUM, category=ErrorCategory.SYSTEM)
    async def get_dashboard_data(self, refresh_cache: bool = False) -> Dict[str, Any]:
        """
        Obtém dados completos do dashboard
        
        Args:
            refresh_cache: Forçar atualização do cache
            
        Returns:
            Dados estruturados do dashboard
        """
        
        # Verificar cache
        if not refresh_cache and self._is_cache_valid():
            return self.dashboard_cache
        
        self.logger.info("Atualizando dados do dashboard")
        
        try:
            # Coletar dados base
            metrics = await self.data_collector.collect_all_metrics()
            dashboard_data = await self.data_collector.get_dashboard_data()
            
            # Dados do scheduler (se disponível)
            scheduler_data = {}
            if self.scheduler:
                scheduler_data = self.scheduler.get_scheduler_status()
            
            # Métricas de erro
            error_metrics = error_handler.get_error_metrics()
            error_summary = error_handler.get_error_summary()
            
            # Dados de relatórios recentes
            recent_reports = await self._get_recent_reports()
            
            # Compilar dados do dashboard
            dashboard = {
                "timestamp": datetime.utcnow().isoformat(),
                "system_status": self._get_system_status(metrics, error_summary),
                "key_metrics": self._get_key_metrics(dashboard_data),
                "charts_data": self._prepare_charts_data(metrics),
                "recent_activity": self._get_recent_activity(recent_reports),
                "scheduler_status": scheduler_data,
                "error_summary": error_summary,
                "widgets": self._get_widgets_data(metrics, dashboard_data),
                "alerts": self._get_active_alerts(error_summary),
                "performance_indicators": self._get_performance_indicators(metrics)
            }
            
            # Atualizar cache
            self.dashboard_cache = dashboard
            self.last_cache_update = datetime.utcnow()
            
            return dashboard
            
        except Exception as e:
            self.logger.error(f"Erro ao obter dados do dashboard: {e}")
            # Retornar dados em cache se disponível
            if self.dashboard_cache:
                return self.dashboard_cache
            raise
    
    def _is_cache_valid(self) -> bool:
        """Verifica se o cache ainda é válido"""
        if not self.last_cache_update or not self.dashboard_cache:
            return False
        
        age = (datetime.utcnow() - self.last_cache_update).total_seconds()
        return age < self.cache_ttl
    
    def _get_system_status(self, metrics: Dict[str, Any], error_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Determina status geral do sistema"""
        
        system_metrics = metrics.get("system_metrics", {})
        session_metrics = metrics.get("session_metrics", {})
        
        # Calcular score de saúde
        health_score = error_summary.get("system_health_score", 100)
        
        # Determinar status
        if health_score >= 90:
            status = "healthy"
            color = "green"
        elif health_score >= 70:
            status = "warning"
            color = "yellow"
        else:
            status = "critical"
            color = "red"
        
        return {
            "status": status,
            "color": color,
            "health_score": health_score,
            "uptime_hours": system_metrics.get("uptime_hours", 0),
            "active_sessions": session_metrics.get("active_sessions", 0),
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def _get_key_metrics(self, dashboard_data) -> List[Dict[str, Any]]:
        """Obtém métricas-chave para cards principais"""
        
        return [
            {
                "id": "active_sessions",
                "title": "Sessões Ativas",
                "value": dashboard_data.current_sessions,
                "unit": "",
                "trend": "stable",
                "color": "blue",
                "icon": "users"
            },
            {
                "id": "active_agents",
                "title": "Agentes Ativos",
                "value": dashboard_data.active_agents,
                "unit": "",
                "trend": "stable",
                "color": "green",
                "icon": "cpu"
            },
            {
                "id": "response_time",
                "title": "Tempo de Resposta",
                "value": round(dashboard_data.avg_response_time, 1),
                "unit": "ms",
                "trend": "improving",
                "color": "orange",
                "icon": "clock"
            },
            {
                "id": "collaboration_score",
                "title": "Score de Colaboração",
                "value": round(dashboard_data.collaboration_score, 1),
                "unit": "/10",
                "trend": "stable",
                "color": "purple",
                "icon": "team"
            },
            {
                "id": "error_rate",
                "title": "Taxa de Erro",
                "value": round(dashboard_data.error_rate, 2),
                "unit": "%",
                "trend": "decreasing",
                "color": "red" if dashboard_data.error_rate > 5 else "green",
                "icon": "alert"
            },
            {
                "id": "system_uptime",
                "title": "Uptime do Sistema",
                "value": round(dashboard_data.system_uptime, 1),
                "unit": "h",
                "trend": "stable",
                "color": "cyan",
                "icon": "server"
            }
        ]
    
    def _prepare_charts_data(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara dados para gráficos do dashboard"""
        
        # Dados de tendência (simulados - em produção viriam do banco)
        hours = [(datetime.now() - timedelta(hours=i)).strftime("%H:%M") for i in range(23, -1, -1)]
        
        return {
            "sessions_trend": {
                "labels": hours,
                "datasets": [{
                    "label": "Sessões por Hora",
                    "data": [45, 52, 48, 61, 55, 67, 58, 72, 65, 59, 63, 68, 
                            71, 66, 62, 69, 74, 70, 65, 61, 58, 55, 52, 48],
                    "borderColor": "#3B82F6",
                    "backgroundColor": "rgba(59, 130, 246, 0.1)"
                }]
            },
            "response_time_trend": {
                "labels": hours,
                "datasets": [{
                    "label": "Tempo de Resposta (ms)",
                    "data": [245, 230, 255, 240, 235, 250, 245, 238, 242, 248,
                            252, 246, 241, 239, 244, 247, 243, 240, 238, 245,
                            250, 248, 246, 244],
                    "borderColor": "#F59E0B",
                    "backgroundColor": "rgba(245, 158, 11, 0.1)"
                }]
            },
            "agent_activity": {
                "labels": [
                    "Ana Beatriz", "Carlos Eduardo", "Sofia", "Gabriel",
                    "Isabella", "Lucas", "Mariana", "Pedro"
                ],
                "datasets": [{
                    "label": "Atividade dos Agentes",
                    "data": [95, 88, 92, 85, 90, 87, 89, 91],
                    "backgroundColor": [
                        "#EF4444", "#F59E0B", "#10B981", "#3B82F6",
                        "#8B5CF6", "#F97316", "#06B6D4", "#84CC16"
                    ]
                }]
            },
            "error_distribution": {
                "labels": ["Sistema", "Dados", "Templates", "Email", "Outros"],
                "datasets": [{
                    "label": "Distribuição de Erros",
                    "data": [5, 3, 2, 1, 2],
                    "backgroundColor": [
                        "#EF4444", "#F59E0B", "#10B981", "#3B82F6", "#8B5CF6"
                    ]
                }]
            }
        }
    
    def _get_recent_activity(self, recent_reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Obtém atividades recentes do sistema"""
        
        activities = []
        
        # Adicionar relatórios recentes
        for report in recent_reports[:5]:
            activities.append({
                "id": str(uuid.uuid4()),
                "type": "report_generated",
                "title": f"Relatório {report['type']} gerado",
                "description": f"Formato: {', '.join(report['formats'])}",
                "timestamp": report["timestamp"],
                "icon": "file-text",
                "color": "blue"
            })
        
        # Adicionar eventos do sistema (simulados)
        activities.extend([
            {
                "id": str(uuid.uuid4()),
                "type": "system_event",
                "title": "Sistema iniciado",
                "description": "Todos os agentes carregados com sucesso",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "icon": "power",
                "color": "green"
            },
            {
                "id": str(uuid.uuid4()),
                "type": "alert",
                "title": "Alerta de performance",
                "description": "Tempo de resposta acima do normal",
                "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
                "icon": "alert-triangle",
                "color": "orange"
            }
        ])
        
        # Ordenar por timestamp
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return activities[:10]  # Últimas 10 atividades
    
    async def _get_recent_reports(self) -> List[Dict[str, Any]]:
        """Obtém relatórios gerados recentemente"""
        
        # Em produção, isso viria do banco de dados
        # Por enquanto, retornar dados simulados
        
        recent_reports = [
            {
                "id": "exec_001",
                "type": "executive_summary",
                "formats": ["html", "pdf"],
                "timestamp": (datetime.now() - timedelta(hours=1)).isoformat(),
                "status": "completed",
                "duration": 12.5
            },
            {
                "id": "agent_002",
                "type": "agent_performance",
                "formats": ["html"],
                "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                "status": "completed",
                "duration": 8.2
            },
            {
                "id": "collab_003",
                "type": "collaboration_stats",
                "formats": ["html", "pdf"],
                "timestamp": (datetime.now() - timedelta(hours=6)).isoformat(),
                "status": "completed",
                "duration": 15.1
            }
        ]
        
        return recent_reports
    
    def _get_widgets_data(self, metrics: Dict[str, Any], dashboard_data) -> List[Dict[str, Any]]:
        """Obtém dados para widgets do dashboard"""
        
        widgets = []
        
        for widget_id, config in self.widget_configs.items():
            if config["enabled"]:
                widget_data = self._generate_widget_data(widget_id, config, metrics, dashboard_data)
                widgets.append(widget_data)
        
        return widgets
    
    def _generate_widget_data(
        self, 
        widget_id: str, 
        config: Dict[str, Any], 
        metrics: Dict[str, Any], 
        dashboard_data
    ) -> Dict[str, Any]:
        """Gera dados para um widget específico"""
        
        base_widget = {
            "id": widget_id,
            "title": config["title"],
            "type": config["type"],
            "size": config["size"],
            "position": config["position"]
        }
        
        if widget_id == "system_overview":
            base_widget["data"] = {
                "cpu_usage": metrics.get("system_metrics", {}).get("cpu_usage_percent", 0),
                "memory_usage": metrics.get("system_metrics", {}).get("memory_usage_percent", 0),
                "disk_usage": metrics.get("system_metrics", {}).get("disk_usage_percent", 0),
                "uptime": metrics.get("system_metrics", {}).get("uptime_hours", 0)
            }
        
        elif widget_id == "agent_status":
            agent_metrics = metrics.get("agent_metrics", {})
            base_widget["data"] = {
                "total_agents": agent_metrics.get("total_active_agents", 0),
                "avg_response_time": agent_metrics.get("avg_response_time", 0),
                "participation_rate": agent_metrics.get("avg_participation_rate", 0)
            }
        
        elif widget_id == "recent_errors":
            recent_errors = error_handler.get_recent_errors(24)
            base_widget["data"] = {
                "total_errors": len(recent_errors),
                "critical_errors": len([e for e in recent_errors if e.severity.value == "critical"]),
                "error_trend": error_handler.get_error_summary().get("error_trend", "stable")
            }
        
        return base_widget
    
    def _get_active_alerts(self, error_summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Obtém alertas ativos do sistema"""
        
        alerts = []
        
        # Alertas baseados em métricas de erro
        if error_summary.get("critical_errors_24h", 0) > 0:
            alerts.append({
                "id": "critical_errors",
                "type": "critical",
                "title": "Erros Críticos Detectados",
                "message": f"{error_summary['critical_errors_24h']} erros críticos nas últimas 24h",
                "timestamp": datetime.utcnow().isoformat(),
                "action_required": True
            })
        
        if error_summary.get("system_health_score", 100) < 70:
            alerts.append({
                "id": "low_health",
                "type": "warning",
                "title": "Score de Saúde Baixo",
                "message": f"Score atual: {error_summary['system_health_score']:.1f}%",
                "timestamp": datetime.utcnow().isoformat(),
                "action_required": True
            })
        
        return alerts
    
    def _get_performance_indicators(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Obtém indicadores de performance"""
        
        session_metrics = metrics.get("session_metrics", {})
        performance_metrics = metrics.get("performance_metrics", {})
        
        return {
            "throughput": {
                "value": session_metrics.get("sessions_per_hour", 0),
                "unit": "sessões/hora",
                "target": 50,
                "status": "good" if session_metrics.get("sessions_per_hour", 0) >= 50 else "warning"
            },
            "availability": {
                "value": 99.8,  # Seria calculado baseado em uptime real
                "unit": "%",
                "target": 99.5,
                "status": "excellent"
            },
            "response_time": {
                "value": performance_metrics.get("avg_request_latency_ms", 0),
                "unit": "ms",
                "target": 500,
                "status": "good" if performance_metrics.get("avg_request_latency_ms", 0) <= 500 else "warning"
            },
            "error_rate": {
                "value": performance_metrics.get("error_rate_percent", 0),
                "unit": "%",
                "target": 1,
                "status": "good" if performance_metrics.get("error_rate_percent", 0) <= 1 else "critical"
            }
        }
    
    def _get_default_widget_configs(self) -> Dict[str, Dict[str, Any]]:
        """Configurações padrão dos widgets"""
        
        return {
            "system_overview": {
                "title": "Visão Geral do Sistema",
                "type": "metrics_card",
                "size": "medium",
                "position": {"row": 0, "col": 0},
                "enabled": True
            },
            "agent_status": {
                "title": "Status dos Agentes",
                "type": "agent_grid",
                "size": "large",
                "position": {"row": 0, "col": 1},
                "enabled": True
            },
            "sessions_chart": {
                "title": "Tendência de Sessões",
                "type": "line_chart",
                "size": "large",
                "position": {"row": 1, "col": 0},
                "enabled": True
            },
            "recent_errors": {
                "title": "Erros Recentes",
                "type": "error_list",
                "size": "medium",
                "position": {"row": 1, "col": 1},
                "enabled": True
            },
            "performance_indicators": {
                "title": "Indicadores de Performance",
                "type": "kpi_grid",
                "size": "large",
                "position": {"row": 2, "col": 0},
                "enabled": True
            }
        }
    
    async def generate_dashboard_html(self, custom_config: Optional[Dict[str, Any]] = None) -> str:
        """
        Gera HTML completo do dashboard
        
        Args:
            custom_config: Configurações customizadas do dashboard
            
        Returns:
            HTML do dashboard
        """
        
        # Obter dados do dashboard
        dashboard_data = await self.get_dashboard_data()
        
        # Template HTML do dashboard
        html_template = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard CWB Hub - Sistema de Relatórios</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://unpkg.com/feather-icons"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f8fafc;
            color: #334155;
            line-height: 1.6;
        }
        
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header-title h1 {
            font-size: 2rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .header-subtitle {
            opacity: 0.9;
            font-size: 1rem;
        }
        
        .header-status {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        
        .status-indicator {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.5rem 1rem;
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            font-size: 0.9rem;
        }
        
        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
        }
        
        .dashboard-container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .metric-card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-left: 4px solid;
            transition: transform 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
        }
        
        .metric-header {
            display: flex;
            justify-content: between;
            align-items: center;
            margin-bottom: 1rem;
        }
        
        .metric-icon {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .metric-label {
            color: #64748b;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .charts-section {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 2rem;
            margin-bottom: 2rem;
        }
        
        .chart-container {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .chart-title {
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
            color: #1e293b;
        }
        
        .activity-section {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        
        .activity-item {
            display: flex;
            align-items: center;
            padding: 1rem 0;
            border-bottom: 1px solid #f1f5f9;
        }
        
        .activity-item:last-child {
            border-bottom: none;
        }
        
        .activity-icon {
            width: 32px;
            height: 32px;
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 1rem;
        }
        
        .activity-content {
            flex: 1;
        }
        
        .activity-title {
            font-weight: 600;
            margin-bottom: 0.25rem;
        }
        
        .activity-description {
            color: #64748b;
            font-size: 0.9rem;
        }
        
        .activity-time {
            color: #94a3b8;
            font-size: 0.8rem;
        }
        
        .alerts-section {
            margin-top: 2rem;
        }
        
        .alert {
            background: white;
            border-left: 4px solid #ef4444;
            padding: 1rem 1.5rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 1rem;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        }
        
        .alert.warning {
            border-left-color: #f59e0b;
        }
        
        .alert-title {
            font-weight: 600;
            margin-bottom: 0.5rem;
        }
        
        .alert-message {
            color: #64748b;
        }
        
        .refresh-indicator {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #10b981;
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            display: none;
        }
        
        @media (max-width: 768px) {
            .dashboard-container {
                padding: 1rem;
            }
            
            .charts-section {
                grid-template-columns: 1fr;
            }
            
            .header-content {
                flex-direction: column;
                gap: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="refresh-indicator" id="refreshIndicator">
        Atualizando dados...
    </div>
    
    <header class="dashboard-header">
        <div class="header-content">
            <div class="header-title">
                <h1>Dashboard CWB Hub</h1>
                <div class="header-subtitle">Sistema de Relatórios Automatizados</div>
            </div>
            <div class="header-status">
                <div class="status-indicator">
                    <div class="status-dot"></div>
                    <span>Sistema Operacional</span>
                </div>
                <div class="status-indicator">
                    <i data-feather="clock"></i>
                    <span id="lastUpdate">Atualizado agora</span>
                </div>
            </div>
        </div>
    </header>
    
    <div class="dashboard-container">
        <!-- Métricas Principais -->
        <div class="metrics-grid" id="metricsGrid">
            <!-- Métricas serão inseridas aqui via JavaScript -->
        </div>
        
        <!-- Gráficos -->
        <div class="charts-section">
            <div class="chart-container">
                <h3 class="chart-title">Tendência de Sessões (24h)</h3>
                <canvas id="sessionsChart" width="400" height="200"></canvas>
            </div>
            
            <div class="activity-section">
                <h3 class="chart-title">Atividade Recente</h3>
                <div id="recentActivity">
                    <!-- Atividades serão inseridas aqui -->
                </div>
            </div>
        </div>
        
        <!-- Alertas -->
        <div class="alerts-section" id="alertsSection">
            <!-- Alertas serão inseridos aqui -->
        </div>
    </div>
    
    <script>
        // Dados do dashboard (inseridos pelo Python)
        const dashboardData = """ + json.dumps(dashboard_data, default=str, ensure_ascii=False) + """;
        
        // Função para renderizar métricas
        function renderMetrics() {
            const metricsGrid = document.getElementById('metricsGrid');
            metricsGrid.innerHTML = '';
            
            dashboardData.key_metrics.forEach(metric => {
                const card = document.createElement('div');
                card.className = 'metric-card';
                card.style.borderLeftColor = getColorCode(metric.color);
                
                card.innerHTML = `
                    <div class="metric-header">
                        <div class="metric-icon" style="background: ${getColorCode(metric.color)}20; color: ${getColorCode(metric.color)}">
                            <i data-feather="${metric.icon}"></i>
                        </div>
                    </div>
                    <div class="metric-value" style="color: ${getColorCode(metric.color)}">
                        ${metric.value}${metric.unit}
                    </div>
                    <div class="metric-label">${metric.title}</div>
                `;
                
                metricsGrid.appendChild(card);
            });
            
            feather.replace();
        }
        
        // Função para renderizar atividades
        function renderActivity() {
            const activityContainer = document.getElementById('recentActivity');
            activityContainer.innerHTML = '';
            
            dashboardData.recent_activity.slice(0, 5).forEach(activity => {
                const item = document.createElement('div');
                item.className = 'activity-item';
                
                const timeAgo = getTimeAgo(new Date(activity.timestamp));
                
                item.innerHTML = `
                    <div class="activity-icon" style="background: ${getColorCode(activity.color)}20; color: ${getColorCode(activity.color)}">
                        <i data-feather="${activity.icon}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${activity.title}</div>
                        <div class="activity-description">${activity.description}</div>
                        <div class="activity-time">${timeAgo}</div>
                    </div>
                `;
                
                activityContainer.appendChild(item);
            });
            
            feather.replace();
        }
        
        // Função para renderizar alertas
        function renderAlerts() {
            const alertsSection = document.getElementById('alertsSection');
            alertsSection.innerHTML = '';
            
            if (dashboardData.alerts && dashboardData.alerts.length > 0) {
                const title = document.createElement('h3');
                title.className = 'chart-title';
                title.textContent = 'Alertas Ativos';
                alertsSection.appendChild(title);
                
                dashboardData.alerts.forEach(alert => {
                    const alertDiv = document.createElement('div');
                    alertDiv.className = `alert ${alert.type}`;
                    
                    alertDiv.innerHTML = `
                        <div class="alert-title">${alert.title}</div>
                        <div class="alert-message">${alert.message}</div>
                    `;
                    
                    alertsSection.appendChild(alertDiv);
                });
            }
        }
        
        // Função para renderizar gráfico de sessões
        function renderSessionsChart() {
            const ctx = document.getElementById('sessionsChart').getContext('2d');
            
            new Chart(ctx, {
                type: 'line',
                data: dashboardData.charts_data.sessions_trend,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            grid: {
                                color: '#f1f5f9'
                            }
                        },
                        x: {
                            grid: {
                                color: '#f1f5f9'
                            }
                        }
                    },
                    elements: {
                        point: {
                            radius: 3,
                            hoverRadius: 6
                        },
                        line: {
                            tension: 0.4
                        }
                    }
                }
            });
        }
        
        // Funções utilitárias
        function getColorCode(color) {
            const colors = {
                blue: '#3b82f6',
                green: '#10b981',
                orange: '#f59e0b',
                purple: '#8b5cf6',
                red: '#ef4444',
                cyan: '#06b6d4'
            };
            return colors[color] || '#64748b';
        }
        
        function getTimeAgo(date) {
            const now = new Date();
            const diff = now - date;
            const minutes = Math.floor(diff / 60000);
            const hours = Math.floor(minutes / 60);
            
            if (hours > 0) {
                return `${hours}h atrás`;
            } else if (minutes > 0) {
                return `${minutes}m atrás`;
            } else {
                return 'Agora';
            }
        }
        
        // Função para atualizar timestamp
        function updateTimestamp() {
            const lastUpdate = document.getElementById('lastUpdate');
            const updateTime = new Date(dashboardData.timestamp);
            const timeAgo = getTimeAgo(updateTime);
            lastUpdate.textContent = `Atualizado ${timeAgo}`;
        }
        
        // Auto-refresh (a cada 30 segundos)
        function autoRefresh() {
            const indicator = document.getElementById('refreshIndicator');
            indicator.style.display = 'block';
            
            setTimeout(() => {
                location.reload();
            }, 1000);
        }
        
        // Inicializar dashboard
        document.addEventListener('DOMContentLoaded', function() {
            renderMetrics();
            renderActivity();
            renderAlerts();
            renderSessionsChart();
            updateTimestamp();
            
            // Auto-refresh a cada 5 minutos
            setInterval(autoRefresh, 300000);
            
            // Atualizar timestamp a cada minuto
            setInterval(updateTimestamp, 60000);
        });
    </script>
</body>
</html>
        """
        
        return html_template
    
    async def create_session(self, user_id: str) -> str:
        """Cria uma nova sessão de dashboard"""
        session_id = str(uuid.uuid4())
        
        self.active_sessions[session_id] = {
            "user_id": user_id,
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "preferences": {}
        }
        
        return session_id
    
    def update_session_activity(self, session_id: str):
        """Atualiza atividade da sessão"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]["last_activity"] = datetime.utcnow()
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Obtém informações da sessão"""
        return self.active_sessions.get(session_id)
    
    async def cleanup_old_sessions(self, max_age_hours: int = 24):
        """Remove sessões antigas"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for session_id, session_data in self.active_sessions.items():
            if session_data["last_activity"] < cutoff_time:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            del self.active_sessions[session_id]
        
        if to_remove:
            self.logger.info(f"Removidas {len(to_remove)} sessões antigas do dashboard")
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Obtém estatísticas do dashboard"""
        return {
            "active_sessions": len(self.active_sessions),
            "cache_status": "valid" if self._is_cache_valid() else "expired",
            "last_cache_update": self.last_cache_update.isoformat() if self.last_cache_update else None,
            "widgets_enabled": len([w for w in self.widget_configs.values() if w["enabled"]]),
            "total_widgets": len(self.widget_configs)
        }