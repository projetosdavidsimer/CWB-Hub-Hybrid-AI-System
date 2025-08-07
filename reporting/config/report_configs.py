"""
Report Configurations - Configurações do Sistema de Relatórios
Criado pela Equipe Híbrida CWB Hub

Pedro Henrique Almeida (PM): "Configurações centralizadas para facilitar 
a gestão e customização do sistema de relatórios."
"""

import os
from datetime import timedelta
from typing import Dict, Any, List
from pathlib import Path

from ..models.report_models import ReportType, ReportFormat, ReportFrequency


class ReportConfig:
    """Configurações centralizadas do sistema de relatórios"""
    
    # Configurações de diretórios
    BASE_DIR = Path(__file__).parent.parent.parent
    REPORTS_OUTPUT_DIR = BASE_DIR / "reports_output"
    TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
    
    # Configurações de banco de dados
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cwb_user:cwb_password_2025@localhost:5432/cwb_hub")
    
    # Configurações de email
    SMTP_CONFIG = {
        "server": os.getenv("SMTP_SERVER", "smtp.gmail.com"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "username": os.getenv("SMTP_USERNAME", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        "from_name": os.getenv("SMTP_FROM_NAME", "CWB Hub Sistema de Relatórios"),
        "from_email": os.getenv("SMTP_FROM_EMAIL", "noreply@cwbhub.com")
    }
    
    # Configurações de agendamento
    SCHEDULER_CONFIG = {
        "timezone": "America/Sao_Paulo",
        "max_instances": 3,
        "coalesce": False,
        "misfire_grace_time": 300,  # 5 minutos
        "cleanup_interval_hours": 24
    }
    
    # Configurações de retenção
    RETENTION_CONFIG = {
        "reports_max_age_days": 90,
        "executions_max_age_days": 30,
        "logs_max_age_days": 7,
        "cleanup_enabled": True
    }
    
    # Configurações de performance
    PERFORMANCE_CONFIG = {
        "max_concurrent_reports": 5,
        "report_timeout_minutes": 30,
        "data_collection_timeout_minutes": 10,
        "template_render_timeout_minutes": 5
    }
    
    # Configurações de cache
    CACHE_CONFIG = {
        "enabled": True,
        "ttl_minutes": 15,
        "max_size_mb": 100,
        "cache_metrics": True,
        "cache_templates": True
    }
    
    # Configurações de segurança
    SECURITY_CONFIG = {
        "require_authentication": True,
        "allowed_file_types": [".html", ".pdf", ".json", ".xlsx", ".csv"],
        "max_file_size_mb": 50,
        "sanitize_filenames": True
    }
    
    # Configurações padrão de relatórios
    DEFAULT_REPORT_CONFIGS = {
        ReportType.EXECUTIVE_SUMMARY: {
            "name": "Relatório Executivo",
            "description": "Visão geral executiva do sistema CWB Hub",
            "template_name": "executive_summary.html",
            "default_formats": [ReportFormat.HTML, ReportFormat.PDF],
            "default_frequency": ReportFrequency.DAILY,
            "default_schedule_time": "08:00",
            "data_requirements": [
                "session_metrics",
                "agent_metrics", 
                "collaboration_metrics",
                "system_metrics"
            ],
            "recipients": [
                "cto@cwbhub.com",
                "management@cwbhub.com"
            ],
            "priority": "high"
        },
        
        ReportType.AGENT_PERFORMANCE: {
            "name": "Performance dos Agentes",
            "description": "Análise detalhada da performance individual dos agentes",
            "template_name": "agent_performance.html",
            "default_formats": [ReportFormat.HTML],
            "default_frequency": ReportFrequency.WEEKLY,
            "default_schedule_time": "09:00",
            "data_requirements": [
                "agent_metrics",
                "collaboration_metrics",
                "quality_metrics"
            ],
            "recipients": [
                "tech-lead@cwbhub.com",
                "development@cwbhub.com"
            ],
            "priority": "medium"
        },
        
        ReportType.COLLABORATION_STATS: {
            "name": "Estatísticas de Colaboração",
            "description": "Métricas de colaboração entre agentes especializados",
            "template_name": "collaboration_stats.html",
            "default_formats": [ReportFormat.HTML, ReportFormat.PDF],
            "default_frequency": ReportFrequency.WEEKLY,
            "default_schedule_time": "10:00",
            "data_requirements": [
                "collaboration_metrics",
                "agent_metrics"
            ],
            "recipients": [
                "research@cwbhub.com",
                "ai-team@cwbhub.com"
            ],
            "priority": "medium"
        },
        
        ReportType.SYSTEM_USAGE: {
            "name": "Uso do Sistema",
            "description": "Métricas de utilização e performance do sistema",
            "template_name": "system_usage.html",
            "default_formats": [ReportFormat.HTML],
            "default_frequency": ReportFrequency.DAILY,
            "default_schedule_time": "07:00",
            "data_requirements": [
                "system_metrics",
                "session_metrics",
                "performance_metrics"
            ],
            "recipients": [
                "devops@cwbhub.com",
                "infrastructure@cwbhub.com"
            ],
            "priority": "high"
        },
        
        ReportType.QUALITY_ANALYSIS: {
            "name": "Análise de Qualidade",
            "description": "Análise da qualidade das respostas e satisfação do usuário",
            "template_name": "executive_summary.html",  # Reutilizar por enquanto
            "default_formats": [ReportFormat.HTML, ReportFormat.PDF],
            "default_frequency": ReportFrequency.WEEKLY,
            "default_schedule_time": "11:00",
            "data_requirements": [
                "quality_metrics",
                "session_metrics",
                "agent_metrics"
            ],
            "recipients": [
                "quality@cwbhub.com",
                "product@cwbhub.com"
            ],
            "priority": "medium"
        }
    }
    
    # Configurações de métricas
    METRICS_CONFIG = {
        "collection_interval_minutes": 5,
        "aggregation_levels": ["hour", "day", "week", "month"],
        "retention_periods": {
            "raw_data_days": 7,
            "hourly_data_days": 30,
            "daily_data_days": 365,
            "weekly_data_days": 730,
            "monthly_data_days": 1825  # 5 anos
        },
        "quality_thresholds": {
            "min_success_rate": 90.0,
            "max_error_rate": 5.0,
            "min_collaboration_score": 7.0,
            "max_response_time_seconds": 10.0
        }
    }
    
    # Configurações de alertas
    ALERT_CONFIG = {
        "enabled": True,
        "email_alerts": True,
        "alert_recipients": [
            "alerts@cwbhub.com",
            "devops@cwbhub.com"
        ],
        "thresholds": {
            "high_error_rate": 10.0,
            "low_success_rate": 85.0,
            "high_response_time": 15.0,
            "low_collaboration_score": 6.0,
            "system_cpu_high": 80.0,
            "system_memory_high": 85.0,
            "system_disk_high": 90.0
        },
        "cooldown_minutes": 30  # Evitar spam de alertas
    }
    
    # Configurações de dashboard
    DASHBOARD_CONFIG = {
        "refresh_interval_seconds": 30,
        "max_data_points": 100,
        "chart_colors": [
            "#1976D2", "#388E3C", "#F57C00", "#7B1FA2",
            "#C2185B", "#00796B", "#5D4037", "#455A64"
        ],
        "default_time_range_hours": 24,
        "enable_real_time": True
    }
    
    # Configurações de exportação
    EXPORT_CONFIG = {
        "pdf_options": {
            "page_size": "A4",
            "margin": "2cm",
            "encoding": "utf-8",
            "enable_local_file_access": True
        },
        "excel_options": {
            "engine": "openpyxl",
            "include_charts": True,
            "sheet_name": "Relatório"
        },
        "csv_options": {
            "encoding": "utf-8",
            "separator": ",",
            "include_headers": True
        }
    }
    
    @classmethod
    def get_report_config(cls, report_type: ReportType) -> Dict[str, Any]:
        """Obtém configuração específica de um tipo de relatório"""
        return cls.DEFAULT_REPORT_CONFIGS.get(
            report_type, 
            cls.DEFAULT_REPORT_CONFIGS[ReportType.EXECUTIVE_SUMMARY]
        )
    
    @classmethod
    def get_smtp_config(cls) -> Dict[str, Any]:
        """Obtém configuração SMTP"""
        return cls.SMTP_CONFIG.copy()
    
    @classmethod
    def get_scheduler_config(cls) -> Dict[str, Any]:
        """Obtém configuração do scheduler"""
        return cls.SCHEDULER_CONFIG.copy()
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Valida configurações do sistema"""
        validation_results = {}
        
        # Validar diretórios
        validation_results["directories"] = all([
            cls.REPORTS_OUTPUT_DIR.parent.exists(),
            cls.TEMPLATES_DIR.parent.exists()
        ])
        
        # Validar configuração SMTP
        smtp_config = cls.SMTP_CONFIG
        validation_results["smtp"] = all([
            smtp_config["server"],
            smtp_config["port"] > 0,
            smtp_config["port"] < 65536
        ])
        
        # Validar configuração de banco
        validation_results["database"] = bool(cls.DATABASE_URL)
        
        # Validar configurações de performance
        perf_config = cls.PERFORMANCE_CONFIG
        validation_results["performance"] = all([
            perf_config["max_concurrent_reports"] > 0,
            perf_config["report_timeout_minutes"] > 0,
            perf_config["data_collection_timeout_minutes"] > 0
        ])
        
        return validation_results
    
    @classmethod
    def create_directories(cls):
        """Cria diretórios necessários"""
        directories = [
            cls.REPORTS_OUTPUT_DIR,
            cls.TEMPLATES_DIR,
            cls.BASE_DIR / "logs",
            cls.BASE_DIR / "cache"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_environment_info(cls) -> Dict[str, Any]:
        """Obtém informações do ambiente"""
        return {
            "base_dir": str(cls.BASE_DIR),
            "reports_output_dir": str(cls.REPORTS_OUTPUT_DIR),
            "templates_dir": str(cls.TEMPLATES_DIR),
            "database_configured": bool(cls.DATABASE_URL),
            "smtp_configured": bool(cls.SMTP_CONFIG["username"]),
            "cache_enabled": cls.CACHE_CONFIG["enabled"],
            "alerts_enabled": cls.ALERT_CONFIG["enabled"],
            "security_enabled": cls.SECURITY_CONFIG["require_authentication"]
        }


# Configurações específicas por ambiente
class DevelopmentConfig(ReportConfig):
    """Configurações para ambiente de desenvolvimento"""
    
    # Configurações mais relaxadas para desenvolvimento
    PERFORMANCE_CONFIG = {
        **ReportConfig.PERFORMANCE_CONFIG,
        "max_concurrent_reports": 2,
        "report_timeout_minutes": 10
    }
    
    CACHE_CONFIG = {
        **ReportConfig.CACHE_CONFIG,
        "ttl_minutes": 5  # Cache mais curto para desenvolvimento
    }
    
    ALERT_CONFIG = {
        **ReportConfig.ALERT_CONFIG,
        "enabled": False  # Desabilitar alertas em desenvolvimento
    }


class ProductionConfig(ReportConfig):
    """Configurações para ambiente de produção"""
    
    # Configurações otimizadas para produção
    PERFORMANCE_CONFIG = {
        **ReportConfig.PERFORMANCE_CONFIG,
        "max_concurrent_reports": 10,
        "report_timeout_minutes": 60
    }
    
    CACHE_CONFIG = {
        **ReportConfig.CACHE_CONFIG,
        "ttl_minutes": 30,
        "max_size_mb": 500
    }
    
    SECURITY_CONFIG = {
        **ReportConfig.SECURITY_CONFIG,
        "require_authentication": True,
        "max_file_size_mb": 100
    }


# Função para obter configuração baseada no ambiente
def get_config() -> ReportConfig:
    """Retorna configuração baseada na variável de ambiente"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionConfig()
    else:
        return DevelopmentConfig()