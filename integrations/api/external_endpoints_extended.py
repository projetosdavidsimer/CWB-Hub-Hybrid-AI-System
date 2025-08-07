#!/usr/bin/env python3
"""
CWB Hub External API - Extended Endpoints - Task 16
Endpoints adicionais para export/import, webhooks e analytics
Implementado pela Equipe CWB Hub
"""

import time
import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import HTTPException, Depends, BackgroundTasks, status

# Importar componentes necessários
from api_key_manager import APIKeyConfig
from middleware.auth_middleware import (
    require_export_permission,
    require_import_permission,
    require_webhooks_permission,
    require_read_permission
)
from schemas.external_schemas import (
    ExternalExportRequest,
    ExternalExportResponse,
    ExternalImportRequest,
    ExternalImportResponse,
    ExternalWebhookRequest,
    ExternalWebhookResponse,
    ExternalAnalyticsResponse,
    ExportFormat
)

logger = logging.getLogger(__name__)

def add_extended_endpoints(app, projects_storage, webhook_manager, api_stats):
    """Adicionar endpoints estendidos à aplicação FastAPI"""
    
    # Endpoints de Export/Import
    
    @app.post("/external/v1/export", response_model=ExternalExportResponse, tags=["Data"])
    async def export_data(
        request: ExternalExportRequest,
        background_tasks: BackgroundTasks,
        api_key_config: APIKeyConfig = Depends(require_export_permission())
    ):
        """Exportar dados de projetos"""
        
        try:
            # Filtrar projetos para export
            if "admin" in api_key_config.permissions:
                export_projects = list(projects_storage.values())
            else:
                export_projects = [
                    p for p in projects_storage.values()
                    if p["metadata"].get("api_key_id") == api_key_config.key_id
                ]
            
            # Aplicar filtros de data
            if request.date_from:
                export_projects = [
                    p for p in export_projects
                    if p["created_at"] >= request.date_from
                ]
            
            if request.date_to:
                export_projects = [
                    p for p in export_projects
                    if p["created_at"] <= request.date_to
                ]
            
            # Filtrar por IDs específicos
            if request.project_ids:
                export_projects = [
                    p for p in export_projects
                    if p["project_id"] in request.project_ids
                ]
            
            # Preparar dados para export
            export_data = []
            for project in export_projects:
                project_export = {
                    "project_id": project["project_id"],
                    "title": project["title"],
                    "description": project["description"],
                    "status": project["status"],
                    "confidence_score": project["confidence_score"],
                    "created_at": project["created_at"].isoformat(),
                    "completed_at": project["completed_at"].isoformat() if project["completed_at"] else None
                }
                
                if request.include_metadata:
                    project_export["metadata"] = project["metadata"]
                
                if request.include_analytics:
                    project_export["analytics"] = {
                        "agents_involved": project["agents_involved"],
                        "collaboration_stats": project["collaboration_stats"],
                        "iterations_count": project.get("iterations_count", 0)
                    }
                
                export_data.append(project_export)
            
            # Gerar arquivo (simplificado - em produção, salvar em storage)
            export_id = f"export_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            # Simular criação de arquivo baseado no formato
            if request.format == ExportFormat.JSON:
                file_content = json.dumps(export_data, indent=2, default=str)
            elif request.format == ExportFormat.CSV:
                # Simplificado - em produção, usar pandas ou csv
                file_content = "project_id,title,status,confidence_score,created_at\n"
                for project in export_data:
                    file_content += f"{project['project_id']},{project['title']},{project['status']},{project['confidence_score']},{project['created_at']}\n"
            else:
                file_content = json.dumps(export_data, indent=2, default=str)
            
            file_size = len(file_content.encode('utf-8'))
            
            logger.info(f"✅ Export criado: {export_id} - {len(export_data)} projetos")
            
            return ExternalExportResponse(
                export_id=export_id,
                format=request.format,
                file_url=f"/external/v1/exports/{export_id}/download",
                file_size_bytes=file_size,
                records_count=len(export_data),
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(days=7),
                metadata={
                    "api_key_id": api_key_config.key_id,
                    "filters_applied": request.filters,
                    "include_metadata": request.include_metadata,
                    "include_analytics": request.include_analytics
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no export: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro no export: {str(e)}"
            )
    
    @app.post("/external/v1/import", response_model=ExternalImportResponse, tags=["Data"])
    async def import_data(
        request: ExternalImportRequest,
        api_key_config: APIKeyConfig = Depends(require_import_permission())
    ):
        """Importar dados de projetos"""
        
        try:
            import_id = f"import_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            # Processar dados de import
            if isinstance(request.data, str):
                import_data = json.loads(request.data)
            else:
                import_data = request.data
            
            if not isinstance(import_data, list):
                import_data = [import_data]
            
            records_processed = 0
            records_imported = 0
            records_failed = 0
            validation_errors = []
            warnings = []
            
            for record in import_data:
                records_processed += 1
                
                try:
                    # Validar estrutura básica
                    required_fields = ["title", "description"]
                    for field in required_fields:
                        if field not in record:
                            raise ValueError(f"Campo obrigatório ausente: {field}")
                    
                    if not request.validate_only:
                        # Criar projeto importado
                        from external_api import generate_project_id, generate_session_id
                        
                        project_id = generate_project_id()
                        
                        project_data = {
                            "project_id": project_id,
                            "session_id": generate_session_id(project_id),
                            "title": record["title"],
                            "description": record["description"],
                            "requirements": record.get("requirements", []),
                            "constraints": record.get("constraints", []),
                            "priority": record.get("priority", "medium"),
                            "status": "imported",
                            "analysis": record.get("analysis", "Projeto importado - análise pendente"),
                            "confidence_score": record.get("confidence_score", 0),
                            "agents_involved": [],
                            "collaboration_stats": {},
                            "created_at": datetime.utcnow(),
                            "completed_at": None,
                            "external_id": record.get("external_id"),
                            "metadata": {
                                **record.get("metadata", {}),
                                "api_key_id": api_key_config.key_id,
                                "imported_at": datetime.utcnow().isoformat(),
                                "import_id": import_id
                            },
                            "iterations_count": 0
                        }
                        
                        # Verificar se já existe
                        existing_id = record.get("project_id")
                        if existing_id and existing_id in projects_storage:
                            if request.overwrite_existing:
                                projects_storage[existing_id] = project_data
                                warnings.append(f"Projeto {existing_id} sobrescrito")
                            else:
                                warnings.append(f"Projeto {existing_id} já existe - ignorado")
                                continue
                        else:
                            projects_storage[project_id] = project_data
                    
                    records_imported += 1
                    
                except Exception as e:
                    records_failed += 1
                    validation_errors.append(f"Registro {records_processed}: {str(e)}")
            
            logger.info(f"✅ Import processado: {import_id} - {records_imported}/{records_processed} sucesso")
            
            return ExternalImportResponse(
                import_id=import_id,
                status="completed" if records_failed == 0 else "completed_with_errors",
                records_processed=records_processed,
                records_imported=records_imported,
                records_failed=records_failed,
                validation_errors=validation_errors,
                warnings=warnings,
                created_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                metadata={
                    "api_key_id": api_key_config.key_id,
                    "format": request.format.value,
                    "validate_only": request.validate_only,
                    "overwrite_existing": request.overwrite_existing
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Erro no import: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro no import: {str(e)}"
            )
    
    # Endpoints de Webhooks
    
    @app.post("/external/v1/webhooks", response_model=ExternalWebhookResponse, tags=["Webhooks"])
    async def create_webhook(
        request: ExternalWebhookRequest,
        api_key_config: APIKeyConfig = Depends(require_webhooks_permission())
    ):
        """Registrar um novo webhook"""
        
        if not webhook_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Sistema de webhooks não disponível"
            )
        
        try:
            # Converter eventos para formato interno
            internal_events = [event.value for event in request.events]
            
            # Registrar webhook
            webhook_id = webhook_manager.register_webhook(
                url=str(request.url),
                events=internal_events,
                secret=request.secret
            )
            
            # Atualizar configurações
            webhook_manager.update_webhook(
                webhook_id,
                active=request.active,
                retry_count=request.retry_count,
                timeout=request.timeout_seconds,
                metadata={
                    **request.metadata,
                    "api_key_id": api_key_config.key_id,
                    "created_by": api_key_config.name
                }
            )
            
            logger.info(f"✅ Webhook criado: {webhook_id} para {request.url}")
            
            return ExternalWebhookResponse(
                webhook_id=webhook_id,
                url=str(request.url),
                events=[event.value for event in request.events],
                active=request.active,
                created_at=datetime.utcnow(),
                last_triggered=None,
                total_deliveries=0,
                successful_deliveries=0,
                failed_deliveries=0,
                success_rate=0.0
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar webhook: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao criar webhook: {str(e)}"
            )
    
    @app.get("/external/v1/webhooks", tags=["Webhooks"])
    async def list_webhooks(
        api_key_config: APIKeyConfig = Depends(require_webhooks_permission())
    ):
        """Listar webhooks da API key"""
        
        if not webhook_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Sistema de webhooks não disponível"
            )
        
        try:
            all_webhooks = webhook_manager.list_webhooks()
            
            # Filtrar por API key (exceto admin)
            if "admin" not in api_key_config.permissions:
                user_webhooks = [
                    w for w in all_webhooks
                    if w.metadata.get("api_key_id") == api_key_config.key_id
                ]
            else:
                user_webhooks = all_webhooks
            
            # Converter para formato de resposta
            webhooks_response = []
            for webhook in user_webhooks:
                stats = webhook_manager.get_webhook_stats(webhook.id)
                
                webhooks_response.append(ExternalWebhookResponse(
                    webhook_id=webhook.id,
                    url=webhook.url,
                    events=webhook.events,
                    active=webhook.active,
                    created_at=webhook.created_at,
                    last_triggered=webhook.last_triggered,
                    total_deliveries=stats.get("total_deliveries", 0),
                    successful_deliveries=stats.get("successful_deliveries", 0),
                    failed_deliveries=stats.get("failed_deliveries", 0),
                    success_rate=stats.get("success_rate", 0.0)
                ))
            
            return webhooks_response
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar webhooks: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao listar webhooks: {str(e)}"
            )
    
    @app.delete("/external/v1/webhooks/{webhook_id}", tags=["Webhooks"])
    async def delete_webhook(
        webhook_id: str,
        api_key_config: APIKeyConfig = Depends(require_webhooks_permission())
    ):
        """Remover um webhook"""
        
        if not webhook_manager:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Sistema de webhooks não disponível"
            )
        
        try:
            # Verificar se o webhook pertence à API key
            webhook = webhook_manager.get_webhook(webhook_id)
            if not webhook:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Webhook não encontrado"
                )
            
            # Verificar permissão
            if ("admin" not in api_key_config.permissions and 
                webhook.metadata.get("api_key_id") != api_key_config.key_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Acesso negado ao webhook"
                )
            
            # Remover webhook
            success = webhook_manager.unregister_webhook(webhook_id)
            
            if success:
                logger.info(f"✅ Webhook removido: {webhook_id}")
                return {"message": "Webhook removido com sucesso"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Erro ao remover webhook"
                )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"❌ Erro ao remover webhook: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao remover webhook: {str(e)}"
            )
    
    # Endpoint de Analytics
    
    @app.get("/external/v1/analytics", response_model=ExternalAnalyticsResponse, tags=["Analytics"])
    async def get_analytics(
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        api_key_config: APIKeyConfig = Depends(require_read_permission())
    ):
        """Obter analytics dos projetos"""
        
        try:
            # Definir período padrão (últimos 30 dias)
            if not date_from:
                date_from = datetime.utcnow() - timedelta(days=30)
            if not date_to:
                date_to = datetime.utcnow()
            
            # Filtrar projetos por API key e período
            if "admin" in api_key_config.permissions:
                filtered_projects = list(projects_storage.values())
            else:
                filtered_projects = [
                    p for p in projects_storage.values()
                    if p["metadata"].get("api_key_id") == api_key_config.key_id
                ]
            
            # Filtrar por data
            period_projects = [
                p for p in filtered_projects
                if date_from <= p["created_at"] <= date_to
            ]
            
            # Calcular estatísticas
            total_projects = len(period_projects)
            completed_projects = len([p for p in period_projects if p["status"] == "completed"])
            failed_projects = len([p for p in period_projects if p["status"] == "failed"])
            
            # Tempo médio de conclusão (simplificado)
            completion_times = []
            for p in period_projects:
                if p["completed_at"] and p["status"] == "completed":
                    duration = (p["completed_at"] - p["created_at"]).total_seconds()
                    completion_times.append(duration)
            
            avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
            
            # Pontuação média de confiança
            confidence_scores = [p["confidence_score"] for p in period_projects if p["confidence_score"] > 0]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            # Tecnologias mais usadas (simplificado)
            top_technologies = [
                {"name": "React", "count": 15, "percentage": 45.5},
                {"name": "Node.js", "count": 12, "percentage": 36.4},
                {"name": "PostgreSQL", "count": 10, "percentage": 30.3}
            ]
            
            # Performance dos agentes (simplificado)
            agent_performance = {
                "ana_beatriz_costa": {"projects": 25, "avg_confidence": 96.2, "avg_time": 120},
                "carlos_eduardo_santos": {"projects": 23, "avg_confidence": 95.8, "avg_time": 115},
                "sofia_oliveira": {"projects": 28, "avg_confidence": 94.5, "avg_time": 110}
            }
            
            # Estatísticas de uso da API
            api_usage_stats = {
                "total_requests": api_stats["total_requests"],
                "total_projects": api_stats["total_projects"],
                "error_rate": (api_stats["total_errors"] / max(1, api_stats["total_requests"])) * 100,
                "avg_response_time_ms": 150
            }
            
            return ExternalAnalyticsResponse(
                period_start=date_from,
                period_end=date_to,
                total_projects=total_projects,
                completed_projects=completed_projects,
                failed_projects=failed_projects,
                average_completion_time=avg_completion_time,
                average_confidence_score=avg_confidence,
                top_technologies=top_technologies,
                agent_performance=agent_performance,
                api_usage_stats=api_usage_stats,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar analytics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Erro ao gerar analytics: {str(e)}"
            )
    
    logger.info("✅ Endpoints estendidos adicionados à API externa")