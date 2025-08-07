#!/usr/bin/env python3
"""
CWB Hub Persistence System - Database Connection
Configuração e gerenciamento de conexões com PostgreSQL
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
import logging
from typing import Generator, AsyncGenerator
from contextlib import contextmanager, asynccontextmanager

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações do banco de dados
DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "cwb_hub"),
    "username": os.getenv("DB_USER", "cwb_user"),
    "password": os.getenv("DB_PASSWORD", "cwb123"),
}

# URLs de conexão
DATABASE_URL = f"postgresql://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"
ASYNC_DATABASE_URL = f"postgresql+asyncpg://{DATABASE_CONFIG['username']}:{DATABASE_CONFIG['password']}@{DATABASE_CONFIG['host']}:{DATABASE_CONFIG['port']}/{DATABASE_CONFIG['database']}"

# Configurações do pool de conexões
POOL_CONFIG = {
    "poolclass": QueuePool,
    "pool_size": 20,
    "max_overflow": 30,
    "pool_pre_ping": True,
    "pool_recycle": 3600,  # 1 hora
}

# Engine síncrono
engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    **POOL_CONFIG
)

# Engine assíncrono
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Session makers
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=Session
)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


# Event listeners para otimização
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Configurações de otimização para PostgreSQL"""
    if "postgresql" in str(dbapi_connection):
        with dbapi_connection.cursor() as cursor:
            # Configurações de performance
            cursor.execute("SET statement_timeout = '30s'")
            cursor.execute("SET lock_timeout = '10s'")
            cursor.execute("SET idle_in_transaction_session_timeout = '60s'")


# Context managers para sessões
@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager para sessão síncrona"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Erro na sessão do banco de dados: {e}")
        raise
    finally:
        session.close()


@asynccontextmanager
async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Context manager para sessão assíncrona"""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Erro na sessão assíncrona do banco de dados: {e}")
        raise
    finally:
        await session.close()


# Dependency para FastAPI
def get_db() -> Generator[Session, None, None]:
    """Dependency para injeção de dependência no FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency assíncrona para injeção de dependência no FastAPI"""
    async with AsyncSessionLocal() as session:
        yield session


# Funções de utilidade
def test_connection() -> bool:
    """Testa a conexão com o banco de dados"""
    try:
        with get_db_session() as session:
            session.execute(text("SELECT 1"))
        logger.info("✅ Conexão com banco de dados testada com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao conectar com banco de dados: {e}")
        return False


async def test_async_connection() -> bool:
    """Testa a conexão assíncrona com o banco de dados"""
    try:
        async with get_async_db_session() as session:
            await session.execute(text("SELECT 1"))
        logger.info("✅ Conexão assíncrona com banco de dados testada com sucesso")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao conectar assincronamente com banco de dados: {e}")
        return False


def get_connection_info() -> dict:
    """Retorna informações sobre a conexão"""
    return {
        "host": DATABASE_CONFIG["host"],
        "port": DATABASE_CONFIG["port"],
        "database": DATABASE_CONFIG["database"],
        "username": DATABASE_CONFIG["username"],
        "pool_size": POOL_CONFIG["pool_size"],
        "max_overflow": POOL_CONFIG["max_overflow"],
        "engine_url": str(engine.url).replace(DATABASE_CONFIG["password"], "***"),
        "async_engine_url": str(async_engine.url).replace(DATABASE_CONFIG["password"], "***"),
    }


# Função para fechar conexões
def close_connections():
    """Fecha todas as conexões"""
    try:
        engine.dispose()
        logger.info("✅ Conexões síncronas fechadas")
    except Exception as e:
        logger.error(f"❌ Erro ao fechar conexões síncronas: {e}")


async def close_async_connections():
    """Fecha todas as conexões assíncronas"""
    try:
        await async_engine.dispose()
        logger.info("✅ Conexões assíncronas fechadas")
    except Exception as e:
        logger.error(f"❌ Erro ao fechar conexões assíncronas: {e}")


# Health check
def health_check() -> dict:
    """Verifica a saúde da conexão com o banco"""
    try:
        with get_db_session() as session:
            result = session.execute(text("SELECT version(), current_database(), current_user"))
            version, database, user = result.fetchone()
            
            # Estatísticas do pool
            pool = engine.pool
            pool_stats = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                            }
            
            return {
                "status": "healthy",
                "database_version": version,
                "current_database": database,
                "current_user": user,
                "pool_statistics": pool_stats,
                "connection_info": get_connection_info()
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "connection_info": get_connection_info()
        }


if __name__ == "__main__":
    # Teste de conexão
    print("🔍 Testando conexão com banco de dados...")
    print(f"📊 Informações de conexão: {get_connection_info()}")
    
    if test_connection():
        print("✅ Conexão síncrona funcionando!")
        
        # Health check
        health = health_check()
        print(f"🏥 Health check: {health['status']}")
        if health['status'] == 'healthy':
            print(f"📊 Versão do PostgreSQL: {health['database_version']}")
            print(f"🗄️  Banco atual: {health['current_database']}")
            print(f"👤 Usuário atual: {health['current_user']}")
            print(f"🏊 Pool stats: {health['pool_statistics']}")
    else:
        print("❌ Falha na conexão síncrona!")
    
    # Teste assíncrono
    import asyncio
    
    async def test_async():
        if await test_async_connection():
            print("✅ Conexão assíncrona funcionando!")
        else:
            print("❌ Falha na conexão assíncrona!")
    
    asyncio.run(test_async())