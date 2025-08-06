#!/usr/bin/env python3
"""
Inicializador da CWB Hub Public API
Melhoria #3 - Integração com APIs Externas
"""

import subprocess
import sys
import os
import time

def install_dependencies():
    """Instala as dependências necessárias"""
    print("📦 Instalando dependências da API...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def check_redis():
    """Verifica se Redis está disponível"""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, db=0)
        client.ping()
        print("✅ Redis conectado e funcionando")
        return True
    except:
        print("⚠️ Redis não disponível - rate limiting será desabilitado")
        print("   Para instalar Redis:")
        print("   - Windows: https://redis.io/download")
        print("   - Linux: sudo apt-get install redis-server")
        print("   - macOS: brew install redis")
        return False

def start_api():
    """Inicia a API"""
    print("🚀 Iniciando CWB Hub Public API...")
    print("📚 Documentação estará disponível em: http://localhost:8000/docs")
    print("🔍 Health check: http://localhost:8000/health")
    print()
    print("Pressione Ctrl+C para parar a API")
    print("=" * 60)
    
    try:
        # Importar e executar uvicorn
        import uvicorn
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🔚 API encerrada pelo usuário")
    except ImportError:
        print("❌ uvicorn não encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "uvicorn[standard]"])
        print("✅ uvicorn instalado. Execute novamente.")
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")

def main():
    """Função principal"""
    print("🏢 CWB HUB PUBLIC API - STARTER")
    print("Melhoria #3 - Integração com APIs Externas")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("main.py"):
        print("❌ Arquivo main.py não encontrado!")
        print("   Execute este script do diretório integrations/api/")
        return
    
    # Instalar dependências
    if not install_dependencies():
        return
    
    # Verificar Redis (opcional)
    check_redis()
    
    print()
    
    # Iniciar API
    start_api()

if __name__ == "__main__":
    main()