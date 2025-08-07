"""
Template Engine - Sistema de Templates para Relatórios
Criado pela Equipe Híbrida CWB Hub

Isabella Santos (UX/UI Designer): "Vamos criar templates elegantes e informativos 
que transformem dados complexos em insights visuais claros."

Sofia Oliveira (Full Stack): "Com um engine flexível que suporte múltiplos 
formatos e customizações avançadas."
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

from jinja2 import Environment, FileSystemLoader, Template, select_autoescape
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import base64
from io import BytesIO

logger = logging.getLogger(__name__)


class TemplateEngine:
    """
    Engine de templates para geração de relatórios
    
    Responsabilidades:
    - Renderizar templates HTML com dados
    - Gerar gráficos e visualizações
    - Aplicar estilos e formatação
    - Suportar templates customizados
    """
    
    def __init__(self, templates_dir: Optional[Path] = None):
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"
        
        self.templates_dir = templates_dir
        self.templates_dir.mkdir(exist_ok=True)
        
        # Configurar Jinja2
        self.env = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Adicionar filtros customizados
        self._register_custom_filters()
        
        # Configurar matplotlib para gráficos
        plt.style.use('seaborn-v0_8')
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Criar templates padrão se não existirem
        self._create_default_templates()
    
    def _register_custom_filters(self):
        """Registra filtros customizados para os templates"""
        
        @self.env.filter('format_number')
        def format_number(value, decimals=2):
            """Formata números com separadores de milhares"""
            if isinstance(value, (int, float)):
                return f"{value:,.{decimals}f}".replace(',', '.')
            return value
        
        @self.env.filter('format_percent')
        def format_percent(value, decimals=1):
            """Formata percentuais"""
            if isinstance(value, (int, float)):
                return f"{value:.{decimals}f}%"
            return value
        
        @self.env.filter('format_duration')
        def format_duration(seconds):
            """Formata duração em formato legível"""
            if not isinstance(seconds, (int, float)):
                return seconds
            
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            secs = int(seconds % 60)
            
            if hours > 0:
                return f"{hours}h {minutes}m {secs}s"
            elif minutes > 0:
                return f"{minutes}m {secs}s"
            else:
                return f"{secs}s"
        
        @self.env.filter('status_badge')
        def status_badge(status):
            """Gera badge HTML para status"""
            colors = {
                'active': 'success',
                'inactive': 'secondary',
                'error': 'danger',
                'warning': 'warning',
                'completed': 'success',
                'pending': 'info',
                'running': 'primary'
            }
            color = colors.get(status.lower(), 'secondary')
            return f'<span class="badge badge-{color}">{status}</span>'
    
    def render_template(
        self, 
        template_name: str, 
        data: Dict[str, Any],
        **kwargs
    ) -> str:
        """
        Renderiza um template com os dados fornecidos
        
        Args:
            template_name: Nome do template
            data: Dados para renderização
            **kwargs: Parâmetros adicionais
            
        Returns:
            HTML renderizado
        """
        try:
            template = self.env.get_template(template_name)
            
            # Adicionar dados padrão
            render_data = {
                'generated_at': datetime.utcnow(),
                'system_name': 'CWB Hub Hybrid AI System',
                'version': '1.0.0',
                **data,
                **kwargs
            }
            
            # Gerar gráficos se necessário
            if 'charts' not in render_data and self._should_generate_charts(template_name):
                render_data['charts'] = self._generate_charts(data)
            
            html = template.render(**render_data)
            self.logger.info(f"Template '{template_name}' renderizado com sucesso")
            return html
            
        except Exception as e:
            self.logger.error(f"Erro ao renderizar template '{template_name}': {e}")
            return self._render_error_template(str(e))
    
    def _should_generate_charts(self, template_name: str) -> bool:
        """Verifica se o template precisa de gráficos"""
        chart_templates = [
            'executive_summary.html',
            'agent_performance.html',
            'collaboration_stats.html',
            'dashboard.html'
        ]
        return template_name in chart_templates
    
    def _generate_charts(self, data: Dict[str, Any]) -> Dict[str, str]:
        """
        Gera gráficos baseados nos dados
        
        Args:
            data: Dados para gerar gráficos
            
        Returns:
            Dicionário com gráficos em base64
        """
        charts = {}
        
        try:
            # Gráfico de sessões ao longo do tempo
            if 'trends' in data and 'sessions' in data['trends']:
                charts['sessions_trend'] = self._create_line_chart(
                    data['trends']['sessions'],
                    title='Sessões por Dia',
                    ylabel='Número de Sessões'
                )
            
            # Gráfico de performance dos agentes
            if 'agent_metrics' in data and 'agent_details' in data['agent_metrics']:
                charts['agent_performance'] = self._create_agent_performance_chart(
                    data['agent_metrics']['agent_details']
                )
            
            # Gráfico de métricas do sistema
            if 'system_metrics' in data:
                charts['system_metrics'] = self._create_system_metrics_chart(
                    data['system_metrics']
                )
            
            # Gráfico de colaboração
            if 'collaboration_metrics' in data:
                charts['collaboration'] = self._create_collaboration_chart(
                    data['collaboration_metrics']
                )
            
        except Exception as e:
            self.logger.error(f"Erro ao gerar gráficos: {e}")
        
        return charts
    
    def _create_line_chart(
        self, 
        values: List[float], 
        title: str, 
        ylabel: str
    ) -> str:
        """Cria gráfico de linha"""
        try:
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Dados dos últimos 7 dias
            dates = pd.date_range(end=datetime.now(), periods=len(values), freq='D')
            
            ax.plot(dates, values, marker='o', linewidth=2, markersize=6)
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_ylabel(ylabel)
            ax.grid(True, alpha=0.3)
            
            # Formatação do eixo X
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            plt.xticks(rotation=45)
            
            plt.tight_layout()
            
            # Converter para base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{chart_base64}"
            
        except Exception as e:
            self.logger.error(f"Erro ao criar gráfico de linha: {e}")
            return ""
    
    def _create_agent_performance_chart(self, agent_data: Dict[str, Any]) -> str:
        """Cria gráfico de performance dos agentes"""
        try:
            agents = list(agent_data.keys())
            participation_rates = [agent_data[agent]['participation_rate'] for agent in agents]
            quality_scores = [agent_data[agent]['quality_score'] for agent in agents]
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # Gráfico de participação
            bars1 = ax1.bar(range(len(agents)), participation_rates, color='skyblue')
            ax1.set_title('Taxa de Participação dos Agentes', fontweight='bold')
            ax1.set_ylabel('Taxa de Participação (%)')
            ax1.set_xticks(range(len(agents)))
            ax1.set_xticklabels([agent.split()[-1] for agent in agents], rotation=45)
            
            # Adicionar valores nas barras
            for bar, value in zip(bars1, participation_rates):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                        f'{value:.1f}%', ha='center', va='bottom')
            
            # Gráfico de qualidade
            bars2 = ax2.bar(range(len(agents)), quality_scores, color='lightgreen')
            ax2.set_title('Score de Qualidade dos Agentes', fontweight='bold')
            ax2.set_ylabel('Score de Qualidade')
            ax2.set_xticks(range(len(agents)))
            ax2.set_xticklabels([agent.split()[-1] for agent in agents], rotation=45)
            ax2.set_ylim(0, 10)
            
            # Adicionar valores nas barras
            for bar, value in zip(bars2, quality_scores):
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                        f'{value:.1f}', ha='center', va='bottom')
            
            plt.tight_layout()
            
            # Converter para base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{chart_base64}"
            
        except Exception as e:
            self.logger.error(f"Erro ao criar gráfico de agentes: {e}")
            return ""
    
    def _create_system_metrics_chart(self, system_data: Dict[str, Any]) -> str:
        """Cria gráfico de métricas do sistema"""
        try:
            metrics = ['CPU', 'Memória', 'Disco']
            values = [
                system_data.get('cpu_usage_percent', 0),
                system_data.get('memory_usage_percent', 0),
                system_data.get('disk_usage_percent', 0)
            ]
            
            colors = ['#ff9999', '#66b3ff', '#99ff99']
            
            fig, ax = plt.subplots(figsize=(8, 8))
            wedges, texts, autotexts = ax.pie(values, labels=metrics, colors=colors,
                                            autopct='%1.1f%%', startangle=90)
            
            ax.set_title('Uso de Recursos do Sistema', fontsize=14, fontweight='bold')
            
            # Melhorar aparência do texto
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
            
            # Converter para base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{chart_base64}"
            
        except Exception as e:
            self.logger.error(f"Erro ao criar gráfico do sistema: {e}")
            return ""
    
    def _create_collaboration_chart(self, collab_data: Dict[str, Any]) -> str:
        """Cria gráfico de colaboração"""
        try:
            # Gráfico de interações entre agentes
            interactions = collab_data.get('cross_agent_interactions', {})
            
            if not interactions:
                return ""
            
            agents = list(interactions.keys())
            values = list(interactions.values())
            
            fig, ax = plt.subplots(figsize=(10, 6))
            bars = ax.bar(range(len(agents)), values, color='coral')
            
            ax.set_title('Interações por Agente', fontweight='bold')
            ax.set_ylabel('Número de Interações')
            ax.set_xticks(range(len(agents)))
            ax.set_xticklabels([agent.replace('_', ' ') for agent in agents], rotation=45)
            
            # Adicionar valores nas barras
            for bar, value in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                       str(value), ha='center', va='bottom')
            
            plt.tight_layout()
            
            # Converter para base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
            buffer.seek(0)
            chart_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close()
            
            return f"data:image/png;base64,{chart_base64}"
            
        except Exception as e:
            self.logger.error(f"Erro ao criar gráfico de colaboração: {e}")
            return ""
    
    def _render_error_template(self, error_message: str) -> str:
        """Renderiza template de erro"""
        return f"""
        <html>
        <head>
            <title>Erro na Geração do Relatório</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .error {{ color: #d32f2f; background: #ffebee; padding: 20px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>Erro na Geração do Relatório</h1>
            <div class="error">
                <strong>Erro:</strong> {error_message}
            </div>
            <p>Por favor, verifique os dados e tente novamente.</p>
        </body>
        </html>
        """
    
    def _create_default_templates(self):
        """Cria templates padrão se não existirem"""
        templates = {
            'executive_summary.html': self._get_executive_template(),
            'agent_performance.html': self._get_agent_performance_template(),
            'collaboration_stats.html': self._get_collaboration_template(),
            'system_usage.html': self._get_system_usage_template(),
            'dashboard.html': self._get_dashboard_template()
        }
        
        for template_name, content in templates.items():
            template_path = self.templates_dir / template_name
            if not template_path.exists():
                template_path.write_text(content, encoding='utf-8')
                self.logger.info(f"Template padrão criado: {template_name}")
    
    def _get_executive_template(self) -> str:
        """Template para relatório executivo"""
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Executivo - CWB Hub</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 3px solid #2196F3; padding-bottom: 20px; margin-bottom: 30px; }
        .header h1 { color: #1976D2; margin: 0; font-size: 2.5em; }
        .header p { color: #666; margin: 10px 0 0 0; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
        .metric-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }
        .metric-value { font-size: 2.5em; font-weight: bold; margin: 10px 0; }
        .metric-label { font-size: 1.1em; opacity: 0.9; }
        .section { margin: 40px 0; }
        .section h2 { color: #1976D2; border-left: 4px solid #2196F3; padding-left: 15px; }
        .chart-container { text-align: center; margin: 20px 0; }
        .chart-container img { max-width: 100%; height: auto; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .summary-text { line-height: 1.6; color: #333; }
        .footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ system_name }}</h1>
            <p>Relatório Executivo - {{ generated_at.strftime('%d/%m/%Y às %H:%M') }}</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value">{{ session_metrics.active_sessions | format_number(0) }}</div>
                <div class="metric-label">Sessões Ativas</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ agent_metrics.total_active_agents | format_number(0) }}</div>
                <div class="metric-label">Agentes Ativos</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ session_metrics.success_rate_percent | format_percent }}</div>
                <div class="metric-label">Taxa de Sucesso</div>
            </div>
            <div class="metric-card">
                <div class="metric-value">{{ collaboration_metrics.collaboration_quality_score | format_number(1) }}</div>
                <div class="metric-label">Score de Colaboração</div>
            </div>
        </div>

        <div class="section">
            <h2>Resumo Executivo</h2>
            <div class="summary-text">
                <p>O sistema CWB Hub Hybrid AI apresentou excelente performance no período analisado, 
                com {{ session_metrics.total_sessions_period }} sessões processadas e uma taxa de sucesso de 
                {{ session_metrics.success_rate_percent | format_percent }}.</p>
                
                <p>Os {{ agent_metrics.total_active_agents }} agentes especializados mantiveram alta qualidade 
                nas respostas, com score médio de {{ agent_metrics.avg_participation_rate | format_number(1) }}% 
                de participação e tempo médio de resposta de {{ agent_metrics.avg_response_time | format_number(1) }} segundos.</p>
                
                <p>O sistema de colaboração entre agentes demonstrou eficiência excepcional, com 
                {{ collaboration_metrics.successful_collaborations }} colaborações bem-sucedidas de um total de 
                {{ collaboration_metrics.total_collaborations }}, resultando em uma taxa de consenso de 
                {{ collaboration_metrics.consensus_rate | format_percent }}.</p>
            </div>
        </div>

        {% if charts.sessions_trend %}
        <div class="section">
            <h2>Tendência de Sessões</h2>
            <div class="chart-container">
                <img src="{{ charts.sessions_trend }}" alt="Gráfico de Tendência de Sessões">
            </div>
        </div>
        {% endif %}

        {% if charts.agent_performance %}
        <div class="section">
            <h2>Performance dos Agentes</h2>
            <div class="chart-container">
                <img src="{{ charts.agent_performance }}" alt="Gráfico de Performance dos Agentes">
            </div>
        </div>
        {% endif %}

        <div class="footer">
            <p>Relatório gerado automaticamente pelo Sistema de Relatórios CWB Hub</p>
            <p>Versão {{ version }} - {{ generated_at.strftime('%d/%m/%Y às %H:%M:%S') }}</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_agent_performance_template(self) -> str:
        """Template para performance dos agentes"""
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Performance dos Agentes - CWB Hub</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 3px solid #4CAF50; padding-bottom: 20px; margin-bottom: 30px; }
        .header h1 { color: #388E3C; margin: 0; font-size: 2.5em; }
        .agent-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0; }
        .agent-card { border: 1px solid #ddd; border-radius: 10px; padding: 20px; background: #fafafa; }
        .agent-name { font-size: 1.3em; font-weight: bold; color: #388E3C; margin-bottom: 15px; }
        .metric-row { display: flex; justify-content: space-between; margin: 10px 0; }
        .metric-label { color: #666; }
        .metric-value { font-weight: bold; color: #333; }
        .chart-container { text-align: center; margin: 30px 0; }
        .chart-container img { max-width: 100%; height: auto; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .section h2 { color: #388E3C; border-left: 4px solid #4CAF50; padding-left: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Performance dos Agentes</h1>
            <p>Análise Detalhada - {{ generated_at.strftime('%d/%m/%Y às %H:%M') }}</p>
        </div>

        {% if charts.agent_performance %}
        <div class="section">
            <h2>Visão Geral da Performance</h2>
            <div class="chart-container">
                <img src="{{ charts.agent_performance }}" alt="Gráfico de Performance dos Agentes">
            </div>
        </div>
        {% endif %}

        <div class="section">
            <h2>Detalhes por Agente</h2>
            <div class="agent-grid">
                {% for agent_name, metrics in agent_metrics.agent_details.items() %}
                <div class="agent-card">
                    <div class="agent-name">{{ agent_name }}</div>
                    <div class="metric-row">
                        <span class="metric-label">Taxa de Participação:</span>
                        <span class="metric-value">{{ metrics.participation_rate | format_percent }}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Tempo Médio de Resposta:</span>
                        <span class="metric-value">{{ metrics.avg_response_time_seconds | format_duration }}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Total de Interações:</span>
                        <span class="metric-value">{{ metrics.total_interactions | format_number(0) }}</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Score de Qualidade:</span>
                        <span class="metric-value">{{ metrics.quality_score | format_number(1) }}/10</span>
                    </div>
                    <div class="metric-row">
                        <span class="metric-label">Score de Colaboração:</span>
                        <span class="metric-value">{{ metrics.collaboration_score | format_number(1) }}/10</span>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <div class="footer">
            <p>Relatório gerado automaticamente pelo Sistema de Relatórios CWB Hub</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_collaboration_template(self) -> str:
        """Template para estatísticas de colaboração"""
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estatísticas de Colaboração - CWB Hub</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 3px solid #FF9800; padding-bottom: 20px; margin-bottom: 30px; }
        .header h1 { color: #F57C00; margin: 0; font-size: 2.5em; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 30px 0; }
        .stat-card { background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }
        .stat-value { font-size: 2em; font-weight: bold; margin: 10px 0; }
        .stat-label { font-size: 1em; opacity: 0.9; }
        .chart-container { text-align: center; margin: 30px 0; }
        .chart-container img { max-width: 100%; height: auto; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .section h2 { color: #F57C00; border-left: 4px solid #FF9800; padding-left: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Estatísticas de Colaboração</h1>
            <p>Análise da Colaboração entre Agentes - {{ generated_at.strftime('%d/%m/%Y às %H:%M') }}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{{ collaboration_metrics.total_collaborations | format_number(0) }}</div>
                <div class="stat-label">Total de Colaborações</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ collaboration_metrics.consensus_rate | format_percent }}</div>
                <div class="stat-label">Taxa de Consenso</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ collaboration_metrics.avg_collaboration_time | format_duration }}</div>
                <div class="stat-label">Tempo Médio</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{{ collaboration_metrics.collaboration_quality_score | format_number(1) }}</div>
                <div class="stat-label">Score de Qualidade</div>
            </div>
        </div>

        {% if charts.collaboration %}
        <div class="section">
            <h2>Interações por Agente</h2>
            <div class="chart-container">
                <img src="{{ charts.collaboration }}" alt="Gráfico de Interações por Agente">
            </div>
        </div>
        {% endif %}

        <div class="footer">
            <p>Relatório gerado automaticamente pelo Sistema de Relatórios CWB Hub</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_system_usage_template(self) -> str:
        """Template para uso do sistema"""
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Uso do Sistema - CWB Hub</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 3px solid #9C27B0; padding-bottom: 20px; margin-bottom: 30px; }
        .header h1 { color: #7B1FA2; margin: 0; font-size: 2.5em; }
        .usage-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
        .usage-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }
        .usage-value { font-size: 2.2em; font-weight: bold; margin: 10px 0; }
        .usage-label { font-size: 1em; opacity: 0.9; }
        .chart-container { text-align: center; margin: 30px 0; }
        .chart-container img { max-width: 100%; height: auto; border-radius: 5px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        .section h2 { color: #7B1FA2; border-left: 4px solid #9C27B0; padding-left: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Uso do Sistema</h1>
            <p>Métricas de Utilização - {{ generated_at.strftime('%d/%m/%Y às %H:%M') }}</p>
        </div>

        <div class="usage-grid">
            <div class="usage-card">
                <div class="usage-value">{{ system_metrics.uptime_hours | format_number(1) }}h</div>
                <div class="usage-label">Tempo de Atividade</div>
            </div>
            <div class="usage-card">
                <div class="usage-value">{{ system_metrics.cpu_usage_percent | format_percent }}</div>
                <div class="usage-label">Uso de CPU</div>
            </div>
            <div class="usage-card">
                <div class="usage-value">{{ system_metrics.memory_usage_percent | format_percent }}</div>
                <div class="usage-label">Uso de Memória</div>
            </div>
            <div class="usage-card">
                <div class="usage-value">{{ session_metrics.sessions_per_hour | format_number(1) }}</div>
                <div class="usage-label">Sessões/Hora</div>
            </div>
        </div>

        {% if charts.system_metrics %}
        <div class="section">
            <h2>Recursos do Sistema</h2>
            <div class="chart-container">
                <img src="{{ charts.system_metrics }}" alt="Gráfico de Recursos do Sistema">
            </div>
        </div>
        {% endif %}

        <div class="footer">
            <p>Relatório gerado automaticamente pelo Sistema de Relatórios CWB Hub</p>
        </div>
    </div>
</body>
</html>
        """
    
    def _get_dashboard_template(self) -> str:
        """Template para dashboard"""
        return """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - CWB Hub</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { text-align: center; background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header h1 { color: #1976D2; margin: 0; font-size: 2.5em; }
        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .widget { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .widget h3 { margin-top: 0; color: #333; border-bottom: 2px solid #2196F3; padding-bottom: 10px; }
        .metric-large { font-size: 3em; font-weight: bold; color: #1976D2; text-align: center; margin: 20px 0; }
        .metric-small { display: flex; justify-content: space-between; margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 5px; }
        .chart-container { text-align: center; }
        .chart-container img { max-width: 100%; height: auto; border-radius: 5px; }
        .status-good { color: #4CAF50; font-weight: bold; }
        .status-warning { color: #FF9800; font-weight: bold; }
        .status-error { color: #f44336; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Dashboard CWB Hub</h1>
            <p>Última atualização: {{ generated_at.strftime('%d/%m/%Y às %H:%M:%S') }}</p>
        </div>

        <div class="dashboard-grid">
            <div class="widget">
                <h3>Sessões Ativas</h3>
                <div class="metric-large">{{ current_sessions | format_number(0) }}</div>
                <div class="metric-small">
                    <span>Total do Período:</span>
                    <span>{{ total_users | format_number(0) }}</span>
                </div>
            </div>

            <div class="widget">
                <h3>Agentes</h3>
                <div class="metric-large">{{ active_agents | format_number(0) }}</div>
                <div class="metric-small">
                    <span>Status:</span>
                    <span class="status-good">Todos Ativos</span>
                </div>
            </div>

            <div class="widget">
                <h3>Performance</h3>
                <div class="metric-small">
                    <span>Tempo de Resposta:</span>
                    <span>{{ avg_response_time | format_number(1) }}ms</span>
                </div>
                <div class="metric-small">
                    <span>Taxa de Erro:</span>
                    <span class="{% if error_rate < 5 %}status-good{% elif error_rate < 10 %}status-warning{% else %}status-error{% endif %}">{{ error_rate | format_percent }}</span>
                </div>
                <div class="metric-small">
                    <span>Uptime:</span>
                    <span class="status-good">{{ system_uptime | format_number(1) }}h</span>
                </div>
            </div>

            <div class="widget">
                <h3>Colaboração</h3>
                <div class="metric-large">{{ collaboration_score | format_number(1) }}</div>
                <div class="metric-small">
                    <span>Score de Qualidade</span>
                    <span class="status-good">Excelente</span>
                </div>
            </div>

            {% if charts.sessions_trend %}
            <div class="widget" style="grid-column: span 2;">
                <h3>Tendência de Sessões</h3>
                <div class="chart-container">
                    <img src="{{ charts.sessions_trend }}" alt="Tendência de Sessões">
                </div>
            </div>
            {% endif %}

            {% if charts.agent_performance %}
            <div class="widget" style="grid-column: span 2;">
                <h3>Performance dos Agentes</h3>
                <div class="chart-container">
                    <img src="{{ charts.agent_performance }}" alt="Performance dos Agentes">
                </div>
            </div>
            {% endif %}
        </div>
    </div>
</body>
</html>
        """