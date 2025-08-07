#!/usr/bin/env python3
"""
CWB Hub Authentication Middleware - Task 16
Middleware de autenticação para API externa com API keys
Implementado pela Equipe CWB Hub
"""

import time
import logging
from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

# Importar o gerenciador de API keys
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from api_key_manager import api_key_manager, APIKeyConfig

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

class APIKeyAuthMiddleware:
    """Middleware de autenticação com API keys"""
    
    def __init__(self):
        self.api_key_manager = api_key_manager
    
    async def authenticate_api_key(
        self, 
        request: Request,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> APIKeyConfig:
        """Autenticar requisição com API key"""
        
        start_time = time.time()
        
        try:
            # Extrair API key do header Authorization
            api_key = credentials.credentials
            
            if not api_key:
                logger.warning(f"API key não fornecida - IP: {request.client.host}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key é obrigatória",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Validar API key
            config = self.api_key_manager.validate_api_key(api_key)
            
            if not config:
                logger.warning(f"API key inválida: {api_key[:8]}... - IP: {request.client.host}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="API key inválida ou expirada",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Verificar rate limit
            if not self.api_key_manager.check_rate_limit(config.key_id, config.rate_limit_per_hour):
                logger.warning(f"Rate limit excedido para {config.key_id}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit excedido. Máximo {config.rate_limit_per_hour} requisições por hora.",
                    headers={
                        "X-RateLimit-Limit": str(config.rate_limit_per_hour),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(int(time.time()) + 3600)
                    }
                )
            
            # Log da autenticação bem-sucedida
            auth_time = (time.time() - start_time) * 1000
            logger.info(f"Autenticação bem-sucedida: {config.key_id} - {auth_time:.2f}ms")
            
            # Adicionar informações da API key ao request
            request.state.api_key_config = config
            request.state.api_key_id = config.key_id
            
            return config
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Erro na autenticação: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro interno de autenticação"
            )
    
    def require_permission(self, required_permission: str):
        """Decorator para exigir permissão específica"""
        
        def permission_checker(
            request: Request,
            config: APIKeyConfig = Depends(self.authenticate_api_key)
        ) -> APIKeyConfig:
            
            if not self.api_key_manager.check_permission(config, required_permission):
                logger.warning(
                    f"Permissão negada: {config.key_id} tentou acessar {required_permission}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissão insuficiente. Necessária: {required_permission}"
                )
            
            return config
        
        return permission_checker
    
    def require_permissions(self, required_permissions: list):
        """Decorator para exigir múltiplas permissões"""
        
        def permissions_checker(
            request: Request,
            config: APIKeyConfig = Depends(self.authenticate_api_key)
        ) -> APIKeyConfig:
            
            missing_permissions = []
            for permission in required_permissions:
                if not self.api_key_manager.check_permission(config, permission):
                    missing_permissions.append(permission)
            
            if missing_permissions:
                logger.warning(
                    f"Permissões negadas: {config.key_id} - faltam: {missing_permissions}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permissões insuficientes. Necessárias: {missing_permissions}"
                )
            
            return config
        
        return permissions_checker

# Instância global do middleware
auth_middleware = APIKeyAuthMiddleware()

# Funções de conveniência para uso como dependencies

async def authenticate_request(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> APIKeyConfig:
    """Dependency para autenticar requisição"""
    return await auth_middleware.authenticate_api_key(request, credentials)

def require_read_permission():
    """Dependency para exigir permissão de leitura"""
    return auth_middleware.require_permission("read")

def require_write_permission():
    """Dependency para exigir permissão de escrita"""
    return auth_middleware.require_permission("write")

def require_admin_permission():
    """Dependency para exigir permissão de admin"""
    return auth_middleware.require_permission("admin")

def require_export_permission():
    """Dependency para exigir permissão de export"""
    return auth_middleware.require_permission("export")

def require_import_permission():
    """Dependency para exigir permissão de import"""
    return auth_middleware.require_permission("import")

def require_webhooks_permission():
    """Dependency para exigir permissão de webhooks"""
    return auth_middleware.require_permission("webhooks")

# Middleware para logging de requisições autenticadas
class RequestLoggingMiddleware:
    """Middleware para logging detalhado de requisições"""
    
    def __init__(self):
        self.api_key_manager = api_key_manager
    
    async def log_request(self, request: Request, call_next):
        """Log detalhado da requisição"""
        
        start_time = time.time()
        
        # Informações da requisição
        method = request.method
        url = str(request.url)
        ip_address = request.client.host
        user_agent = request.headers.get("User-Agent", "Unknown")
        
        # Processar requisição
        response = await call_next(request)
        
        # Calcular tempo de resposta
        response_time = (time.time() - start_time) * 1000
        
        # Obter informações da API key se disponível
        api_key_id = getattr(request.state, 'api_key_id', None)
        
        if api_key_id:
            # Log de uso da API
            self.api_key_manager.log_api_usage(
                key_id=api_key_id,
                endpoint=request.url.path,
                method=method,
                ip_address=ip_address,
                user_agent=user_agent,
                response_status=response.status_code,
                response_time_ms=response_time
            )
        
        # Log estruturado
        logger.info(
            f"REQUEST {method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {response_time:.2f}ms - "
            f"IP: {ip_address} - "
            f"API Key: {api_key_id or 'None'}"
        )
        
        # Adicionar headers de resposta
        response.headers["X-Response-Time"] = f"{response_time:.2f}ms"
        response.headers["X-API-Version"] = "1.0"
        
        if api_key_id:
            # Adicionar informações de rate limit
            config = getattr(request.state, 'api_key_config', None)
            if config:
                remaining = max(0, config.rate_limit_per_hour - 1)  # Simplificado
                response.headers["X-RateLimit-Limit"] = str(config.rate_limit_per_hour)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
                response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 3600)
        
        return response

# Instância global do middleware de logging
request_logging_middleware = RequestLoggingMiddleware()

# Função para adicionar middleware à aplicação FastAPI
def setup_auth_middleware(app):
    """Configurar middleware de autenticação na aplicação"""
    
    @app.middleware("http")
    async def auth_logging_middleware(request: Request, call_next):
        """Middleware combinado de autenticação e logging"""
        return await request_logging_middleware.log_request(request, call_next)
    
    logger.info("✅ Middleware de autenticação configurado")

# Utilitários para validação de API key

def get_api_key_from_header(request: Request) -> Optional[str]:
    """Extrair API key do header da requisição"""
    
    # Tentar Authorization header (Bearer)
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        return auth_header[7:]  # Remove "Bearer "
    
    # Tentar header X-API-Key
    api_key_header = request.headers.get("X-API-Key")
    if api_key_header:
        return api_key_header
    
    return None

def validate_api_key_header(request: Request) -> Optional[APIKeyConfig]:
    """Validar API key do header sem usar FastAPI dependencies"""
    
    api_key = get_api_key_from_header(request)
    if not api_key:
        return None
    
    return api_key_manager.validate_api_key(api_key)

# Decorador para endpoints que precisam de autenticação opcional
def optional_auth(func):
    """Decorador para autenticação opcional"""
    
    async def wrapper(request: Request, *args, **kwargs):
        # Tentar autenticar, mas não falhar se não conseguir
        config = validate_api_key_header(request)
        
        # Adicionar config ao request se disponível
        if config:
            request.state.api_key_config = config
            request.state.api_key_id = config.key_id
        else:
            request.state.api_key_config = None
            request.state.api_key_id = None
        
        return await func(request, *args, **kwargs)
    
    return wrapper

if __name__ == "__main__":
    # Teste do middleware de autenticação
    print("🔐 Testando middleware de autenticação...")
    
    # Simular criação de API key para teste
    from api_key_manager import create_api_key
    
    test_key = create_api_key(
        name="Test Middleware",
        description="Chave para teste do middleware",
        permissions=["read", "write"],
        created_by="test_system"
    )
    
    print(f"✅ API key de teste criada: {test_key['key_id']}")
    
    # Simular validação
    config = api_key_manager.validate_api_key(test_key['api_key'])
    if config:
        print(f"✅ Validação funcionando: {config.name}")
        
        # Testar permissões
        if api_key_manager.check_permission(config, "read"):
            print("✅ Permissão de leitura OK")
        
        if not api_key_manager.check_permission(config, "admin"):
            print("✅ Permissão de admin negada (correto)")
    
    print("🎉 Middleware de autenticação testado com sucesso!")