"""
Modelos de Dados para Sistema de Relatórios
Criado pela Equipe Híbrida CWB Hub
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, Field

Base = declarative_base()


class ReportType(str, Enum):
    """Tipos de relatórios disponíveis"""
    EXECUTIVE_SUMMARY = "executive_summary"
    AGENT_PERFORMANCE = "agent_performance"
    COLLABORATION_STATS = "collaboration_stats"
    SYSTEM_USAGE = "system_usage"
    QUALITY_ANALYSIS = "quality_analysis"
    INCIDENT_REPORT = "incident_report"
    CUSTOM = "custom"


class ReportFormat(str, Enum):
    """Formatos de saída dos relatórios"""
    HTML = "html"
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"
    CSV = "csv"


class ReportFrequency(str, Enum):
    """Frequências de geração automática"""
    REAL_TIME = "real_time"
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ON_DEMAND = "on_demand"


class ReportStatus(str, Enum):
    """Status de execução dos relatórios"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# Modelos SQLAlchemy para o banco de dados
class Report(Base):
    """Configurações e metadados dos relatórios"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    report_type = Column(String(50), nullable=False)
    template_name = Column(String(255), nullable=False)
    output_formats = Column(JSON)  # Lista de formatos de saída
    parameters = Column(JSON)  # Parâmetros específicos do relatório
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    
    # Relacionamentos
    executions = relationship("ReportExecution", back_populates="report")
    schedules = relationship("ReportSchedule", back_populates="report")


class ReportExecution(Base):
    """Histórico de execuções dos relatórios"""
    __tablename__ = "report_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    execution_id = Column(String(255), unique=True, index=True)  # UUID
    status = Column(String(50), nullable=False, default=ReportStatus.PENDING)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    output_files = Column(JSON)  # Lista de arquivos gerados
    error_message = Column(Text)
    parameters_used = Column(JSON)
    data_period_start = Column(DateTime)
    data_period_end = Column(DateTime)
    triggered_by = Column(String(255))  # 'schedule', 'manual', 'api'
    
    # Relacionamentos
    report = relationship("Report", back_populates="executions")


class ReportSchedule(Base):
    """Agendamentos automáticos de relatórios"""
    __tablename__ = "report_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    name = Column(String(255), nullable=False)
    frequency = Column(String(50), nullable=False)
    cron_expression = Column(String(255))  # Para agendamentos customizados
    is_active = Column(Boolean, default=True)
    next_run = Column(DateTime)
    last_run = Column(DateTime)
    timezone = Column(String(50), default="America/Sao_Paulo")
    recipients = Column(JSON)  # Lista de emails para envio
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    report = relationship("Report", back_populates="schedules")


class ReportData(Base):
    """Dados agregados para relatórios"""
    __tablename__ = "report_data"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(255), nullable=False, index=True)
    metric_value = Column(Float)
    metric_metadata = Column(JSON)
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False, index=True)
    aggregation_level = Column(String(50))  # 'hour', 'day', 'week', 'month'
    source_system = Column(String(255))  # 'orchestrator', 'agents', 'database'
    created_at = Column(DateTime, default=datetime.utcnow)


class MetricsSnapshot(Base):
    """Snapshots de métricas por período"""
    __tablename__ = "metrics_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    snapshot_time = Column(DateTime, nullable=False, index=True)
    snapshot_type = Column(String(50), nullable=False)  # 'hourly', 'daily', 'weekly'
    metrics_data = Column(JSON, nullable=False)  # Todas as métricas do período
    system_status = Column(String(50))
    total_sessions = Column(Integer)
    active_agents = Column(Integer)
    avg_response_time = Column(Float)
    error_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)


# Modelos Pydantic para APIs
class ReportCreate(BaseModel):
    """Modelo para criação de relatórios"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    report_type: ReportType
    template_name: str
    output_formats: List[ReportFormat] = [ReportFormat.HTML]
    parameters: Optional[Dict[str, Any]] = {}
    is_active: bool = True


class ReportUpdate(BaseModel):
    """Modelo para atualização de relatórios"""
    name: Optional[str] = None
    description: Optional[str] = None
    template_name: Optional[str] = None
    output_formats: Optional[List[ReportFormat]] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ReportResponse(BaseModel):
    """Modelo de resposta para relatórios"""
    id: int
    name: str
    description: Optional[str]
    report_type: ReportType
    template_name: str
    output_formats: List[ReportFormat]
    parameters: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    
    class Config:
        from_attributes = True


class ReportExecutionCreate(BaseModel):
    """Modelo para execução de relatórios"""
    report_id: int
    parameters: Optional[Dict[str, Any]] = {}
    data_period_start: Optional[datetime] = None
    data_period_end: Optional[datetime] = None
    output_formats: Optional[List[ReportFormat]] = None


class ReportExecutionResponse(BaseModel):
    """Modelo de resposta para execuções"""
    id: int
    execution_id: str
    report_id: int
    status: ReportStatus
    started_at: datetime
    completed_at: Optional[datetime]
    duration_seconds: Optional[float]
    output_files: Optional[List[str]]
    error_message: Optional[str]
    data_period_start: Optional[datetime]
    data_period_end: Optional[datetime]
    triggered_by: Optional[str]
    
    class Config:
        from_attributes = True


class ReportScheduleCreate(BaseModel):
    """Modelo para criação de agendamentos"""
    report_id: int
    name: str
    frequency: ReportFrequency
    cron_expression: Optional[str] = None
    recipients: List[str] = []
    timezone: str = "America/Sao_Paulo"
    is_active: bool = True


class ReportScheduleResponse(BaseModel):
    """Modelo de resposta para agendamentos"""
    id: int
    report_id: int
    name: str
    frequency: ReportFrequency
    cron_expression: Optional[str]
    is_active: bool
    next_run: Optional[datetime]
    last_run: Optional[datetime]
    timezone: str
    recipients: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class MetricsData(BaseModel):
    """Modelo para dados de métricas"""
    metric_name: str
    metric_value: float
    metric_metadata: Optional[Dict[str, Any]] = {}
    period_start: datetime
    period_end: datetime
    aggregation_level: str
    source_system: str


class DashboardData(BaseModel):
    """Modelo para dados do dashboard"""
    current_sessions: int
    active_agents: int
    total_users: int
    system_uptime: float
    avg_response_time: float
    error_rate: float
    collaboration_score: float
    last_updated: datetime
    trends: Dict[str, List[float]]  # Tendências das métricas