#!/usr/bin/env python3
"""
CWB Hub External API - Startup Script - Task 16
Script principal para inicializar a API externa
Implementado pela Equipe CWB Hub
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Adicionar paths necessários
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))
sys.path.append(str(current_dir.parent.parent / "src"))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Imprimir banner de inicialização"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    CWB HUB EXTERNAL API                      ║
    ║                        Task 16                               ║
    ║              API para Integração Externa                     ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  🚀 FastAPI + Pydantic + Redis                              ║
    ║  🔐 Autenticação por API Keys                               ║
    ║  📊 Rate Limiting Inteligente                               ║
    ║  🔗 Webhooks Configuráveis                                  ║
    ║  📈 Analytics e Monitoramento                               ║
    ║  👥 8 Especialistas IA Colaborando                          ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_dependencies():
    """Verificar dependências necessárias"""
    logger.info("🔍 Verificando dependências...")
    
    required_modules = [
        'fastapi',
        'uvicorn',
        'pydantic',
        'redis',
        'httpx',
        'passlib',
        'jwt'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"  ✅ {module}")
        except ImportError:
            missing_modules.append(module)
            logger.error(f"  ❌ {module}")
    
    if missing_modules:
        logger.error(f"Módulos faltando: {missing_modules}")
        logger.error("Execute: pip install -r requirements.txt")
        return False
    
    logger.info("✅ Todas as dependências estão instaladas")
    return True

def check_redis_connection():
    """Verificar conexão com Redis"""
    logger.info("🔍 Verificando conexão com Redis...")
    
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)
        client.ping()
        logger.info("✅ Redis conectado")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Redis não disponível: {e}")
        logger.warning("Rate limiting será desabilitado")
        return False

def setup_environment():
    """Configurar ambiente"""
    logger.info("🔧 Configurando ambiente...")
    
    # Verificar arquivo .env
    env_file = current_dir / ".env"
    if not env_file.exists():
        logger.info("📝 Criando arquivo .env padrão...")
        
        env_content = """# CWB Hub External API Configuration
CWB_HUB_API_HOST=0.0.0.0
CWB_HUB_API_PORT=8002
CWB_HUB_API_DEBUG=true

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=1

# Rate Limiting
DEFAULT_RATE_LIMIT=1000
BURST_RATE_LIMIT=100

# JWT Configuration
JWT_SECRET_KEY=cwb-hub-external-api-secret-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Webhooks
WEBHOOK_TIMEOUT=30
WEBHOOK_RETRY_COUNT=3

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json

# CORS
CORS_ORIGINS=["*"]
TRUSTED_HOSTS=["*"]
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        logger.info(f"✅ Arquivo .env criado: {env_file}")
    
    # Carregar variáveis de ambiente
    try:
        from dotenv import load_dotenv
        load_dotenv(env_file)
        logger.info("✅ Variáveis de ambiente carregadas")
    except ImportError:
        logger.warning("⚠️ python-dotenv não instalado - usando valores padrão")

def initialize_api_keys():
    """Inicializar sistema de API keys"""
    logger.info("🔑 Inicializando sistema de API keys...")
    
    try:
        from api_key_manager import api_key_manager, create_api_key
        
        # Criar API key de demonstração se não existir
        demo_key = create_api_key(
            name="Demo API Key",
            description="Chave de demonstração para testes",
            permissions=["read", "write", "export", "import", "webhooks"],
            created_by="system",
            rate_limit_per_hour=1000,
            expires_in_days=365
        )
        
        logger.info("✅ Sistema de API keys inicializado")
        logger.info(f"🔑 API Key de demo criada: {demo_key['key_id']}")
        logger.info(f"   Chave: {demo_key['api_key'][:16]}...")
        
        return demo_key
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar API keys: {e}")
        return None

def initialize_webhooks():
    """Inicializar sistema de webhooks"""
    logger.info("🔗 Inicializando sistema de webhooks...")
    
    try:
        from webhooks.webhook_manager import webhook_manager
        
        # Verificar health do sistema de webhooks
        health = asyncio.run(webhook_manager.health_check())
        logger.info(f"✅ Sistema de webhooks: {health['status']}")
        
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ Sistema de webhooks não disponível: {e}")
        return False

def create_startup_script():
    """Criar script de inicialização"""
    startup_script = current_dir / "start_api.sh"
    
    script_content = """#!/bin/bash
# CWB Hub External API Startup Script

echo "🚀 Iniciando CWB Hub External API..."

# Verificar se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado"
    exit 1
fi

# Verificar se as dependências estão instaladas
python3 -c "import fastapi, uvicorn, pydantic, redis" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Instalando dependências..."
    pip install -r requirements.txt
fi

# Verificar se o Redis está rodando
redis-cli ping &> /dev/null
if [ $? -ne 0 ]; then
    echo "⚠️ Redis não está rodando - iniciando..."
    redis-server --daemonize yes
fi

# Iniciar API
echo "🌟 Iniciando API externa..."
python3 start_external_api.py

echo "✅ API iniciada com sucesso!"
echo "📖 Documentação: http://localhost:8002/external/v1/docs"
"""
    
    with open(startup_script, 'w') as f:
        f.write(script_content)
    
    # Tornar executável
    os.chmod(startup_script, 0o755)
    
    logger.info(f"✅ Script de inicialização criado: {startup_script}")

def main():
    """Função principal"""
    print_banner()
    
    logger.info("🚀 Iniciando CWB Hub External API...")
    
    # Verificações pré-inicialização
    if not check_dependencies():
        logger.error("❌ Dependências faltando - abortando")
        sys.exit(1)
    
    # Configurar ambiente
    setup_environment()
    
    # Verificar Redis
    redis_available = check_redis_connection()
    
    # Inicializar componentes
    demo_key = initialize_api_keys()
    webhooks_available = initialize_webhooks()
    
    # Criar script de inicialização
    create_startup_script()
    
    # Importar e configurar aplicação
    logger.info("📦 Carregando aplicação FastAPI...")
    
    try:
        from external_api import app
        from external_endpoints_extended import add_extended_endpoints
        from external_api import projects_storage, api_stats
        from webhooks.webhook_manager import webhook_manager
        
        # Adicionar endpoints estendidos
        add_extended_endpoints(app, projects_storage, webhook_manager, api_stats)
        
        logger.info("✅ Aplicação carregada com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro ao carregar aplicação: {e}")
        sys.exit(1)
    
    # Informações de inicialização
    logger.info("🎯 Configuração da API:")
    logger.info(f"   Host: {os.getenv('CWB_HUB_API_HOST', '0.0.0.0')}")
    logger.info(f"   Porta: {os.getenv('CWB_HUB_API_PORT', '8002')}")
    logger.info(f"   Debug: {os.getenv('CWB_HUB_API_DEBUG', 'true')}")
    logger.info(f"   Redis: {'✅' if redis_available else '❌'}")
    logger.info(f"   Webhooks: {'✅' if webhooks_available else '❌'}")
    
    if demo_key:
        logger.info("🔑 API Key de demonstração:")
        logger.info(f"   ID: {demo_key['key_id']}")
        logger.info(f"   Chave: {demo_key['api_key']}")
        logger.info(f"   Permissões: {demo_key['permissions']}")
    
    logger.info("📚 Endpoints disponíveis:")
    logger.info("   GET  /external/v1/ - Informações da API")
    logger.info("   GET  /external/v1/health - Health check")
    logger.info("   POST /external/v1/projects - Criar projeto")
    logger.info("   GET  /external/v1/projects - Listar projetos")
    logger.info("   GET  /external/v1/projects/{id}/status - Status do projeto")
    logger.info("   POST /external/v1/projects/{id}/iterate - Iterar projeto")
    logger.info("   POST /external/v1/export - Exportar dados")
    logger.info("   POST /external/v1/import - Importar dados")
    logger.info("   POST /external/v1/webhooks - Criar webhook")
    logger.info("   GET  /external/v1/webhooks - Listar webhooks")
    logger.info("   GET  /external/v1/analytics - Analytics")
    
    logger.info("📖 Documentação:")
    logger.info("   Swagger UI: http://localhost:8002/external/v1/docs")
    logger.info("   ReDoc: http://localhost:8002/external/v1/redoc")
    logger.info("   OpenAPI: http://localhost:8002/external/v1/openapi.json")
    
    # Iniciar servidor
    logger.info("🌟 Iniciando servidor...")
    
    try:
        import uvicorn
        
        uvicorn.run(
            app,
            host=os.getenv('CWB_HUB_API_HOST', '0.0.0.0'),
            port=int(os.getenv('CWB_HUB_API_PORT', '8002')),
            reload=os.getenv('CWB_HUB_API_DEBUG', 'true').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'info').lower()
        )
        
    except KeyboardInterrupt:
        logger.info("⏹️ Servidor interrompido pelo usuário")
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()