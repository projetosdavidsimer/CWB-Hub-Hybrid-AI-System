#!/usr/bin/env python3
"""
CWB Hub Persistence System - Database Setup
Script para configurar e inicializar o banco de dados PostgreSQL
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path
import logging

# Adicionar persistence ao path
sys.path.append(str(Path(__file__).parent))

from database.models import Base, create_tables, populate_initial_data
from database.connection import engine, test_connection, health_check, get_connection_info
from auth.jwt_handler import jwt_handler, password_handler

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def install_requirements():
    """Instala dependências do sistema de persistência"""
    print("📦 Instalando dependências do sistema de persistência...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            str(Path(__file__).parent / "requirements.txt")
        ], check=True)
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False


def check_postgresql():
    """Verifica se PostgreSQL está disponível"""
    print("🔍 Verificando disponibilidade do PostgreSQL...")
    
    # Verificar se psql está disponível
    try:
        result = subprocess.run(["psql", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ PostgreSQL encontrado: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️  PostgreSQL não encontrado no sistema")
    print("📋 Para instalar PostgreSQL:")
    print("   Windows: https://www.postgresql.org/download/windows/")
    print("   macOS: brew install postgresql")
    print("   Ubuntu: sudo apt-get install postgresql postgresql-contrib")
    
    return False


def setup_environment():
    """Configura variáveis de ambiente"""
    print("🔧 Configurando variáveis de ambiente...")
    
    env_vars = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "cwb_hub",
        "DB_USER": "cwb_user",
        "DB_PASSWORD": "cwb_password_2025",
        "JWT_SECRET_KEY": "cwb_hub_secret_key_2025_very_secure",
        "ACCESS_TOKEN_EXPIRE_MINUTES": "30",
        "REFRESH_TOKEN_EXPIRE_DAYS": "7",
    }
    
    env_file = Path(__file__).parent / ".env"
    
    with open(env_file, "w") as f:
        f.write("# CWB Hub Persistence System Environment Variables\n")
        f.write("# Generated automatically - modify as needed\n\n")
        
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
            os.environ[key] = value
    
    print(f"✅ Arquivo .env criado: {env_file}")
    print("📋 Variáveis configuradas:")
    for key, value in env_vars.items():
        if "PASSWORD" in key or "SECRET" in key:
            print(f"   {key}=***")
        else:
            print(f"   {key}={value}")


def create_database_sql():
    """Gera SQL para criar banco e usuário"""
    sql_commands = f"""
-- CWB Hub Database Setup
-- Execute como superuser do PostgreSQL

-- Criar usuário
CREATE USER cwb_user WITH PASSWORD 'cwb_password_2025';

-- Criar banco de dados
CREATE DATABASE cwb_hub OWNER cwb_user;

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE cwb_hub TO cwb_user;

-- Conectar ao banco cwb_hub e conceder privilégios no schema
\\c cwb_hub
GRANT ALL ON SCHEMA public TO cwb_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cwb_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cwb_user;

-- Configurações de performance
ALTER DATABASE cwb_hub SET shared_preload_libraries = 'pg_stat_statements';
ALTER DATABASE cwb_hub SET log_statement = 'all';
ALTER DATABASE cwb_hub SET log_min_duration_statement = 1000;
    """
    
    sql_file = Path(__file__).parent / "setup_database.sql"
    with open(sql_file, "w") as f:
        f.write(sql_commands)
    
    print(f"✅ Arquivo SQL criado: {sql_file}")
    print("📋 Para executar:")
    print(f"   sudo -u postgres psql -f {sql_file}")
    
    return sql_file


def setup_database():
    """Configura o banco de dados"""
    print("🗄️  Configurando banco de dados...")
    
    # Testar conexão
    if not test_connection():
        print("❌ Não foi possível conectar ao banco de dados")
        print("📋 Verifique se:")
        print("   1. PostgreSQL está rodando")
        print("   2. Banco 'cwb_hub' existe")
        print("   3. Usuário 'cwb_user' tem permissões")
        print("   4. Credenciais estão corretas no .env")
        return False
    
    try:
        # Criar tabelas
        print("📋 Criando tabelas...")
        create_tables(engine)
        print("✅ Tabelas criadas com sucesso!")
        
        # Popular dados iniciais
        print("�� Populando dados iniciais...")
        from database.connection import get_db_session
        with get_db_session() as session:
            populate_initial_data(session)
        
        print("✅ Banco de dados configurado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao configurar banco de dados: {e}")
        return False


def test_authentication():
    """Testa o sistema de autenticação"""
    print("🔐 Testando sistema de autenticação...")
    
    try:
        # Criar usuário de teste
        test_user = {
            "sub": "1",
            "email": "admin@cwbhub.com",
            "role": "admin",
            "company": "CWB Hub"
        }
        
        # Criar tokens
        tokens = jwt_handler.create_token_pair(test_user)
        print("✅ Tokens JWT criados com sucesso!")
        
        # Verificar token
        payload = jwt_handler.verify_access_token(tokens["access_token"])
        if payload:
            print(f"✅ Token verificado: {payload['email']}")
        
        # Testar senha
        password = "admin123"
        hashed = password_handler.hash_password(password)
        if password_handler.verify_password(password, hashed):
            print("✅ Sistema de senhas funcionando!")
        
        print("✅ Sistema de autenticação testado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar autenticação: {e}")
        return False


def show_status():
    """Mostra status do sistema"""
    print("\n" + "=" * 60)
    print("📊 STATUS DO SISTEMA DE PERSISTÊNCIA")
    print("=" * 60)
    
    # Informações de conexão
    conn_info = get_connection_info()
    print("🔗 Conexão:")
    print(f"   Host: {conn_info['host']}:{conn_info['port']}")
    print(f"   Database: {conn_info['database']}")
    print(f"   User: {conn_info['username']}")
    
    # Health check
    health = health_check()
    print(f"\n🏥 Health Check: {health['status'].upper()}")
    
    if health['status'] == 'healthy':
        print(f"   PostgreSQL: {health['database_version']}")
        print(f"   Pool Size: {health['pool_statistics']['size']}")
        print(f"   Active Connections: {health['pool_statistics']['checked_out']}")
    
    # Arquivos criados
    files_created = [
        "database/models.py",
        "database/connection.py", 
        "auth/jwt_handler.py",
        "requirements.txt",
        ".env",
        "setup_database.sql"
    ]
    
    print("\n📁 Arquivos Criados:")
    for file in files_created:
        file_path = Path(__file__).parent / file
        if file_path.exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file}")


def main():
    """Função principal"""
    print("🗄️  CWB HUB PERSISTENCE SYSTEM SETUP")
    print("Melhoria #2 de 27 para Dominação Mundial")
    print("=" * 60)
    
    # 1. Instalar dependências
    if not install_requirements():
        print("❌ Falha na instalação de dependências")
        return
    
    # 2. Verificar PostgreSQL
    check_postgresql()
    
    # 3. Configurar ambiente
    setup_environment()
    
    # 4. Criar SQL de setup
    sql_file = create_database_sql()
    
    # 5. Tentar configurar banco
    print("\n🗄️  Tentando configurar banco de dados...")
    if setup_database():
        # 6. Testar autenticação
        test_authentication()
        
        # 7. Mostrar status
        show_status()
        
        print("\n🎉 SISTEMA DE PERSISTÊNCIA CONFIGURADO COM SUCESSO!")
        print("=" * 60)
        print("📋 Próximos passos:")
        print("   1. Integrar com web interface")
        print("   2. Implementar APIs CRUD")
        print("   3. Adicionar testes automatizados")
        print("   4. Configurar backup automático")
        
    else:
        print("\n⚠️  CONFIGURAÇÃO PARCIAL CONCLUÍDA")
        print("=" * 60)
        print("📋 Para completar a configuração:")
        print(f"   1. Execute: sudo -u postgres psql -f {sql_file}")
        print("   2. Execute novamente este script")
        print("   3. Verifique as configurações no arquivo .env")


if __name__ == "__main__":
    main()