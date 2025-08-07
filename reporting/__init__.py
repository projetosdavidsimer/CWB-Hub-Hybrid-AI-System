"""
CWB Hub Automated Reporting System
Sistema de Relatórios Automatizados da CWB Hub

Criado pela Equipe Híbrida CWB Hub:
- Ana Beatriz Costa (CTO) - Estratégia e Visão
- Carlos Eduardo Santos (Arquiteto) - Arquitetura do Sistema
- Sofia Oliveira (Full Stack) - Implementação Web
- Gabriel Mendes (Mobile) - Integração Mobile
- Isabella Santos (UX/UI) - Design dos Relatórios
- Lucas Pereira (QA) - Qualidade e Testes
- Mariana Rodrigues (DevOps) - Infraestrutura
- Pedro Henrique Almeida (PM) - Gestão do Projeto
"""

__version__ = "1.0.0"
__author__ = "Equipe Híbrida CWB Hub"

from .core.report_engine import ReportEngine
from .core.data_collector import DataCollector
from .core.template_engine import TemplateEngine
from .core.scheduler import ReportScheduler

__all__ = [
    "ReportEngine",
    "DataCollector", 
    "TemplateEngine",
    "ReportScheduler"
]