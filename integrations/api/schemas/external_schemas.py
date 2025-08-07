#!/usr/bin/env python3
"""
CWB Hub External API Schemas - Task 16
Schemas Pydantic para validação da API externa
Implementado pela Equipe CWB Hub
"""

from pydantic import BaseModel, Field, validator, HttpUrl
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class ProjectPriority(str, Enum):
    """Níveis de prioridade do projeto"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ProjectStatus(str, Enum):
    """Status do projeto"""
    PENDING = "pending"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExportFormat(str, Enum):
    """Formatos de export disponíveis"""
    JSON = "json"
    CSV = "csv"
    XML = "xml"
    PDF = "pdf"

class WebhookEvent(str, Enum):
    """Eventos de webhook disponíveis"""
    PROJECT_CREATED = "project.created"
    PROJECT_COMPLETED = "project.completed"
    PROJECT_FAILED = "project.failed"
    ANALYSIS_STARTED = "analysis.started"
    ANALYSIS_COMPLETED = "analysis.completed"
    ITERATION_COMPLETED = "iteration.completed"

# Schemas de Request

class ExternalProjectRequest(BaseModel):
    """Solicitação de análise de projeto via API externa"""
    title: str = Field(..., min_length=1, max_length=200, description="Título do projeto")
    description: str = Field(..., min_length=10, max_length=5000, description="Descrição detalhada")
    requirements: List[str] = Field(..., min_items=1, max_items=50, description="Lista de requisitos")
    constraints: Optional[List[str]] = Field(default=[], max_items=20, description="Restrições do projeto")
    priority: ProjectPriority = Field(default=ProjectPriority.MEDIUM, description="Prioridade do projeto")
    budget_range: Optional[str] = Field(default=None, max_length=100, description="Faixa de orçamento")
    timeline: Optional[str] = Field(default=None, max_length=100, description="Prazo esperado")
    technology_preferences: Optional[List[str]] = Field(default=[], max_items=10, description="Tecnologias preferidas")
    target_audience: Optional[str] = Field(default=None, max_length=500, description="Público-alvo")
    business_goals: Optional[List[str]] = Field(default=[], max_items=10, description="Objetivos de negócio")
    external_id: Optional[str] = Field(default=None, max_length=100, description="ID no sistema externo")
    callback_url: Optional[HttpUrl] = Field(default=None, description="URL para callback")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadados adicionais")
    
    @validator('requirements')
    def validate_requirements(cls, v):
        """Validar requisitos"""
        for req in v:
            if len(req.strip()) < 3:
                raise ValueError("Cada requisito deve ter pelo menos 3 caracteres")
        return v
    
    @validator('metadata')
    def validate_metadata(cls, v):
        """Validar metadados"""
        if len(str(v)) > 2000:  # Limitar tamanho dos metadados
            raise ValueError("Metadados muito grandes")
        return v

class ExternalIterationRequest(BaseModel):
    """Solicitação de iteração de projeto"""
    feedback: str = Field(..., min_length=10, max_length=2000, description="Feedback para refinamento")
    focus_areas: Optional[List[str]] = Field(default=[], max_items=5, description="Áreas de foco")
    additional_requirements: Optional[List[str]] = Field(default=[], max_items=10, description="Requisitos adicionais")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadados da iteração")

class ExternalExportRequest(BaseModel):
    """Solicitação de export de dados"""
    format: ExportFormat = Field(..., description="Formato do export")
    date_from: Optional[datetime] = Field(default=None, description="Data inicial")
    date_to: Optional[datetime] = Field(default=None, description="Data final")
    project_ids: Optional[List[str]] = Field(default=[], max_items=100, description="IDs específicos")
    include_metadata: bool = Field(default=True, description="Incluir metadados")
    include_analytics: bool = Field(default=False, description="Incluir analytics")
    filters: Optional[Dict[str, Any]] = Field(default={}, description="Filtros adicionais")

class ExternalImportRequest(BaseModel):
    """Solicitação de import de dados"""
    format: ExportFormat = Field(..., description="Formato dos dados")
    data: Union[str, Dict[str, Any], List[Dict[str, Any]]] = Field(..., description="Dados para import")
    validate_only: bool = Field(default=False, description="Apenas validar sem importar")
    overwrite_existing: bool = Field(default=False, description="Sobrescrever existentes")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadados do import")

class ExternalWebhookRequest(BaseModel):
    """Solicitação de configuração de webhook"""
    url: HttpUrl = Field(..., description="URL do webhook")
    events: List[WebhookEvent] = Field(..., min_items=1, description="Eventos para escutar")
    secret: Optional[str] = Field(default=None, min_length=8, max_length=100, description="Chave secreta")
    active: bool = Field(default=True, description="Webhook ativo")
    retry_count: int = Field(default=3, ge=0, le=10, description="Tentativas de retry")
    timeout_seconds: int = Field(default=30, ge=5, le=300, description="Timeout em segundos")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Metadados do webhook")

# Schemas de Response

class ExternalProjectResponse(BaseModel):
    """Resposta de análise de projeto"""
    project_id: str = Field(..., description="ID único do projeto")
    session_id: str = Field(..., description="ID da sessão de análise")
    title: str = Field(..., description="Título do projeto")
    status: ProjectStatus = Field(..., description="Status atual")
    analysis: str = Field(..., description="Análise completa da equipe")
    confidence_score: float = Field(..., ge=0, le=100, description="Pontuação de confiança")
    estimated_timeline: Optional[str] = Field(default=None, description="Timeline estimado")
    estimated_budget: Optional[str] = Field(default=None, description="Orçamento estimado")
    recommended_technologies: List[str] = Field(default=[], description="Tecnologias recomendadas")
    risk_assessment: Optional[str] = Field(default=None, description="Avaliação de riscos")
    next_steps: List[str] = Field(default=[], description="Próximos passos recomendados")
    agents_involved: List[str] = Field(..., description="Agentes que participaram")
    collaboration_stats: Dict[str, Any] = Field(..., description="Estatísticas de colaboração")
    created_at: datetime = Field(..., description="Data de criação")
    completed_at: Optional[datetime] = Field(default=None, description="Data de conclusão")
    external_id: Optional[str] = Field(default=None, description="ID no sistema externo")
    metadata: Dict[str, Any] = Field(default={}, description="Metadados do projeto")

class ExternalIterationResponse(BaseModel):
    """Resposta de iteração"""
    project_id: str = Field(..., description="ID do projeto")
    session_id: str = Field(..., description="ID da sessão")
    iteration_number: int = Field(..., ge=1, description="Número da iteração")
    refined_analysis: str = Field(..., description="Análise refinada")
    confidence_improvement: float = Field(..., description="Melhoria na confiança")
    changes_summary: str = Field(..., description="Resumo das mudanças")
    updated_timeline: Optional[str] = Field(default=None, description="Timeline atualizado")
    updated_budget: Optional[str] = Field(default=None, description="Orçamento atualizado")
    additional_recommendations: List[str] = Field(default=[], description="Recomendações adicionais")
    timestamp: datetime = Field(..., description="Timestamp da iteração")
    metadata: Dict[str, Any] = Field(default={}, description="Metadados da iteração")

class ExternalProjectStatus(BaseModel):
    """Status detalhado de um projeto"""
    project_id: str = Field(..., description="ID do projeto")
    session_id: str = Field(..., description="ID da sessão")
    status: ProjectStatus = Field(..., description="Status atual")
    progress_percentage: float = Field(..., ge=0, le=100, description="Percentual de progresso")
    current_phase: str = Field(..., description="Fase atual")
    phases_completed: List[str] = Field(default=[], description="Fases concluídas")
    estimated_completion: Optional[datetime] = Field(default=None, description="Conclusão estimada")
    agents_working: List[str] = Field(default=[], description="Agentes trabalhando")
    last_activity: datetime = Field(..., description="Última atividade")
    iterations_count: int = Field(default=0, ge=0, description="Número de iterações")
    messages_count: int = Field(default=0, ge=0, description="Número de mensagens")
    external_id: Optional[str] = Field(default=None, description="ID no sistema externo")

class ExternalExportResponse(BaseModel):
    """Resposta de export"""
    export_id: str = Field(..., description="ID do export")
    format: ExportFormat = Field(..., description="Formato do export")
    file_url: Optional[str] = Field(default=None, description="URL do arquivo")
    file_size_bytes: int = Field(..., ge=0, description="Tamanho do arquivo")
    records_count: int = Field(..., ge=0, description="Número de registros")
    created_at: datetime = Field(..., description="Data de criação")
    expires_at: Optional[datetime] = Field(default=None, description="Data de expiração")
    metadata: Dict[str, Any] = Field(default={}, description="Metadados do export")

class ExternalImportResponse(BaseModel):
    """Resposta de import"""
    import_id: str = Field(..., description="ID do import")
    status: str = Field(..., description="Status do import")
    records_processed: int = Field(..., ge=0, description="Registros processados")
    records_imported: int = Field(..., ge=0, description="Registros importados")
    records_failed: int = Field(..., ge=0, description="Registros falharam")
    validation_errors: List[str] = Field(default=[], description="Erros de validação")
    warnings: List[str] = Field(default=[], description="Avisos")
    created_at: datetime = Field(..., description="Data de criação")
    completed_at: Optional[datetime] = Field(default=None, description="Data de conclusão")
    metadata: Dict[str, Any] = Field(default={}, description="Metadados do import")

class ExternalWebhookResponse(BaseModel):
    """Resposta de webhook"""
    webhook_id: str = Field(..., description="ID do webhook")
    url: str = Field(..., description="URL do webhook")
    events: List[str] = Field(..., description="Eventos configurados")
    active: bool = Field(..., description="Status ativo")
    created_at: datetime = Field(..., description="Data de criação")
    last_triggered: Optional[datetime] = Field(default=None, description="Último disparo")
    total_deliveries: int = Field(default=0, ge=0, description="Total de entregas")
    successful_deliveries: int = Field(default=0, ge=0, description="Entregas bem-sucedidas")
    failed_deliveries: int = Field(default=0, ge=0, description="Entregas falharam")
    success_rate: float = Field(default=0, ge=0, le=100, description="Taxa de sucesso")

class ExternalHealthResponse(BaseModel):
    """Resposta de health check"""
    status: str = Field(..., description="Status geral")
    timestamp: datetime = Field(..., description="Timestamp do check")
    version: str = Field(..., description="Versão da API")
    uptime_seconds: int = Field(..., ge=0, description="Uptime em segundos")
    services: Dict[str, str] = Field(..., description="Status dos serviços")
    performance: Dict[str, Any] = Field(..., description="Métricas de performance")
    rate_limits: Dict[str, Any] = Field(..., description="Informações de rate limit")

class ExternalErrorResponse(BaseModel):
    """Resposta de erro padronizada"""
    error_code: str = Field(..., description="Código do erro")
    error_message: str = Field(..., description="Mensagem do erro")
    error_details: Optional[Dict[str, Any]] = Field(default=None, description="Detalhes do erro")
    timestamp: datetime = Field(..., description="Timestamp do erro")
    request_id: Optional[str] = Field(default=None, description="ID da requisição")
    documentation_url: Optional[str] = Field(default=None, description="URL da documentação")

# Schemas de Analytics

class ExternalAnalyticsResponse(BaseModel):
    """Resposta de analytics"""
    period_start: datetime = Field(..., description="Início do período")
    period_end: datetime = Field(..., description="Fim do período")
    total_projects: int = Field(..., ge=0, description="Total de projetos")
    completed_projects: int = Field(..., ge=0, description="Projetos concluídos")
    failed_projects: int = Field(..., ge=0, description="Projetos falharam")
    average_completion_time: float = Field(..., ge=0, description="Tempo médio de conclusão")
    average_confidence_score: float = Field(..., ge=0, le=100, description="Pontuação média de confiança")
    top_technologies: List[Dict[str, Any]] = Field(default=[], description="Tecnologias mais usadas")
    agent_performance: Dict[str, Any] = Field(default={}, description="Performance dos agentes")
    api_usage_stats: Dict[str, Any] = Field(default={}, description="Estatísticas de uso da API")
    generated_at: datetime = Field(..., description="Data de geração")

# Schemas de Paginação

class PaginationParams(BaseModel):
    """Parâmetros de paginação"""
    page: int = Field(default=1, ge=1, description="Número da página")
    page_size: int = Field(default=20, ge=1, le=100, description="Tamanho da página")
    sort_by: Optional[str] = Field(default="created_at", description="Campo para ordenação")
    sort_order: Optional[str] = Field(default="desc", regex="^(asc|desc)$", description="Ordem de classificação")

class PaginatedResponse(BaseModel):
    """Resposta paginada"""
    items: List[Any] = Field(..., description="Itens da página")
    total_items: int = Field(..., ge=0, description="Total de itens")
    total_pages: int = Field(..., ge=0, description="Total de páginas")
    current_page: int = Field(..., ge=1, description="Página atual")
    page_size: int = Field(..., ge=1, description="Tamanho da página")
    has_next: bool = Field(..., description="Tem próxima página")
    has_previous: bool = Field(..., description="Tem página anterior")