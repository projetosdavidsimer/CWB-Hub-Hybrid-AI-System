"""
Report Engine - Motor Principal do Sistema de Relatórios
Criado pela Equipe Híbrida CWB Hub

Pedro Henrique Almeida (Project Manager): "Vamos orquestrar todo o processo 
de geração de relatórios de forma eficiente e coordenada."

Carlos Eduardo Santos (Arquiteto): "Com uma arquitetura robusta que integra 
coleta, processamento e distribuição de forma seamless."
"""

import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json

from .data_collector import DataCollector
from .template_engine import TemplateEngine
from ..models.report_models import (
    ReportType, ReportFormat, ReportStatus, 
    ReportCreate, ReportExecutionCreate, ReportExecutionResponse
)

logger = logging.getLogger(__name__)


class ReportEngine:
    """
    Motor principal do sistema de relatórios
    
    Responsabilidades:
    - Orquestrar o processo de geração de relatórios
    - Coordenar coleta de dados e renderização
    - Gerenciar execuções e status
    - Integrar com exportadores e distribuidores
    """
    
    def __init__(
        self, 
        data_collector: Optional[DataCollector] = None,
        template_engine: Optional[TemplateEngine] = None,
        output_dir: Optional[Path] = None
    ):
        self.data_collector = data_collector or DataCollector()
        self.template_engine = template_engine or TemplateEngine()
        
        if output_dir is None:
            output_dir = Path(__file__).parent.parent.parent / "reports_output"
        
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Cache de execuções ativas
        self.active_executions: Dict[str, Dict[str, Any]] = {}
        
        # Configurações padrão de relatórios
        self.default_reports = self._get_default_report_configs()
    
    async def generate_report(
        self,
        report_type: Union[ReportType, str],
        output_formats: List[ReportFormat] = None,
        period_start: Optional[datetime] = None,
        period_end: Optional[datetime] = None,
        parameters: Optional[Dict[str, Any]] = None,
        execution_id: Optional[str] = None
    ) -> ReportExecutionResponse:
        """
        Gera um relatório completo
        
        Args:
            report_type: Tipo do relatório
            output_formats: Formatos de saída desejados
            period_start: Início do período de dados
            period_end: Fim do período de dados
            parameters: Parâmetros específicos do relatório
            execution_id: ID da execução (gerado automaticamente se não fornecido)
            
        Returns:
            Resposta com detalhes da execução
        """
        if execution_id is None:
            execution_id = str(uuid.uuid4())
        
        if output_formats is None:
            output_formats = [ReportFormat.HTML]
        
        if parameters is None:
            parameters = {}
        
        # Registrar execução
        execution = {
            "execution_id": execution_id,
            "report_type": report_type,
            "status": ReportStatus.PENDING,
            "started_at": datetime.utcnow(),
            "output_formats": output_formats,
            "parameters": parameters,
            "period_start": period_start,
            "period_end": period_end,
            "output_files": [],
            "error_message": None
        }
        
        self.active_executions[execution_id] = execution
        
        try:
            self.logger.info(f"Iniciando geração de relatório: {report_type} (ID: {execution_id})")
            
            # Atualizar status
            execution["status"] = ReportStatus.RUNNING
            
            # 1. Coletar dados
            self.logger.info("Coletando dados...")
            data = await self.data_collector.collect_all_metrics(period_start, period_end)
            
            # Validar dados
            if not await self.data_collector.validate_metrics(data):
                raise ValueError("Dados coletados falharam na validação")
            
            # 2. Obter configuração do relatório
            report_config = self._get_report_config(report_type)
            template_name = report_config["template_name"]
            
            # 3. Preparar dados para o template
            template_data = self._prepare_template_data(data, parameters, report_config)
            
            # 4. Renderizar template
            self.logger.info(f"Renderizando template: {template_name}")
            html_content = self.template_engine.render_template(template_name, template_data)
            
            # 5. Gerar arquivos de saída
            output_files = []
            for format_type in output_formats:
                file_path = await self._export_report(
                    html_content, format_type, execution_id, report_type
                )
                if file_path:
                    output_files.append(str(file_path))
            
            # 6. Finalizar execução
            execution["status"] = ReportStatus.COMPLETED
            execution["completed_at"] = datetime.utcnow()
            execution["duration_seconds"] = (
                execution["completed_at"] - execution["started_at"]
            ).total_seconds()
            execution["output_files"] = output_files
            
            self.logger.info(f"Relatório gerado com sucesso: {execution_id}")
            
            return ReportExecutionResponse(
                id=0,  # Seria o ID do banco de dados
                execution_id=execution_id,
                report_id=0,  # Seria o ID do relatório no banco
                status=execution["status"],
                started_at=execution["started_at"],
                completed_at=execution["completed_at"],
                duration_seconds=execution["duration_seconds"],
                output_files=execution["output_files"],
                error_message=None,
                data_period_start=period_start,
                data_period_end=period_end,
                triggered_by="manual"
            )
            
        except Exception as e:
            self.logger.error(f"Erro na geração do relatório {execution_id}: {e}")
            
            # Atualizar status de erro
            execution["status"] = ReportStatus.FAILED
            execution["completed_at"] = datetime.utcnow()
            execution["error_message"] = str(e)
            execution["duration_seconds"] = (
                execution["completed_at"] - execution["started_at"]
            ).total_seconds()
            
            return ReportExecutionResponse(
                id=0,
                execution_id=execution_id,
                report_id=0,
                status=execution["status"],
                started_at=execution["started_at"],
                completed_at=execution["completed_at"],
                duration_seconds=execution["duration_seconds"],
                output_files=[],
                error_message=execution["error_message"],
                data_period_start=period_start,
                data_period_end=period_end,
                triggered_by="manual"
            )
    
    async def generate_dashboard_report(self) -> str:
        """
        Gera relatório de dashboard em tempo real
        
        Returns:
            HTML do dashboard
        """
        try:
            self.logger.info("Gerando dashboard em tempo real")
            
            # Coletar dados do dashboard
            dashboard_data = await self.data_collector.get_dashboard_data()
            
            # Converter para dicionário para o template
            data = {
                "current_sessions": dashboard_data.current_sessions,
                "active_agents": dashboard_data.active_agents,
                "total_users": dashboard_data.total_users,
                "system_uptime": dashboard_data.system_uptime,
                "avg_response_time": dashboard_data.avg_response_time,
                "error_rate": dashboard_data.error_rate,
                "collaboration_score": dashboard_data.collaboration_score,
                "trends": dashboard_data.trends
            }
            
            # Renderizar dashboard
            html_content = self.template_engine.render_template("dashboard.html", data)
            
            self.logger.info("Dashboard gerado com sucesso")
            return html_content
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar dashboard: {e}")
            return self.template_engine._render_error_template(str(e))
    
    def _get_report_config(self, report_type: Union[ReportType, str]) -> Dict[str, Any]:
        """Obtém configuração do relatório"""
        if isinstance(report_type, str):
            report_type = ReportType(report_type)
        
        return self.default_reports.get(report_type, self.default_reports[ReportType.EXECUTIVE_SUMMARY])
    
    def _prepare_template_data(
        self, 
        raw_data: Dict[str, Any], 
        parameters: Dict[str, Any],
        report_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Prepara dados para o template"""
        
        # Dados base do template
        template_data = {
            **raw_data,
            **parameters,
            "report_config": report_config,
            "generated_at": datetime.utcnow(),
            "system_name": "CWB Hub Hybrid AI System",
            "version": "1.0.0"
        }
        
        # Adicionar métricas calculadas
        template_data["calculated_metrics"] = self._calculate_derived_metrics(raw_data)
        
        return template_data
    
    def _calculate_derived_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula métricas derivadas dos dados brutos"""
        try:
            session_metrics = data.get("session_metrics", {})
            agent_metrics = data.get("agent_metrics", {})
            system_metrics = data.get("system_metrics", {})
            
            return {
                "overall_health_score": self._calculate_health_score(data),
                "efficiency_score": self._calculate_efficiency_score(session_metrics, agent_metrics),
                "resource_utilization": self._calculate_resource_utilization(system_metrics),
                "trend_analysis": self._analyze_trends(data)
            }
        except Exception as e:
            self.logger.warning(f"Erro ao calcular métricas derivadas: {e}")
            return {}
    
    def _calculate_health_score(self, data: Dict[str, Any]) -> float:
        """Calcula score geral de saúde do sistema"""
        try:
            # Fatores para o score de saúde
            factors = []
            
            # Taxa de sucesso das sessões
            session_metrics = data.get("session_metrics", {})
            success_rate = session_metrics.get("success_rate_percent", 0)
            factors.append(success_rate / 100)
            
            # Performance do sistema
            performance_metrics = data.get("performance_metrics", {})
            error_rate = performance_metrics.get("error_rate_percent", 0)
            factors.append(max(0, (100 - error_rate) / 100))
            
            # Colaboração entre agentes
            collab_metrics = data.get("collaboration_metrics", {})
            collab_score = collab_metrics.get("collaboration_quality_score", 0)
            factors.append(collab_score / 10)
            
            # Calcular média ponderada
            if factors:
                return round(sum(factors) / len(factors) * 10, 2)
            return 0.0
            
        except Exception as e:
            self.logger.warning(f"Erro ao calcular health score: {e}")
            return 0.0
    
    def _calculate_efficiency_score(
        self, 
        session_metrics: Dict[str, Any], 
        agent_metrics: Dict[str, Any]
    ) -> float:
        """Calcula score de eficiência"""
        try:
            factors = []
            
            # Tempo médio de sessão
            avg_duration = session_metrics.get("avg_session_duration_minutes", 0)
            if avg_duration > 0:
                # Normalizar para score (assumindo 30 min como ideal)
                duration_score = min(1.0, 30 / avg_duration)
                factors.append(duration_score)
            
            # Tempo médio de resposta dos agentes
            avg_response_time = agent_metrics.get("avg_response_time", 0)
            if avg_response_time > 0:
                # Normalizar para score (assumindo 3s como ideal)
                response_score = min(1.0, 3 / avg_response_time)
                factors.append(response_score)
            
            # Taxa de participação dos agentes
            participation_rate = agent_metrics.get("avg_participation_rate", 0)
            factors.append(participation_rate / 100)
            
            if factors:
                return round(sum(factors) / len(factors) * 10, 2)
            return 0.0
            
        except Exception as e:
            self.logger.warning(f"Erro ao calcular efficiency score: {e}")
            return 0.0
    
    def _calculate_resource_utilization(self, system_metrics: Dict[str, Any]) -> Dict[str, float]:
        """Calcula utilização de recursos"""
        try:
            return {
                "cpu_utilization": system_metrics.get("cpu_usage_percent", 0),
                "memory_utilization": system_metrics.get("memory_usage_percent", 0),
                "disk_utilization": system_metrics.get("disk_usage_percent", 0),
                "overall_utilization": (
                    system_metrics.get("cpu_usage_percent", 0) +
                    system_metrics.get("memory_usage_percent", 0) +
                    system_metrics.get("disk_usage_percent", 0)
                ) / 3
            }
        except Exception as e:
            self.logger.warning(f"Erro ao calcular utilização de recursos: {e}")
            return {}
    
    def _analyze_trends(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Analisa tendências dos dados"""
        try:
            # Análise simplificada de tendências
            trends = {}
            
            # Tendência de sessões (simulada)
            session_metrics = data.get("session_metrics", {})
            total_sessions = session_metrics.get("total_sessions_period", 0)
            
            if total_sessions > 100:
                trends["sessions"] = "crescendo"
            elif total_sessions > 50:
                trends["sessions"] = "estável"
            else:
                trends["sessions"] = "baixo"
            
            # Tendência de qualidade
            quality_metrics = data.get("quality_metrics", {})
            quality_score = quality_metrics.get("avg_response_quality_score", 0)
            
            if quality_score > 8.5:
                trends["quality"] = "excelente"
            elif quality_score > 7.0:
                trends["quality"] = "boa"
            else:
                trends["quality"] = "precisa_melhoria"
            
            return trends
            
        except Exception as e:
            self.logger.warning(f"Erro ao analisar tendências: {e}")
            return {}
    
    async def _export_report(
        self,
        html_content: str,
        format_type: ReportFormat,
        execution_id: str,
        report_type: Union[ReportType, str]
    ) -> Optional[Path]:
        """Exporta relatório no formato especificado"""
        try:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            filename = f"{report_type}_{timestamp}_{execution_id[:8]}"
            
            if format_type == ReportFormat.HTML:
                file_path = self.output_dir / f"{filename}.html"
                file_path.write_text(html_content, encoding='utf-8')
                return file_path
            
            elif format_type == ReportFormat.PDF:
                # Importar weasyprint apenas quando necessário
                try:
                    from weasyprint import HTML, CSS
                    file_path = self.output_dir / f"{filename}.pdf"
                    
                    # CSS básico para PDF
                    css = CSS(string="""
                        @page { margin: 2cm; }
                        body { font-family: Arial, sans-serif; }
                        .chart-container img { max-width: 100%; }
                    """)
                    
                    HTML(string=html_content).write_pdf(str(file_path), stylesheets=[css])
                    return file_path
                    
                except ImportError:
                    self.logger.warning("WeasyPrint não disponível, pulando geração de PDF")
                    return None
            
            elif format_type == ReportFormat.JSON:
                # Extrair dados estruturados do HTML (simplificado)
                file_path = self.output_dir / f"{filename}.json"
                json_data = {
                    "execution_id": execution_id,
                    "report_type": str(report_type),
                    "generated_at": datetime.utcnow().isoformat(),
                    "html_content": html_content
                }
                file_path.write_text(json.dumps(json_data, indent=2), encoding='utf-8')
                return file_path
            
            else:
                self.logger.warning(f"Formato não suportado: {format_type}")
                return None
                
        except Exception as e:
            self.logger.error(f"Erro ao exportar relatório em {format_type}: {e}")
            return None
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Obtém status de uma execução"""
        return self.active_executions.get(execution_id)
    
    def list_active_executions(self) -> List[Dict[str, Any]]:
        """Lista todas as execuções ativas"""
        return list(self.active_executions.values())
    
    def _get_default_report_configs(self) -> Dict[ReportType, Dict[str, Any]]:
        """Configurações padrão dos relatórios"""
        return {
            ReportType.EXECUTIVE_SUMMARY: {
                "name": "Relatório Executivo",
                "description": "Visão geral executiva do sistema",
                "template_name": "executive_summary.html",
                "default_formats": [ReportFormat.HTML, ReportFormat.PDF],
                "data_requirements": ["session_metrics", "agent_metrics", "collaboration_metrics"]
            },
            ReportType.AGENT_PERFORMANCE: {
                "name": "Performance dos Agentes",
                "description": "Análise detalhada da performance individual dos agentes",
                "template_name": "agent_performance.html",
                "default_formats": [ReportFormat.HTML],
                "data_requirements": ["agent_metrics", "collaboration_metrics"]
            },
            ReportType.COLLABORATION_STATS: {
                "name": "Estatísticas de Colaboração",
                "description": "Métricas de colaboração entre agentes",
                "template_name": "collaboration_stats.html",
                "default_formats": [ReportFormat.HTML],
                "data_requirements": ["collaboration_metrics", "agent_metrics"]
            },
            ReportType.SYSTEM_USAGE: {
                "name": "Uso do Sistema",
                "description": "Métricas de utilização e performance do sistema",
                "template_name": "system_usage.html",
                "default_formats": [ReportFormat.HTML],
                "data_requirements": ["system_metrics", "session_metrics", "performance_metrics"]
            },
            ReportType.QUALITY_ANALYSIS: {
                "name": "Análise de Qualidade",
                "description": "Análise da qualidade das respostas e satisfação",
                "template_name": "executive_summary.html",  # Reutilizar por enquanto
                "default_formats": [ReportFormat.HTML],
                "data_requirements": ["quality_metrics", "session_metrics"]
            }
        }
    
    async def cleanup_old_executions(self, max_age_hours: int = 24):
        """Remove execuções antigas do cache"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        
        to_remove = []
        for execution_id, execution in self.active_executions.items():
            if execution["started_at"] < cutoff_time:
                to_remove.append(execution_id)
        
        for execution_id in to_remove:
            del self.active_executions[execution_id]
        
        if to_remove:
            self.logger.info(f"Removidas {len(to_remove)} execuções antigas do cache")