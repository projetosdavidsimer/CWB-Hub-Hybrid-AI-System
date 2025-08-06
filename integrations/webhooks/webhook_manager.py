#!/usr/bin/env python3
"""
CWB Hub Webhook Manager - Sistema de Webhooks
Gerenciamento completo de webhooks para integrações externas
"""

import os
import json
import asyncio
import hmac
import hashlib
import time
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import logging
from pathlib import Path
import sys

# Adicionar persistence ao path
sys.path.append(str(Path(__file__).parent.parent.parent / "persistence"))

from database.connection import get_async_db_session
from database.models import User, Project, Session, AuditLog

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WebhookEvent(Enum):
    """Tipos de eventos de webhook"""
    PROJECT_CREATED = "project.created"
    PROJECT_COMPLETED = "project.completed"
    PROJECT_UPDATED = "project.updated"
    SESSION_STARTED = "session.started"
    SESSION_COMPLETED = "session.completed"
    FEEDBACK_RECEIVED = "feedback.received"
    ERROR_OCCURRED = "error.occurred"
    USER_REGISTERED = "user.registered"
    INTEGRATION_CONNECTED = "integration.connected"


class WebhookStatus(Enum):
    """Status de entrega do webhook"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETRYING = "retrying"
    EXPIRED = "expired"


@dataclass
class WebhookPayload:
    """Payload do webhook"""
    event: str
    timestamp: datetime
    data: Dict[str, Any]
    user_id: Optional[int] = None
    project_id: Optional[int] = None
    session_id: Optional[str] = None


@dataclass
class WebhookEndpoint:
    """Configuração de endpoint de webhook"""
    id: str
    url: str
    secret: str
    events: List[str]
    active: bool = True
    retry_count: int = 3
    timeout: int = 30
    created_at: datetime = None
    last_delivery: Optional[datetime] = None


@dataclass
class WebhookDelivery:
    """Registro de entrega de webhook"""
    id: str
    endpoint_id: str
    event: str
    payload: Dict[str, Any]
    status: WebhookStatus
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    attempts: int = 0
    created_at: datetime = None
    delivered_at: Optional[datetime] = None
    next_retry: Optional[datetime] = None


class WebhookManager:
    """Gerenciador de webhooks"""
    
    def __init__(self):
        self.endpoints: Dict[str, WebhookEndpoint] = {}
        self.deliveries: Dict[str, WebhookDelivery] = {}
        self.max_retries = 5
        self.retry_delays = [60, 300, 900, 3600, 7200]  # 1min, 5min, 15min, 1h, 2h
    
    def register_endpoint(self, endpoint: WebhookEndpoint) -> bool:
        """Registra um novo endpoint de webhook"""
        try:
            if not endpoint.created_at:
                endpoint.created_at = datetime.utcnow()
            
            self.endpoints[endpoint.id] = endpoint
            logger.info(f"✅ Endpoint registrado: {endpoint.id} -> {endpoint.url}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar endpoint: {e}")
            return False
    
    def unregister_endpoint(self, endpoint_id: str) -> bool:
        """Remove um endpoint de webhook"""
        try:
            if endpoint_id in self.endpoints:
                del self.endpoints[endpoint_id]
                logger.info(f"✅ Endpoint removido: {endpoint_id}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ Erro ao remover endpoint: {e}")
            return False
    
    def update_endpoint(self, endpoint_id: str, updates: Dict[str, Any]) -> bool:
        """Atualiza configurações de um endpoint"""
        try:
            if endpoint_id not in self.endpoints:
                return False
            
            endpoint = self.endpoints[endpoint_id]
            for key, value in updates.items():
                if hasattr(endpoint, key):
                    setattr(endpoint, key, value)
            
            logger.info(f"✅ Endpoint atualizado: {endpoint_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar endpoint: {e}")
            return False
    
    async def send_webhook(self, event: WebhookEvent, data: Dict[str, Any], 
                          user_id: Optional[int] = None, project_id: Optional[int] = None,
                          session_id: Optional[str] = None) -> List[str]:
        """Envia webhook para todos os endpoints interessados"""
        
        # Criar payload
        payload = WebhookPayload(
            event=event.value,
            timestamp=datetime.utcnow(),
            data=data,
            user_id=user_id,
            project_id=project_id,
            session_id=session_id
        )
        
        delivery_ids = []
        
        # Enviar para endpoints interessados
        for endpoint_id, endpoint in self.endpoints.items():
            if endpoint.active and event.value in endpoint.events:
                delivery_id = await self._deliver_webhook(endpoint, payload)
                if delivery_id:
                    delivery_ids.append(delivery_id)
        
        return delivery_ids
    
    async def _deliver_webhook(self, endpoint: WebhookEndpoint, payload: WebhookPayload) -> Optional[str]:
        """Entrega webhook para um endpoint específico"""
        
        # Criar registro de entrega
        delivery_id = f"delivery_{int(time.time())}_{endpoint.id}"
        delivery = WebhookDelivery(
            id=delivery_id,
            endpoint_id=endpoint.id,
            event=payload.event,
            payload=asdict(payload),
            status=WebhookStatus.PENDING,
            created_at=datetime.utcnow()
        )
        
        self.deliveries[delivery_id] = delivery
        
        # Tentar entrega
        success = await self._attempt_delivery(endpoint, delivery, payload)
        
        if success:
            delivery.status = WebhookStatus.DELIVERED
            delivery.delivered_at = datetime.utcnow()
            endpoint.last_delivery = datetime.utcnow()
        else:
            delivery.status = WebhookStatus.FAILED
            # Agendar retry se necessário
            if delivery.attempts < self.max_retries:
                delivery.status = WebhookStatus.RETRYING
                delay = self.retry_delays[min(delivery.attempts, len(self.retry_delays) - 1)]
                delivery.next_retry = datetime.utcnow() + timedelta(seconds=delay)
        
        return delivery_id
    
    async def _attempt_delivery(self, endpoint: WebhookEndpoint, delivery: WebhookDelivery, 
                               payload: WebhookPayload) -> bool:
        """Tenta entregar webhook"""
        
        try:
            delivery.attempts += 1
            
            # Preparar dados
            payload_json = json.dumps(asdict(payload), default=str)
            
            # Criar assinatura HMAC
            signature = self._create_signature(payload_json, endpoint.secret)
            
            # Headers
            headers = {
                'Content-Type': 'application/json',
                'X-CWBHub-Signature': signature,
                'X-CWBHub-Event': payload.event,
                'X-CWBHub-Delivery': delivery.id,
                'User-Agent': 'CWBHub-Webhooks/1.0'
            }
            
            # Fazer requisição
            timeout = aiohttp.ClientTimeout(total=endpoint.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(endpoint.url, data=payload_json, headers=headers) as response:
                    delivery.response_code = response.status
                    delivery.response_body = await response.text()
                    
                    # Considerar sucesso se status 2xx
                    if 200 <= response.status < 300:
                        logger.info(f"✅ Webhook entregue: {delivery.id} -> {endpoint.url} ({response.status})")
                        return True
                    else:
                        logger.warning(f"⚠️ Webhook falhou: {delivery.id} -> {endpoint.url} ({response.status})")
                        return False
        
        except asyncio.TimeoutError:
            logger.error(f"⏰ Timeout webhook: {delivery.id} -> {endpoint.url}")
            delivery.response_body = "Request timeout"
            return False
        
        except Exception as e:
            logger.error(f"❌ Erro webhook: {delivery.id} -> {endpoint.url}: {e}")
            delivery.response_body = str(e)
            return False
    
    def _create_signature(self, payload: str, secret: str) -> str:
        """Cria assinatura HMAC para webhook"""
        signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    def verify_signature(self, payload: str, signature: str, secret: str) -> bool:
        """Verifica assinatura HMAC de webhook"""
        expected_signature = self._create_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)
    
    async def retry_failed_deliveries(self):
        """Reprocessa entregas falhadas"""
        now = datetime.utcnow()
        retried = 0
        
        for delivery in self.deliveries.values():
            if (delivery.status == WebhookStatus.RETRYING and 
                delivery.next_retry and 
                delivery.next_retry <= now and
                delivery.attempts < self.max_retries):
                
                endpoint = self.endpoints.get(delivery.endpoint_id)
                if endpoint and endpoint.active:
                    # Recriar payload
                    payload = WebhookPayload(**delivery.payload)
                    
                    # Tentar novamente
                    success = await self._attempt_delivery(endpoint, delivery, payload)
                    
                    if success:
                        delivery.status = WebhookStatus.DELIVERED
                        delivery.delivered_at = now
                        endpoint.last_delivery = now
                    else:
                        if delivery.attempts >= self.max_retries:
                            delivery.status = WebhookStatus.EXPIRED
                        else:
                            delay = self.retry_delays[min(delivery.attempts, len(self.retry_delays) - 1)]
                            delivery.next_retry = now + timedelta(seconds=delay)
                    
                    retried += 1
        
        if retried > 0:
            logger.info(f"🔄 Reprocessadas {retried} entregas de webhook")
    
    def get_endpoint_stats(self, endpoint_id: str) -> Dict[str, Any]:
        """Obtém estatísticas de um endpoint"""
        if endpoint_id not in self.endpoints:
            return {}
        
        endpoint = self.endpoints[endpoint_id]
        deliveries = [d for d in self.deliveries.values() if d.endpoint_id == endpoint_id]
        
        total = len(deliveries)
        delivered = len([d for d in deliveries if d.status == WebhookStatus.DELIVERED])
        failed = len([d for d in deliveries if d.status == WebhookStatus.FAILED])
        pending = len([d for d in deliveries if d.status in [WebhookStatus.PENDING, WebhookStatus.RETRYING]])
        
        return {
            "endpoint_id": endpoint_id,
            "url": endpoint.url,
            "active": endpoint.active,
            "events": endpoint.events,
            "total_deliveries": total,
            "successful_deliveries": delivered,
            "failed_deliveries": failed,
            "pending_deliveries": pending,
            "success_rate": (delivered / total * 100) if total > 0 else 0,
            "last_delivery": endpoint.last_delivery,
            "created_at": endpoint.created_at
        }
    
    def get_delivery_details(self, delivery_id: str) -> Optional[Dict[str, Any]]:
        """Obtém detalhes de uma entrega"""
        if delivery_id not in self.deliveries:
            return None
        
        delivery = self.deliveries[delivery_id]
        return asdict(delivery)
    
    def cleanup_old_deliveries(self, days: int = 30):
        """Remove entregas antigas"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        old_deliveries = [
            delivery_id for delivery_id, delivery in self.deliveries.items()
            if delivery.created_at < cutoff
        ]
        
        for delivery_id in old_deliveries:
            del self.deliveries[delivery_id]
        
        logger.info(f"🧹 Removidas {len(old_deliveries)} entregas antigas")


# Instância global do gerenciador
webhook_manager = WebhookManager()


# Funções de conveniência
async def send_project_created_webhook(project_id: int, user_id: int, project_data: Dict[str, Any]):
    """Envia webhook de projeto criado"""
    return await webhook_manager.send_webhook(
        WebhookEvent.PROJECT_CREATED,
        project_data,
        user_id=user_id,
        project_id=project_id
    )


async def send_session_completed_webhook(session_id: str, user_id: int, session_data: Dict[str, Any]):
    """Envia webhook de sessão completada"""
    return await webhook_manager.send_webhook(
        WebhookEvent.SESSION_COMPLETED,
        session_data,
        user_id=user_id,
        session_id=session_id
    )


async def send_error_webhook(error_data: Dict[str, Any], user_id: Optional[int] = None):
    """Envia webhook de erro"""
    return await webhook_manager.send_webhook(
        WebhookEvent.ERROR_OCCURRED,
        error_data,
        user_id=user_id
    )


# Função para inicializar webhooks padrão
def initialize_default_webhooks():
    """Inicializa webhooks padrão para desenvolvimento"""
    
    # Webhook de desenvolvimento local
    dev_endpoint = WebhookEndpoint(
        id="dev_local",
        url="http://localhost:3000/webhooks/cwbhub",
        secret="dev_secret_key_2025",
        events=[event.value for event in WebhookEvent],
        active=True
    )
    
    webhook_manager.register_endpoint(dev_endpoint)
    
    # Webhook para Slack (se configurado)
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if slack_webhook_url:
        slack_endpoint = WebhookEndpoint(
            id="slack_notifications",
            url=slack_webhook_url,
            secret=os.getenv("SLACK_WEBHOOK_SECRET", "slack_secret"),
            events=[
                WebhookEvent.PROJECT_COMPLETED.value,
                WebhookEvent.ERROR_OCCURRED.value
            ],
            active=True
        )
        webhook_manager.register_endpoint(slack_endpoint)
    
    # Webhook para Teams (se configurado)
    teams_webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    if teams_webhook_url:
        teams_endpoint = WebhookEndpoint(
            id="teams_notifications",
            url=teams_webhook_url,
            secret=os.getenv("TEAMS_WEBHOOK_SECRET", "teams_secret"),
            events=[
                WebhookEvent.PROJECT_COMPLETED.value,
                WebhookEvent.SESSION_COMPLETED.value
            ],
            active=True
        )
        webhook_manager.register_endpoint(teams_endpoint)


# Task para retry automático
async def webhook_retry_task():
    """Task para reprocessar webhooks falhados"""
    while True:
        try:
            await webhook_manager.retry_failed_deliveries()
            await asyncio.sleep(300)  # 5 minutos
        except Exception as e:
            logger.error(f"❌ Erro no retry task: {e}")
            await asyncio.sleep(60)  # 1 minuto em caso de erro


if __name__ == "__main__":
    # Teste do sistema de webhooks
    print("🔗 CWB HUB WEBHOOK MANAGER")
    print("=" * 40)
    
    async def test_webhooks():
        # Inicializar webhooks padrão
        initialize_default_webhooks()
        
        # Testar envio de webhook
        test_data = {
            "project_id": 123,
            "title": "Sistema de E-commerce",
            "status": "completed",
            "confidence": 94.4
        }
        
        delivery_ids = await send_project_created_webhook(123, 1, test_data)
        print(f"✅ Webhooks enviados: {len(delivery_ids)}")
        
        # Mostrar estatísticas
        for endpoint_id in webhook_manager.endpoints.keys():
            stats = webhook_manager.get_endpoint_stats(endpoint_id)
            print(f"📊 {endpoint_id}: {stats['success_rate']:.1f}% success rate")
    
    asyncio.run(test_webhooks())
    print("✅ Sistema de webhooks testado com sucesso!")