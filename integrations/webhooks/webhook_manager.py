"""
CWB Hub Webhook Manager - Melhoria #3 Fase 2
Sistema de webhooks configuráveis para eventos do CWB Hub
Implementado pela Equipe CWB Hub + Qodo (Freelancer)
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import httpx
import hashlib
import hmac
from urllib.parse import urlparse

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookEvent(Enum):
    """Tipos de eventos de webhook"""
    ANALYSIS_STARTED = "analysis.started"
    ANALYSIS_COMPLETED = "analysis.completed"
    ANALYSIS_FAILED = "analysis.failed"
    ITERATION_STARTED = "iteration.started"
    ITERATION_COMPLETED = "iteration.completed"
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"
    AGENT_COLLABORATION = "agent.collaboration"
    SYSTEM_HEALTH = "system.health"

@dataclass
class WebhookConfig:
    """Configuração de webhook"""
    id: str
    url: str
    events: List[str]
    secret: Optional[str] = None
    active: bool = True
    retry_count: int = 3
    timeout: int = 30
    created_at: datetime = None
    last_triggered: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

@dataclass
class WebhookPayload:
    """Payload do webhook"""
    event: str
    timestamp: datetime
    data: Dict[str, Any]
    webhook_id: str
    signature: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        return {
            "event": self.event,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "webhook_id": self.webhook_id,
            "signature": self.signature
        }

@dataclass
class WebhookDelivery:
    """Registro de entrega de webhook"""
    id: str
    webhook_id: str
    event: str
    url: str
    status_code: Optional[int] = None
    response_body: Optional[str] = None
    error: Optional[str] = None
    attempt: int = 1
    delivered_at: Optional[datetime] = None
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()

class WebhookManager:
    """Gerenciador de webhooks do CWB Hub"""
    
    def __init__(self):
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.deliveries: List[WebhookDelivery] = []
        self.event_handlers: Dict[str, List[Callable]] = {}
        self.client = httpx.AsyncClient(timeout=30.0)
        
    def register_webhook(self, url: str, events: List[str], secret: Optional[str] = None) -> str:
        """Registrar um novo webhook"""
        webhook_id = self._generate_webhook_id(url)
        
        # Validar URL
        if not self._validate_url(url):
            raise ValueError(f"URL inválida: {url}")
        
        # Validar eventos
        valid_events = [e.value for e in WebhookEvent]
        for event in events:
            if event not in valid_events:
                raise ValueError(f"Evento inválido: {event}. Eventos válidos: {valid_events}")
        
        webhook = WebhookConfig(
            id=webhook_id,
            url=url,
            events=events,
            secret=secret
        )
        
        self.webhooks[webhook_id] = webhook
        
        logger.info(f"Webhook registrado: {webhook_id} para {url}")
        return webhook_id
    
    def unregister_webhook(self, webhook_id: str) -> bool:
        """Remover um webhook"""
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            logger.info(f"Webhook removido: {webhook_id}")
            return True
        return False
    
    def update_webhook(self, webhook_id: str, **kwargs) -> bool:
        """Atualizar configuração de webhook"""
        if webhook_id not in self.webhooks:
            return False
        
        webhook = self.webhooks[webhook_id]
        
        for key, value in kwargs.items():
            if hasattr(webhook, key):
                setattr(webhook, key, value)
        
        logger.info(f"Webhook atualizado: {webhook_id}")
        return True
    
    def get_webhook(self, webhook_id: str) -> Optional[WebhookConfig]:
        """Obter configuração de webhook"""
        return self.webhooks.get(webhook_id)
    
    def list_webhooks(self) -> List[WebhookConfig]:
        """Listar todos os webhooks"""
        return list(self.webhooks.values())
    
    async def trigger_event(self, event: str, data: Dict[str, Any]) -> List[WebhookDelivery]:
        """Disparar evento para webhooks relevantes"""
        deliveries = []
        
        # Encontrar webhooks que escutam este evento
        relevant_webhooks = [
            webhook for webhook in self.webhooks.values()
            if webhook.active and event in webhook.events
        ]
        
        if not relevant_webhooks:
            logger.debug(f"Nenhum webhook registrado para evento: {event}")
            return deliveries
        
        logger.info(f"Disparando evento {event} para {len(relevant_webhooks)} webhooks")
        
        # Disparar para cada webhook
        tasks = []
        for webhook in relevant_webhooks:
            task = self._deliver_webhook(webhook, event, data)
            tasks.append(task)
        
        # Executar em paralelo
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, WebhookDelivery):
                deliveries.append(result)
                self.deliveries.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Erro ao entregar webhook: {result}")
        
        return deliveries
    
    async def _deliver_webhook(self, webhook: WebhookConfig, event: str, data: Dict[str, Any]) -> WebhookDelivery:
        """Entregar webhook com retry"""
        delivery_id = self._generate_delivery_id()
        
        payload = WebhookPayload(
            event=event,
            timestamp=datetime.utcnow(),
            data=data,
            webhook_id=webhook.id
        )
        
        # Gerar assinatura se secret estiver configurado
        if webhook.secret:
            payload.signature = self._generate_signature(payload.to_dict(), webhook.secret)
        
        delivery = WebhookDelivery(
            id=delivery_id,
            webhook_id=webhook.id,
            event=event,
            url=webhook.url
        )
        
        # Tentar entregar com retry
        for attempt in range(1, webhook.retry_count + 1):
            delivery.attempt = attempt
            
            try:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "CWB-Hub-Webhook/1.0",
                    "X-CWB-Event": event,
                    "X-CWB-Delivery": delivery_id,
                    "X-CWB-Timestamp": str(int(payload.timestamp.timestamp()))
                }
                
                if payload.signature:
                    headers["X-CWB-Signature"] = payload.signature
                
                response = await self.client.post(
                    webhook.url,
                    json=payload.to_dict(),
                    headers=headers,
                    timeout=webhook.timeout
                )
                
                delivery.status_code = response.status_code
                delivery.response_body = response.text[:1000]  # Limitar tamanho
                delivery.delivered_at = datetime.utcnow()
                
                # Atualizar último trigger do webhook
                webhook.last_triggered = datetime.utcnow()
                
                if response.status_code < 400:
                    logger.info(f"Webhook entregue com sucesso: {webhook.id} (tentativa {attempt})")
                    break
                else:
                    logger.warning(f"Webhook falhou: {webhook.id} - Status {response.status_code} (tentativa {attempt})")
                    
            except Exception as e:
                delivery.error = str(e)
                logger.error(f"Erro ao entregar webhook {webhook.id} (tentativa {attempt}): {e}")
                
                # Se não é a última tentativa, aguardar antes de tentar novamente
                if attempt < webhook.retry_count:
                    await asyncio.sleep(2 ** attempt)  # Backoff exponencial
        
        return delivery
    
    def get_deliveries(self, webhook_id: Optional[str] = None, limit: int = 100) -> List[WebhookDelivery]:
        """Obter histórico de entregas"""
        deliveries = self.deliveries
        
        if webhook_id:
            deliveries = [d for d in deliveries if d.webhook_id == webhook_id]
        
        # Ordenar por data (mais recentes primeiro)
        deliveries.sort(key=lambda d: d.created_at, reverse=True)
        
        return deliveries[:limit]
    
    def get_webhook_stats(self, webhook_id: str) -> Dict[str, Any]:
        """Obter estatísticas de um webhook"""
        webhook = self.get_webhook(webhook_id)
        if not webhook:
            return {}
        
        deliveries = [d for d in self.deliveries if d.webhook_id == webhook_id]
        
        successful = len([d for d in deliveries if d.status_code and d.status_code < 400])
        failed = len(deliveries) - successful
        
        return {
            "webhook_id": webhook_id,
            "url": webhook.url,
            "active": webhook.active,
            "events": webhook.events,
            "created_at": webhook.created_at.isoformat(),
            "last_triggered": webhook.last_triggered.isoformat() if webhook.last_triggered else None,
            "total_deliveries": len(deliveries),
            "successful_deliveries": successful,
            "failed_deliveries": failed,
            "success_rate": (successful / len(deliveries) * 100) if deliveries else 0
        }
    
    def _generate_webhook_id(self, url: str) -> str:
        """Gerar ID único para webhook"""
        timestamp = str(int(time.time()))
        data = f"{url}:{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:16]
    
    def _generate_delivery_id(self) -> str:
        """Gerar ID único para entrega"""
        timestamp = str(int(time.time() * 1000))
        return f"del_{timestamp}_{len(self.deliveries)}"
    
    def _validate_url(self, url: str) -> bool:
        """Validar URL do webhook"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except:
            return False
    
    def _generate_signature(self, payload: Dict[str, Any], secret: str) -> str:
        """Gerar assinatura HMAC para webhook"""
        payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return f"sha256={signature}"
    
    async def cleanup_old_deliveries(self, days: int = 30):
        """Limpar entregas antigas"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        old_count = len(self.deliveries)
        self.deliveries = [
            d for d in self.deliveries 
            if d.created_at > cutoff_date
        ]
        
        removed = old_count - len(self.deliveries)
        if removed > 0:
            logger.info(f"Removidas {removed} entregas antigas (>{days} dias)")
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check do sistema de webhooks"""
        active_webhooks = len([w for w in self.webhooks.values() if w.active])
        total_webhooks = len(self.webhooks)
        
        recent_deliveries = [
            d for d in self.deliveries 
            if d.created_at > datetime.utcnow() - timedelta(hours=24)
        ]
        
        successful_recent = len([
            d for d in recent_deliveries 
            if d.status_code and d.status_code < 400
        ])
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "webhooks": {
                "total": total_webhooks,
                "active": active_webhooks,
                "inactive": total_webhooks - active_webhooks
            },
            "deliveries_24h": {
                "total": len(recent_deliveries),
                "successful": successful_recent,
                "failed": len(recent_deliveries) - successful_recent,
                "success_rate": (successful_recent / len(recent_deliveries) * 100) if recent_deliveries else 0
            },
            "total_deliveries": len(self.deliveries)
        }
    
    async def shutdown(self):
        """Encerrar o gerenciador de webhooks"""
        await self.client.aclose()
        logger.info("Webhook Manager encerrado")

# Instância global do gerenciador
webhook_manager = WebhookManager()

# Funções de conveniência para integração com CWB Hub
async def register_cwb_webhook(url: str, events: List[str], secret: Optional[str] = None) -> str:
    """Registrar webhook para eventos do CWB Hub"""
    return webhook_manager.register_webhook(url, events, secret)

async def trigger_cwb_event(event: str, data: Dict[str, Any]) -> List[WebhookDelivery]:
    """Disparar evento do CWB Hub"""
    return await webhook_manager.trigger_event(event, data)

# Eventos específicos do CWB Hub
async def trigger_analysis_started(session_id: str, request: str):
    """Disparar evento de análise iniciada"""
    await trigger_cwb_event(WebhookEvent.ANALYSIS_STARTED.value, {
        "session_id": session_id,
        "request": request,
        "timestamp": datetime.utcnow().isoformat()
    })

async def trigger_analysis_completed(session_id: str, analysis: str, stats: Dict[str, Any]):
    """Disparar evento de análise concluída"""
    await trigger_cwb_event(WebhookEvent.ANALYSIS_COMPLETED.value, {
        "session_id": session_id,
        "analysis": analysis,
        "stats": stats,
        "timestamp": datetime.utcnow().isoformat()
    })

async def trigger_iteration_completed(session_id: str, refined_analysis: str, iteration_count: int):
    """Disparar evento de iteração concluída"""
    await trigger_cwb_event(WebhookEvent.ITERATION_COMPLETED.value, {
        "session_id": session_id,
        "refined_analysis": refined_analysis,
        "iteration_count": iteration_count,
        "timestamp": datetime.utcnow().isoformat()
    })

if __name__ == "__main__":
    # Exemplo de uso
    async def test_webhooks():
        # Registrar webhook de teste
        webhook_id = await register_cwb_webhook(
            "https://httpbin.org/post",
            [WebhookEvent.ANALYSIS_COMPLETED.value],
            secret="test-secret"
        )
        
        print(f"Webhook registrado: {webhook_id}")
        
        # Disparar evento de teste
        await trigger_analysis_completed(
            "test_session",
            "Análise de teste concluída",
            {"collaborations": 5, "confidence": 0.95}
        )
        
        # Ver estatísticas
        stats = webhook_manager.get_webhook_stats(webhook_id)
        print(f"Estatísticas: {stats}")
        
        # Health check
        health = await webhook_manager.health_check()
        print(f"Health: {health}")
        
        await webhook_manager.shutdown()
    
    asyncio.run(test_webhooks())