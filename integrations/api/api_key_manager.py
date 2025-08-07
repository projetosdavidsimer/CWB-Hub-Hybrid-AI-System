#!/usr/bin/env python3
"""
CWB Hub API Key Manager - Task 16
Sistema de gerenciamento de API keys para integração externa
Implementado pela Equipe CWB Hub
"""

import hashlib
import secrets
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum
import redis

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIKeyPermission(Enum):
    """Permissões disponíveis para API keys"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    EXPORT = "export"
    IMPORT = "import"
    WEBHOOKS = "webhooks"

class APIKeyStatus(Enum):
    """Status de uma API key"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    EXPIRED = "expired"
    REVOKED = "revoked"

@dataclass
class APIKeyConfig:
    """Configuração de uma API key"""
    key_id: str
    key_hash: str  # Hash da chave para segurança
    name: str
    description: str
    permissions: List[str]
    rate_limit_per_hour: int
    expires_at: Optional[datetime]
    created_at: datetime
    created_by: str
    last_used: Optional[datetime]
    usage_count: int
    status: str
    metadata: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter para dicionário"""
        data = asdict(self)
        # Converter datetime para ISO string
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        data['created_at'] = self.created_at.isoformat()
        if self.last_used:
            data['last_used'] = self.last_used.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APIKeyConfig':
        """Criar instância a partir de dicionário"""
        # Converter strings ISO para datetime
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('last_used'):
            data['last_used'] = datetime.fromisoformat(data['last_used'])
        return cls(**data)

@dataclass
class APIKeyUsage:
    """Registro de uso de API key"""
    key_id: str
    endpoint: str
    method: str
    timestamp: datetime
    ip_address: str
    user_agent: str
    response_status: int
    response_time_ms: float

class APIKeyManager:
    """Gerenciador de API keys para sistemas externos"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis_client = redis_client
        self.api_keys: Dict[str, APIKeyConfig] = {}
        self.usage_logs: List[APIKeyUsage] = []
        
        # Tentar conectar ao Redis se não fornecido
        if not self.redis_client:
            try:
                self.redis_client = redis.Redis(
                    host='localhost', 
                    port=6379, 
                    db=1,  # DB diferente para API keys
                    decode_responses=True
                )
                self.redis_client.ping()
                logger.info("✅ Redis conectado para API Key Manager")
            except:
                logger.warning("⚠️ Redis não disponível - usando armazenamento em memória")
                self.redis_client = None
    
    def generate_api_key(
        self,
        name: str,
        description: str,
        permissions: List[str],
        created_by: str,
        rate_limit_per_hour: int = 1000,
        expires_in_days: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """Gerar uma nova API key"""
        
        # Validar permissões
        valid_permissions = [p.value for p in APIKeyPermission]
        for perm in permissions:
            if perm not in valid_permissions:
                raise ValueError(f"Permissão inválida: {perm}. Válidas: {valid_permissions}")
        
        # Gerar chave única
        raw_key = secrets.token_urlsafe(32)
        key_id = f"cwb_{int(time.time())}_{secrets.token_hex(8)}"
        
        # Hash da chave para armazenamento seguro
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        
        # Calcular expiração
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        # Criar configuração
        config = APIKeyConfig(
            key_id=key_id,
            key_hash=key_hash,
            name=name,
            description=description,
            permissions=permissions,
            rate_limit_per_hour=rate_limit_per_hour,
            expires_at=expires_at,
            created_at=datetime.utcnow(),
            created_by=created_by,
            last_used=None,
            usage_count=0,
            status=APIKeyStatus.ACTIVE.value,
            metadata=metadata or {}
        )
        
        # Armazenar
        self._store_api_key(config)
        
        logger.info(f"✅ API key criada: {key_id} para {name}")
        
        return {
            "key_id": key_id,
            "api_key": raw_key,
            "name": name,
            "permissions": permissions,
            "rate_limit_per_hour": rate_limit_per_hour,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "created_at": config.created_at.isoformat()
        }
    
    def validate_api_key(self, api_key: str) -> Optional[APIKeyConfig]:
        """Validar uma API key e retornar sua configuração"""
        
        # Hash da chave fornecida
        key_hash = hashlib.sha256(api_key.encode()).hexdigest()
        
        # Buscar configuração
        config = self._find_key_by_hash(key_hash)
        
        if not config:
            logger.warning(f"❌ API key inválida: {api_key[:8]}...")
            return None
        
        # Verificar status
        if config.status != APIKeyStatus.ACTIVE.value:
            logger.warning(f"❌ API key inativa: {config.key_id}")
            return None
        
        # Verificar expiração
        if config.expires_at and datetime.utcnow() > config.expires_at:
            logger.warning(f"❌ API key expirada: {config.key_id}")
            self._update_key_status(config.key_id, APIKeyStatus.EXPIRED.value)
            return None
        
        # Atualizar último uso
        config.last_used = datetime.utcnow()
        config.usage_count += 1
        self._store_api_key(config)
        
        logger.debug(f"✅ API key válida: {config.key_id}")
        return config
    
    def check_permission(self, config: APIKeyConfig, required_permission: str) -> bool:
        """Verificar se a API key tem a permissão necessária"""
        
        # Admin tem todas as permissões
        if APIKeyPermission.ADMIN.value in config.permissions:
            return True
        
        # Verificar permissão específica
        return required_permission in config.permissions
    
    def check_rate_limit(self, key_id: str, rate_limit: int) -> bool:
        """Verificar rate limit para uma API key"""
        
        if not self.redis_client:
            return True  # Sem Redis, permitir
        
        try:
            # Chave para rate limiting
            rate_key = f"api_rate_limit:{key_id}"
            
            # Obter contagem atual
            current = self.redis_client.get(rate_key)
            
            if current is None:
                # Primeira requisição na janela
                self.redis_client.setex(rate_key, 3600, 1)  # 1 hora
                return True
            
            current_count = int(current)
            
            if current_count >= rate_limit:
                logger.warning(f"❌ Rate limit excedido para {key_id}: {current_count}/{rate_limit}")
                return False
            
            # Incrementar contador
            self.redis_client.incr(rate_key)
            return True
            
        except Exception as e:
            logger.error(f"Erro no rate limiting: {e}")
            return True  # Em caso de erro, permitir
    
    def revoke_api_key(self, key_id: str, revoked_by: str) -> bool:
        """Revogar uma API key"""
        
        config = self._get_key_config(key_id)
        if not config:
            return False
        
        config.status = APIKeyStatus.REVOKED.value
        config.metadata['revoked_by'] = revoked_by
        config.metadata['revoked_at'] = datetime.utcnow().isoformat()
        
        self._store_api_key(config)
        
        logger.info(f"✅ API key revogada: {key_id} por {revoked_by}")
        return True
    
    def list_api_keys(self, include_revoked: bool = False) -> List[Dict[str, Any]]:
        """Listar todas as API keys"""
        
        keys = []
        
        if self.redis_client:
            # Buscar do Redis
            pattern = "api_key:*"
            for key in self.redis_client.scan_iter(match=pattern):
                try:
                    data = json.loads(self.redis_client.get(key))
                    config = APIKeyConfig.from_dict(data)
                    
                    if not include_revoked and config.status == APIKeyStatus.REVOKED.value:
                        continue
                    
                    # Remover hash da chave por segurança
                    key_data = config.to_dict()
                    del key_data['key_hash']
                    keys.append(key_data)
                    
                except Exception as e:
                    logger.error(f"Erro ao carregar chave {key}: {e}")
        else:
            # Buscar da memória
            for config in self.api_keys.values():
                if not include_revoked and config.status == APIKeyStatus.REVOKED.value:
                    continue
                
                key_data = config.to_dict()
                del key_data['key_hash']
                keys.append(key_data)
        
        return keys
    
    def get_api_key_stats(self, key_id: str) -> Optional[Dict[str, Any]]:
        """Obter estatísticas de uma API key"""
        
        config = self._get_key_config(key_id)
        if not config:
            return None
        
        # Estatísticas básicas
        stats = {
            "key_id": key_id,
            "name": config.name,
            "status": config.status,
            "created_at": config.created_at.isoformat(),
            "last_used": config.last_used.isoformat() if config.last_used else None,
            "usage_count": config.usage_count,
            "permissions": config.permissions,
            "rate_limit_per_hour": config.rate_limit_per_hour
        }
        
        # Rate limit atual
        if self.redis_client:
            try:
                rate_key = f"api_rate_limit:{key_id}"
                current_usage = self.redis_client.get(rate_key)
                stats["current_hour_usage"] = int(current_usage) if current_usage else 0
                stats["rate_limit_remaining"] = max(0, config.rate_limit_per_hour - stats["current_hour_usage"])
            except:
                stats["current_hour_usage"] = 0
                stats["rate_limit_remaining"] = config.rate_limit_per_hour
        
        return stats
    
    def log_api_usage(
        self,
        key_id: str,
        endpoint: str,
        method: str,
        ip_address: str,
        user_agent: str,
        response_status: int,
        response_time_ms: float
    ):
        """Registrar uso da API"""
        
        usage = APIKeyUsage(
            key_id=key_id,
            endpoint=endpoint,
            method=method,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            response_status=response_status,
            response_time_ms=response_time_ms
        )
        
        self.usage_logs.append(usage)
        
        # Manter apenas os últimos 10000 logs em memória
        if len(self.usage_logs) > 10000:
            self.usage_logs = self.usage_logs[-5000:]
        
        # Log estruturado
        logger.info(
            f"API_USAGE key_id={key_id} endpoint={endpoint} method={method} "
            f"status={response_status} time={response_time_ms}ms ip={ip_address}"
        )
    
    def _store_api_key(self, config: APIKeyConfig):
        """Armazenar configuração de API key"""
        
        if self.redis_client:
            # Armazenar no Redis
            key = f"api_key:{config.key_id}"
            data = json.dumps(config.to_dict())
            self.redis_client.set(key, data)
        else:
            # Armazenar em memória
            self.api_keys[config.key_id] = config
    
    def _get_key_config(self, key_id: str) -> Optional[APIKeyConfig]:
        """Obter configuração de uma API key"""
        
        if self.redis_client:
            try:
                key = f"api_key:{key_id}"
                data = self.redis_client.get(key)
                if data:
                    return APIKeyConfig.from_dict(json.loads(data))
            except Exception as e:
                logger.error(f"Erro ao buscar chave {key_id}: {e}")
        else:
            return self.api_keys.get(key_id)
        
        return None
    
    def _find_key_by_hash(self, key_hash: str) -> Optional[APIKeyConfig]:
        """Encontrar API key pelo hash"""
        
        if self.redis_client:
            # Buscar no Redis
            pattern = "api_key:*"
            for key in self.redis_client.scan_iter(match=pattern):
                try:
                    data = json.loads(self.redis_client.get(key))
                    if data.get('key_hash') == key_hash:
                        return APIKeyConfig.from_dict(data)
                except:
                    continue
        else:
            # Buscar em memória
            for config in self.api_keys.values():
                if config.key_hash == key_hash:
                    return config
        
        return None
    
    def _update_key_status(self, key_id: str, status: str):
        """Atualizar status de uma API key"""
        
        config = self._get_key_config(key_id)
        if config:
            config.status = status
            self._store_api_key(config)

# Instância global
api_key_manager = APIKeyManager()

# Funções de conveniência
def create_api_key(
    name: str,
    description: str,
    permissions: List[str],
    created_by: str,
    **kwargs
) -> Dict[str, str]:
    """Criar uma nova API key"""
    return api_key_manager.generate_api_key(
        name, description, permissions, created_by, **kwargs
    )

def validate_api_key(api_key: str) -> Optional[APIKeyConfig]:
    """Validar uma API key"""
    return api_key_manager.validate_api_key(api_key)

def check_api_permission(config: APIKeyConfig, permission: str) -> bool:
    """Verificar permissão de API key"""
    return api_key_manager.check_permission(config, permission)

def check_api_rate_limit(key_id: str, rate_limit: int) -> bool:
    """Verificar rate limit"""
    return api_key_manager.check_rate_limit(key_id, rate_limit)

if __name__ == "__main__":
    # Teste do sistema de API keys
    print("🔑 Testando API Key Manager...")
    
    # Criar API key de teste
    test_key = create_api_key(
        name="Test Integration",
        description="Chave de teste para integração",
        permissions=["read", "write"],
        created_by="test_user",
        rate_limit_per_hour=100,
        expires_in_days=30
    )
    
    print(f"✅ API key criada: {test_key['key_id']}")
    print(f"   Chave: {test_key['api_key'][:16]}...")
    
    # Validar chave
    config = validate_api_key(test_key['api_key'])
    if config:
        print(f"✅ Chave válida para: {config.name}")
        print(f"   Permissões: {config.permissions}")
        print(f"   Rate limit: {config.rate_limit_per_hour}/hora")
    
    # Testar permissões
    if check_api_permission(config, "read"):
        print("✅ Permissão de leitura OK")
    
    if not check_api_permission(config, "admin"):
        print("✅ Permissão de admin negada (correto)")
    
    # Testar rate limit
    if check_api_rate_limit(config.key_id, config.rate_limit_per_hour):
        print("✅ Rate limit OK")
    
    print("🎉 API Key Manager testado com sucesso!")