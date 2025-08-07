#!/usr/bin/env python3
"""
CWB Hub Advanced Cache System - Sistema de Cache Avançado
Melhoria #11 - Cache Redis para Performance e Redução de Custos
"""

import redis
import json
import hashlib
import time
import logging
from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import asyncio
import pickle
import gzip
from dataclasses import dataclass
from enum import Enum

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CacheLevel(Enum):
    """Níveis de cache disponíveis"""
    MEMORY = "memory"
    REDIS = "redis"
    PERSISTENT = "persistent"

@dataclass
class CacheStats:
    """Estatísticas do cache"""
    hits: int = 0
    misses: int = 0
    total_requests: int = 0
    hit_rate: float = 0.0
    memory_usage: int = 0
    redis_usage: int = 0
    cost_savings: float = 0.0

class AdvancedCacheManager:
    """
    Sistema de cache avançado multi-nível para CWB Hub
    
    Funcionalidades:
    - Cache em memória (L1) - ultra rápido
    - Cache Redis (L2) - compartilhado entre instâncias
    - Cache persistente (L3) - para dados críticos
    - Compressão automática
    - TTL configurável
    - Estatísticas detalhadas
    - Limpeza automática
    """
    
    def __init__(self, 
                 redis_host: str = "localhost",
                 redis_port: int = 6379,
                 redis_db: int = 1,  # DB separado para cache
                 memory_limit: int = 100,  # MB
                 default_ttl: int = 3600):  # 1 hora
        
        self.memory_cache: Dict[str, Dict[str, Any]] = {}
        self.memory_limit = memory_limit * 1024 * 1024  # Converter para bytes
        self.default_ttl = default_ttl
        self.stats = CacheStats()
        
        # Configurar Redis
        try:
            self.redis_client = redis.Redis(
                host=redis_host, 
                port=redis_port, 
                db=redis_db, 
                decode_responses=False  # Para suportar dados binários
            )
            self.redis_client.ping()
            self.redis_available = True
            logger.info("✅ Redis cache conectado")
        except Exception as e:
            self.redis_available = False
            logger.warning(f"⚠️ Redis não disponível: {e}")
        
        # Configurações de cache por tipo
        self.cache_configs = {
            "llm_responses": {
                "ttl": 7 * 24 * 3600,  # 7 dias
                "compress": True,
                "level": CacheLevel.REDIS
            },
            "agent_analysis": {
                "ttl": 24 * 3600,  # 1 dia
                "compress": True,
                "level": CacheLevel.REDIS
            },
            "project_data": {
                "ttl": 30 * 24 * 3600,  # 30 dias
                "compress": False,
                "level": CacheLevel.PERSISTENT
            },
            "user_sessions": {
                "ttl": 3600,  # 1 hora
                "compress": False,
                "level": CacheLevel.MEMORY
            },
            "api_responses": {
                "ttl": 1800,  # 30 minutos
                "compress": True,
                "level": CacheLevel.REDIS
            }
        }
    
    def _generate_key(self, namespace: str, identifier: str, params: Optional[Dict] = None) -> str:
        """Gera chave única para cache"""
        key_data = f"{namespace}:{identifier}"
        
        if params:
            # Ordenar parâmetros para consistência
            sorted_params = json.dumps(params, sort_keys=True)
            param_hash = hashlib.md5(sorted_params.encode()).hexdigest()[:8]
            key_data += f":{param_hash}"
        
        return f"cwb_cache:{key_data}"
    
    def _compress_data(self, data: Any) -> bytes:
        """Comprime dados usando gzip"""
        try:
            serialized = pickle.dumps(data)
            compressed = gzip.compress(serialized)
            return compressed
        except Exception as e:
            logger.error(f"Erro ao comprimir dados: {e}")
            return pickle.dumps(data)
    
    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Descomprime dados"""
        try:
            decompressed = gzip.decompress(compressed_data)
            return pickle.loads(decompressed)
        except:
            # Fallback para dados não comprimidos
            return pickle.loads(compressed_data)
    
    def _get_cache_config(self, cache_type: str) -> Dict[str, Any]:
        """Obtém configuração de cache para tipo específico"""
        return self.cache_configs.get(cache_type, {
            "ttl": self.default_ttl,
            "compress": False,
            "level": CacheLevel.MEMORY
        })
    
    def _cleanup_memory_cache(self):
        """Limpa cache em memória se exceder limite"""
        current_size = sum(
            len(str(item).encode()) 
            for item in self.memory_cache.values()
        )
        
        if current_size > self.memory_limit:
            # Remover itens mais antigos
            sorted_items = sorted(
                self.memory_cache.items(),
                key=lambda x: x[1].get('timestamp', 0)
            )
            
            # Remover 25% dos itens mais antigos
            items_to_remove = len(sorted_items) // 4
            for i in range(items_to_remove):
                key = sorted_items[i][0]
                del self.memory_cache[key]
            
            logger.info(f"🧹 Cache em memória limpo: {items_to_remove} itens removidos")
    
    async def get(self, 
                  cache_type: str, 
                  identifier: str, 
                  params: Optional[Dict] = None) -> Optional[Any]:
        """
        Recupera item do cache
        
        Args:
            cache_type: Tipo de cache (llm_responses, agent_analysis, etc.)
            identifier: Identificador único
            params: Parâmetros adicionais para chave
            
        Returns:
            Dados do cache ou None se não encontrado
        """
        self.stats.total_requests += 1
        
        key = self._generate_key(cache_type, identifier, params)
        config = self._get_cache_config(cache_type)
        current_time = time.time()
        
        # Tentar cache em memória primeiro (L1)
        if config["level"] in [CacheLevel.MEMORY, CacheLevel.REDIS]:
            if key in self.memory_cache:
                item = self.memory_cache[key]
                if current_time - item["timestamp"] < config["ttl"]:
                    self.stats.hits += 1
                    self.stats.hit_rate = self.stats.hits / self.stats.total_requests
                    logger.debug(f"🎯 Cache hit (memory): {cache_type}:{identifier}")
                    return item["data"]
                else:
                    # Item expirado
                    del self.memory_cache[key]
        
        # Tentar cache Redis (L2)
        if self.redis_available and config["level"] in [CacheLevel.REDIS, CacheLevel.PERSISTENT]:
            try:
                cached_data = self.redis_client.get(key)
                if cached_data:
                    if config["compress"]:
                        data = self._decompress_data(cached_data)
                    else:
                        data = pickle.loads(cached_data)
                    
                    # Adicionar ao cache em memória para próximas consultas
                    if config["level"] == CacheLevel.REDIS:
                        self.memory_cache[key] = {
                            "data": data,
                            "timestamp": current_time
                        }
                        self._cleanup_memory_cache()
                    
                    self.stats.hits += 1
                    self.stats.hit_rate = self.stats.hits / self.stats.total_requests
                    logger.debug(f"🎯 Cache hit (redis): {cache_type}:{identifier}")
                    return data
                    
            except Exception as e:
                logger.error(f"Erro ao acessar Redis cache: {e}")
        
        # Cache miss
        self.stats.misses += 1
        self.stats.hit_rate = self.stats.hits / self.stats.total_requests
        logger.debug(f"❌ Cache miss: {cache_type}:{identifier}")
        return None
    
    async def set(self, 
                  cache_type: str, 
                  identifier: str, 
                  data: Any, 
                  params: Optional[Dict] = None,
                  custom_ttl: Optional[int] = None) -> bool:
        """
        Armazena item no cache
        
        Args:
            cache_type: Tipo de cache
            identifier: Identificador único
            data: Dados para armazenar
            params: Parâmetros adicionais para chave
            custom_ttl: TTL customizado (opcional)
            
        Returns:
            True se armazenado com sucesso
        """
        key = self._generate_key(cache_type, identifier, params)
        config = self._get_cache_config(cache_type)
        ttl = custom_ttl or config["ttl"]
        current_time = time.time()
        
        try:
            # Cache em memória (L1)
            if config["level"] in [CacheLevel.MEMORY, CacheLevel.REDIS]:
                self.memory_cache[key] = {
                    "data": data,
                    "timestamp": current_time
                }
                self._cleanup_memory_cache()
            
            # Cache Redis (L2)
            if self.redis_available and config["level"] in [CacheLevel.REDIS, CacheLevel.PERSISTENT]:
                if config["compress"]:
                    cached_data = self._compress_data(data)
                else:
                    cached_data = pickle.dumps(data)
                
                self.redis_client.setex(key, ttl, cached_data)
            
            logger.debug(f"💾 Cache set: {cache_type}:{identifier} (TTL: {ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao armazenar no cache: {e}")
            return False
    
    async def delete(self, 
                     cache_type: str, 
                     identifier: str, 
                     params: Optional[Dict] = None) -> bool:
        """Remove item do cache"""
        key = self._generate_key(cache_type, identifier, params)
        
        try:
            # Remover do cache em memória
            if key in self.memory_cache:
                del self.memory_cache[key]
            
            # Remover do Redis
            if self.redis_available:
                self.redis_client.delete(key)
            
            logger.debug(f"🗑️ Cache deleted: {cache_type}:{identifier}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao remover do cache: {e}")
            return False
    
    async def clear_cache_type(self, cache_type: str) -> int:
        """Limpa todos os itens de um tipo de cache"""
        pattern = f"cwb_cache:{cache_type}:*"
        count = 0
        
        try:
            # Limpar cache em memória
            keys_to_remove = [k for k in self.memory_cache.keys() if k.startswith(f"cwb_cache:{cache_type}:")]
            for key in keys_to_remove:
                del self.memory_cache[key]
                count += 1
            
            # Limpar Redis
            if self.redis_available:
                redis_keys = self.redis_client.keys(pattern)
                if redis_keys:
                    self.redis_client.delete(*redis_keys)
                    count += len(redis_keys)
            
            logger.info(f"🧹 Cache type cleared: {cache_type} ({count} items)")
            return count
            
        except Exception as e:
            logger.error(f"Erro ao limpar cache type: {e}")
            return 0
    
    def get_stats(self) -> CacheStats:
        """Retorna estatísticas do cache"""
        # Calcular uso de memória
        memory_usage = sum(
            len(str(item).encode()) 
            for item in self.memory_cache.values()
        )
        
        # Calcular uso do Redis
        redis_usage = 0
        if self.redis_available:
            try:
                info = self.redis_client.info('memory')
                redis_usage = info.get('used_memory', 0)
            except:
                pass
        
        # Estimar economia de custos (baseado em hit rate)
        # Assumindo $0.002 por 1K tokens de API
        estimated_api_calls_saved = self.stats.hits
        cost_savings = estimated_api_calls_saved * 0.002
        
        self.stats.memory_usage = memory_usage
        self.stats.redis_usage = redis_usage
        self.stats.cost_savings = cost_savings
        
        return self.stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema de cache"""
        health = {
            "memory_cache": {
                "status": "operational",
                "items": len(self.memory_cache),
                "usage_mb": sum(len(str(item).encode()) for item in self.memory_cache.values()) / 1024 / 1024
            },
            "redis_cache": {
                "status": "unavailable",
                "items": 0,
                "usage_mb": 0
            }
        }
        
        if self.redis_available:
            try:
                self.redis_client.ping()
                info = self.redis_client.info()
                health["redis_cache"] = {
                    "status": "operational",
                    "items": info.get('db1', {}).get('keys', 0),
                    "usage_mb": info.get('used_memory', 0) / 1024 / 1024
                }
            except Exception as e:
                health["redis_cache"]["status"] = f"error: {e}"
        
        return health

# Instância global do cache
cache_manager = AdvancedCacheManager()

# Funções de conveniência para uso fácil
async def cache_llm_response(prompt_hash: str, response: str, model: str = "default") -> bool:
    """Cache resposta de LLM"""
    return await cache_manager.set(
        "llm_responses", 
        prompt_hash, 
        response, 
        params={"model": model}
    )

async def get_cached_llm_response(prompt_hash: str, model: str = "default") -> Optional[str]:
    """Recupera resposta de LLM do cache"""
    return await cache_manager.get(
        "llm_responses", 
        prompt_hash, 
        params={"model": model}
    )

async def cache_agent_analysis(agent_id: str, analysis: Dict[str, Any], project_id: str) -> bool:
    """Cache análise de agente"""
    return await cache_manager.set(
        "agent_analysis", 
        f"{agent_id}_{project_id}", 
        analysis
    )

async def get_cached_agent_analysis(agent_id: str, project_id: str) -> Optional[Dict[str, Any]]:
    """Recupera análise de agente do cache"""
    return await cache_manager.get(
        "agent_analysis", 
        f"{agent_id}_{project_id}"
    )

async def cache_project_data(project_id: str, data: Dict[str, Any]) -> bool:
    """Cache dados de projeto"""
    return await cache_manager.set(
        "project_data", 
        project_id, 
        data
    )

async def get_cached_project_data(project_id: str) -> Optional[Dict[str, Any]]:
    """Recupera dados de projeto do cache"""
    return await cache_manager.get(
        "project_data", 
        project_id
    )

if __name__ == "__main__":
    # Teste básico do sistema de cache
    async def test_cache():
        print("🧪 Testando sistema de cache avançado...")
        
        # Teste de cache LLM
        await cache_llm_response("test_prompt_123", "Resposta de teste", "gpt-4")
        cached = await get_cached_llm_response("test_prompt_123", "gpt-4")
        print(f"✅ Cache LLM: {cached}")
        
        # Teste de cache de agente
        analysis = {"confidence": 95.5, "recommendations": ["Use React", "Implement tests"]}
        await cache_agent_analysis("ana_beatriz_costa", analysis, "proj_123")
        cached_analysis = await get_cached_agent_analysis("ana_beatriz_costa", "proj_123")
        print(f"✅ Cache Agent: {cached_analysis}")
        
        # Estatísticas
        stats = cache_manager.get_stats()
        print(f"📊 Stats: {stats}")
        
        # Health check
        health = await cache_manager.health_check()
        print(f"🏥 Health: {health}")
    
    asyncio.run(test_cache())