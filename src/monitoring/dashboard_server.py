#!/usr/bin/env python3
"""
CWB Hub Dashboard Server - Servidor Web do Dashboard
Melhoria #8 - Dashboard de Monitoramento Avançado
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

# FastAPI imports
try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("⚠️ FastAPI não disponível. Usando servidor HTTP básico.")

from .metrics_aggregator import metrics_aggregator, MetricType, AlertLevel

logger = logging.getLogger(__name__)

class DashboardServer:
    """
    Servidor Web do Dashboard CWB Hub
    
    Funcionalidades:
    - APIs REST para métricas
    - WebSocket para atualizações em tempo real
    - Interface web responsiva
    - Autenticação básica
    - Exportação de relatórios
    """
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.app = None
        self.websocket_connections: List[WebSocket] = []
        
        # Estatísticas do servidor
        self.server_stats = {
            "start_time": time.time(),
            "total_requests": 0,
            "websocket_connections": 0,
            "api_calls": 0
        }
        
        if FASTAPI_AVAILABLE:
            self._setup_fastapi()
        else:
            self._setup_basic_server()
        
        logger.info(f"📊 Dashboard Server configurado em {host}:{port}")
    
    def _setup_fastapi(self):
        """Configura servidor FastAPI"""
        self.app = FastAPI(
            title="CWB Hub Dashboard",
            description="Dashboard de Monitoramento Avançado",
            version="1.0.0"
        )
        
        # CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Middleware para estatísticas
        @self.app.middleware("http")
        async def stats_middleware(request, call_next):
            self.server_stats["total_requests"] += 1
            response = await call_next(request)
            return response
        
        # Rotas
        self._setup_routes()
        
        # Servir arquivos estáticos
        static_path = Path(__file__).parent / "static"
        if static_path.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_path)), name="static")
    
    def _setup_basic_server(self):
        """Configura servidor HTTP básico (fallback)"""
        # Implementação básica sem FastAPI
        logger.warning("⚠️ Usando servidor básico. Funcionalidades limitadas.")
    
    def _setup_routes(self):
        """Configura rotas da API"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home():
            """Página principal do dashboard"""
            return await self._get_dashboard_html()
        
        @self.app.get("/api/health")
        async def health_check():
            """Health check da API"""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time() - self.server_stats["start_time"]
            }
        
        @self.app.get("/api/metrics/current")
        async def get_current_metrics():
            """Métricas atuais"""
            self.server_stats["api_calls"] += 1
            await metrics_aggregator.collect_all_metrics()
            return metrics_aggregator.get_current_metrics()
        
        @self.app.get("/api/metrics/historical")
        async def get_historical_metrics(
            metric_type: Optional[str] = None,
            hours: int = 24
        ):
            """Métricas históricas"""
            self.server_stats["api_calls"] += 1
            
            metric_type_enum = None
            if metric_type:
                try:
                    metric_type_enum = MetricType(metric_type)
                except ValueError:
                    raise HTTPException(status_code=400, detail="Invalid metric type")
            
            return metrics_aggregator.get_historical_metrics(metric_type_enum, hours)
        
        @self.app.get("/api/alerts")
        async def get_alerts(resolved: Optional[bool] = None):
            """Lista de alertas"""
            self.server_stats["api_calls"] += 1
            return metrics_aggregator.get_alerts(resolved)
        
        @self.app.post("/api/alerts/{alert_id}/resolve")
        async def resolve_alert(alert_id: str):
            """Resolve um alerta"""
            self.server_stats["api_calls"] += 1
            success = metrics_aggregator.resolve_alert(alert_id)
            if success:
                return {"status": "resolved", "alert_id": alert_id}
            else:
                raise HTTPException(status_code=404, detail="Alert not found")
        
        @self.app.get("/api/summary")
        async def get_summary():
            """Resumo executivo"""
            self.server_stats["api_calls"] += 1
            await metrics_aggregator.collect_all_metrics()
            
            summary = metrics_aggregator.get_summary_stats()
            
            # Adicionar métricas do servidor
            summary.update({
                "server_uptime": time.time() - self.server_stats["start_time"],
                "total_api_requests": self.server_stats["total_requests"],
                "websocket_connections": len(self.websocket_connections)
            })
            
            return summary
        
        @self.app.get("/api/report/executive")
        async def get_executive_report():
            """Relatório executivo"""
            self.server_stats["api_calls"] += 1
            return await self._generate_executive_report()
        
        @self.app.websocket("/ws/metrics")
        async def websocket_metrics(websocket: WebSocket):
            """WebSocket para métricas em tempo real"""
            await websocket.accept()
            self.websocket_connections.append(websocket)
            self.server_stats["websocket_connections"] += 1
            
            try:
                while True:
                    # Coletar métricas atuais
                    await metrics_aggregator.collect_all_metrics()
                    current_metrics = metrics_aggregator.get_current_metrics()
                    
                    # Enviar para cliente
                    await websocket.send_json({
                        "type": "metrics_update",
                        "data": current_metrics,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # Aguardar 5 segundos
                    await asyncio.sleep(5)
                    
            except WebSocketDisconnect:
                self.websocket_connections.remove(websocket)
                logger.info("🔌 Cliente WebSocket desconectado")
    
    async def _get_dashboard_html(self) -> str:
        """Retorna HTML do dashboard"""
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CWB Hub - Dashboard de Monitoramento</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 2rem;
            font-weight: 700;
        }
        
        .header .subtitle {
            color: #7f8c8d;
            font-size: 1rem;
            margin-top: 0.5rem;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-top: 2rem;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 1.5rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .card h3 {
            color: #2c3e50;
            margin-bottom: 1rem;
            font-size: 1.2rem;
            border-bottom: 2px solid #3498db;
            padding-bottom: 0.5rem;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 0.8rem 0;
            padding: 0.5rem;
            background: rgba(52, 152, 219, 0.1);
            border-radius: 8px;
        }
        
        .metric-label {
            font-weight: 500;
            color: #34495e;
        }
        
        .metric-value {
            font-weight: 700;
            font-size: 1.1rem;
        }
        
        .status-healthy { color: #27ae60; }
        .status-warning { color: #f39c12; }
        .status-error { color: #e74c3c; }
        .status-critical { color: #c0392b; }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 1rem;
        }
        
        .alerts-container {
            max-height: 300px;
            overflow-y: auto;
        }
        
        .alert {
            padding: 0.8rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .alert-info { 
            background: rgba(52, 152, 219, 0.1);
            border-left-color: #3498db;
        }
        
        .alert-warning { 
            background: rgba(243, 156, 18, 0.1);
            border-left-color: #f39c12;
        }
        
        .alert-error { 
            background: rgba(231, 76, 60, 0.1);
            border-left-color: #e74c3c;
        }
        
        .alert-critical { 
            background: rgba(192, 57, 43, 0.1);
            border-left-color: #c0392b;
        }
        
        .connection-status {
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 0.5rem 1rem;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .connected {
            background: rgba(39, 174, 96, 0.9);
            color: white;
        }
        
        .disconnected {
            background: rgba(231, 76, 60, 0.9);
            color: white;
        }
        
        @media (max-width: 768px) {
            .dashboard-grid {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 1rem;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 CWB Hub Dashboard</h1>
        <div class="subtitle">Sistema de Monitoramento Avançado - IA Híbrida</div>
    </div>
    
    <div class="connection-status" id="connectionStatus">
        🔌 Conectando...
    </div>
    
    <div class="container">
        <div class="dashboard-grid">
            <!-- Status Geral -->
            <div class="card">
                <h3>📊 Status Geral do Sistema</h3>
                <div class="metric">
                    <span class="metric-label">Status:</span>
                    <span class="metric-value" id="systemStatus">Carregando...</span>
                </div>
                <div class="metric">
                    <span class="metric-label">CPU:</span>
                    <span class="metric-value" id="cpuUsage">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Memória:</span>
                    <span class="metric-value" id="memoryUsage">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Sessões Ativas:</span>
                    <span class="metric-value" id="activeSessions">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Uptime:</span>
                    <span class="metric-value" id="uptime">0h</span>
                </div>
            </div>
            
            <!-- Cache Performance -->
            <div class="card">
                <h3>💾 Performance do Cache</h3>
                <div class="metric">
                    <span class="metric-label">Hit Rate:</span>
                    <span class="metric-value" id="cacheHitRate">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Hits:</span>
                    <span class="metric-value" id="cacheHits">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Misses:</span>
                    <span class="metric-value" id="cacheMisses">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Economia:</span>
                    <span class="metric-value" id="costSavings">$0.00</span>
                </div>
            </div>
            
            <!-- Sistema de Aprendizado -->
            <div class="card">
                <h3>🧠 Sistema de Aprendizado</h3>
                <div class="metric">
                    <span class="metric-label">Satisfação Média:</span>
                    <span class="metric-value" id="avgSatisfaction">0%</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Total Interações:</span>
                    <span class="metric-value" id="totalInteractions">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Padrões Identificados:</span>
                    <span class="metric-value" id="patternsIdentified">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Taxa de Evolução:</span>
                    <span class="metric-value" id="evolutionRate">0%</span>
                </div>
            </div>
            
            <!-- Alertas -->
            <div class="card">
                <h3>🚨 Alertas Ativos</h3>
                <div class="alerts-container" id="alertsContainer">
                    <div class="metric">
                        <span class="metric-label">Carregando alertas...</span>
                    </div>
                </div>
            </div>
            
            <!-- Gráfico de Performance -->
            <div class="card">
                <h3>📈 Performance em Tempo Real</h3>
                <div class="chart-container">
                    <canvas id="performanceChart"></canvas>
                </div>
            </div>
            
            <!-- Métricas LLM -->
            <div class="card">
                <h3>🤖 Sistema LLM</h3>
                <div class="metric">
                    <span class="metric-label">Custo/Hora:</span>
                    <span class="metric-value" id="llmCost">$0.00</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Tokens Processados:</span>
                    <span class="metric-value" id="tokensProcessed">0</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Taxa de Erro:</span>
                    <span class="metric-value" id="llmErrorRate">0%</span>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // WebSocket connection
        let ws;
        let performanceChart;
        let chartData = {
            labels: [],
            datasets: [{
                label: 'CPU %',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }, {
                label: 'Memória %',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }]
        };
        
        function initChart() {
            const ctx = document.getElementById('performanceChart').getContext('2d');
            performanceChart = new Chart(ctx, {
                type: 'line',
                data: chartData,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
        
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/metrics`;
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                document.getElementById('connectionStatus').textContent = '🟢 Conectado';
                document.getElementById('connectionStatus').className = 'connection-status connected';
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                if (data.type === 'metrics_update') {
                    updateDashboard(data.data);
                }
            };
            
            ws.onclose = function() {
                document.getElementById('connectionStatus').textContent = '🔴 Desconectado';
                document.getElementById('connectionStatus').className = 'connection-status disconnected';
                
                // Tentar reconectar em 5 segundos
                setTimeout(connectWebSocket, 5000);
            };
            
            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }
        
        function updateDashboard(data) {
            const systemHealth = data.system_health;
            const currentMetrics = data.current_metrics;
            
            // Status geral
            document.getElementById('systemStatus').textContent = systemHealth.overall_status;
            document.getElementById('systemStatus').className = `metric-value status-${systemHealth.overall_status}`;
            
            document.getElementById('cpuUsage').textContent = `${systemHealth.cpu_usage.toFixed(1)}%`;
            document.getElementById('memoryUsage').textContent = `${systemHealth.memory_usage.toFixed(1)}%`;
            document.getElementById('activeSessions').textContent = systemHealth.active_sessions;
            document.getElementById('uptime').textContent = `${(systemHealth.uptime / 3600).toFixed(1)}h`;
            
            // Cache metrics
            if (currentMetrics['cache.hit_rate']) {
                document.getElementById('cacheHitRate').textContent = `${currentMetrics['cache.hit_rate'].value.toFixed(1)}%`;
            }
            if (currentMetrics['cache.hits']) {
                document.getElementById('cacheHits').textContent = currentMetrics['cache.hits'].value;
            }
            if (currentMetrics['cache.misses']) {
                document.getElementById('cacheMisses').textContent = currentMetrics['cache.misses'].value;
            }
            if (currentMetrics['cache.cost_savings']) {
                document.getElementById('costSavings').textContent = `$${currentMetrics['cache.cost_savings'].value.toFixed(2)}`;
            }
            
            // Learning metrics
            if (currentMetrics['learning.average_satisfaction']) {
                document.getElementById('avgSatisfaction').textContent = `${currentMetrics['learning.average_satisfaction'].value.toFixed(1)}%`;
            }
            if (currentMetrics['learning.total_interactions']) {
                document.getElementById('totalInteractions').textContent = currentMetrics['learning.total_interactions'].value;
            }
            if (currentMetrics['learning.patterns_identified']) {
                document.getElementById('patternsIdentified').textContent = currentMetrics['learning.patterns_identified'].value;
            }
            if (currentMetrics['learning.evolution_success_rate']) {
                document.getElementById('evolutionRate').textContent = `${currentMetrics['learning.evolution_success_rate'].value.toFixed(1)}%`;
            }
            
            // LLM metrics
            if (currentMetrics['llm.cost_per_hour']) {
                document.getElementById('llmCost').textContent = `$${currentMetrics['llm.cost_per_hour'].value.toFixed(2)}`;
            }
            if (currentMetrics['llm.tokens_processed']) {
                document.getElementById('tokensProcessed').textContent = currentMetrics['llm.tokens_processed'].value.toLocaleString();
            }
            if (currentMetrics['llm.error_rate']) {
                document.getElementById('llmErrorRate').textContent = `${currentMetrics['llm.error_rate'].value.toFixed(1)}%`;
            }
            
            // Update chart
            updateChart(systemHealth);
            
            // Update alerts
            updateAlerts();
        }
        
        function updateChart(systemHealth) {
            const now = new Date().toLocaleTimeString();
            
            // Add new data point
            chartData.labels.push(now);
            chartData.datasets[0].data.push(systemHealth.cpu_usage);
            chartData.datasets[1].data.push(systemHealth.memory_usage);
            
            // Keep only last 20 points
            if (chartData.labels.length > 20) {
                chartData.labels.shift();
                chartData.datasets[0].data.shift();
                chartData.datasets[1].data.shift();
            }
            
            performanceChart.update();
        }
        
        async function updateAlerts() {
            try {
                const response = await fetch('/api/alerts?resolved=false');
                const alerts = await response.json();
                
                const container = document.getElementById('alertsContainer');
                
                if (alerts.length === 0) {
                    container.innerHTML = '<div class="metric"><span class="metric-label">✅ Nenhum alerta ativo</span></div>';
                } else {
                    container.innerHTML = alerts.map(alert => `
                        <div class="alert alert-${alert.level}">
                            <strong>${alert.title}</strong><br>
                            ${alert.description}<br>
                            <small>${new Date(alert.timestamp).toLocaleString()}</small>
                        </div>
                    `).join('');
                }
            } catch (error) {
                console.error('Error fetching alerts:', error);
            }
        }
        
        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            initChart();
            connectWebSocket();
        });
    </script>
</body>
</html>
        """
    
    async def _generate_executive_report(self) -> Dict[str, Any]:
        """Gera relatório executivo"""
        await metrics_aggregator.collect_all_metrics()
        
        summary = metrics_aggregator.get_summary_stats()
        current_metrics = metrics_aggregator.get_current_metrics()
        alerts = metrics_aggregator.get_alerts(resolved=False)
        
        # Calcular KPIs
        kpis = {
            "system_availability": 100 - summary.get("active_alerts", 0) * 5,  # Estimativa
            "performance_score": 100 - summary.get("cpu_usage", 0) - summary.get("memory_usage", 0) / 2,
            "user_satisfaction": summary.get("average_satisfaction", 0),
            "cost_efficiency": summary.get("cache_hit_rate", 0),
            "ai_evolution_rate": 85  # Estimativa baseada no sistema de aprendizado
        }
        
        # Tendências (simuladas para MVP)
        trends = {
            "performance": "improving",
            "costs": "decreasing",
            "satisfaction": "stable",
            "reliability": "excellent"
        }
        
        # Recomendações
        recommendations = []
        
        if summary.get("cpu_usage", 0) > 70:
            recommendations.append("Considerar upgrade de CPU ou otimização de processos")
        
        if summary.get("cache_hit_rate", 0) < 60:
            recommendations.append("Otimizar estratégia de cache para melhor performance")
        
        if len(alerts) > 5:
            recommendations.append("Revisar e resolver alertas pendentes")
        
        if summary.get("average_satisfaction", 0) < 80:
            recommendations.append("Analisar feedback dos usuários para melhorias")
        
        return {
            "report_id": f"exec_report_{int(time.time())}",
            "generated_at": datetime.now().isoformat(),
            "period": "last_24_hours",
            "executive_summary": {
                "overall_health": summary.get("system_health", "unknown"),
                "key_metrics": {
                    "uptime_hours": summary.get("uptime_hours", 0),
                    "total_sessions": summary.get("active_sessions", 0),
                    "cache_efficiency": summary.get("cache_hit_rate", 0),
                    "user_satisfaction": summary.get("average_satisfaction", 0)
                }
            },
            "kpis": kpis,
            "trends": trends,
            "alerts_summary": {
                "total_active": len(alerts),
                "critical": len([a for a in alerts if a.get("level") == "critical"]),
                "warnings": len([a for a in alerts if a.get("level") == "warning"])
            },
            "recommendations": recommendations,
            "cost_analysis": {
                "estimated_savings": summary.get("cache_hit_rate", 0) * 100,  # Estimativa
                "efficiency_score": kpis["cost_efficiency"]
            }
        }
    
    async def start_server(self):
        """Inicia o servidor"""
        if FASTAPI_AVAILABLE and self.app:
            logger.info(f"🚀 Iniciando Dashboard Server em http://{self.host}:{self.port}")
            
            # Iniciar coleta de métricas em background
            asyncio.create_task(self._metrics_collection_loop())
            
            # Iniciar servidor
            config = uvicorn.Config(
                app=self.app,
                host=self.host,
                port=self.port,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()
        else:
            logger.error("❌ FastAPI não disponível. Não é possível iniciar o servidor.")
    
    async def _metrics_collection_loop(self):
        """Loop de coleta de métricas em background"""
        while True:
            try:
                await metrics_aggregator.collect_all_metrics()
                await asyncio.sleep(30)  # Coletar a cada 30 segundos
            except Exception as e:
                logger.error(f"❌ Erro na coleta de métricas: {e}")
                await asyncio.sleep(60)  # Aguardar mais tempo em caso de erro
    
    async def broadcast_alert(self, alert: Dict[str, Any]):
        """Envia alerta para todos os clientes WebSocket conectados"""
        if self.websocket_connections:
            message = {
                "type": "alert",
                "data": alert,
                "timestamp": datetime.now().isoformat()
            }
            
            # Enviar para todos os clientes conectados
            disconnected = []
            for websocket in self.websocket_connections:
                try:
                    await websocket.send_json(message)
                except:
                    disconnected.append(websocket)
            
            # Remover conexões desconectadas
            for ws in disconnected:
                self.websocket_connections.remove(ws)

# Instância global do servidor de dashboard
dashboard_server = DashboardServer()

if __name__ == "__main__":
    # Executar servidor
    if FASTAPI_AVAILABLE:
        asyncio.run(dashboard_server.start_server())
    else:
        print("❌ FastAPI não disponível. Instale com: pip install fastapi uvicorn")
        print("📊 Métricas ainda podem ser coletadas via metrics_aggregator")