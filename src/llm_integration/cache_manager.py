#!/usr/bin/env python3
"""
Cache Manager - Sistema de cache inteligente para respostas LLM
Melhoria #6 - Integração com Modelos de Linguagem
"""

import hashlib
import json
import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import asyncio

logger = logging.getLogger(__name__)

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("⚠️ Redis não disponível. Cache será em memória apenas.")


@dataclass
class CacheEntry:
    """Entrada do cache"""
    content: str
    model_used: str
    provider: str
    tokens_used: int
    cost: float
    timestamp: float
    hit_count: int = 0
    agent_id: Optional[str] = None
    context_hash: Optional[str] = None


class CacheManager:
    """Gerenciador de cache inteligente para respostas LLM"""
    
    def __init__(self):
        self.memory_cache: Dict[str, CacheEntry] = {}
        self.redis_client = None
        self.cache_ttl = 3600 * 24 * 7  # 7 dias
        self.max_memory_entries = 1000
        self.stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_saves": 0,
            "memory_hits": 0,
            "redis_hits": 0
        }
        
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Inicializa conexão Redis se disponível"""
        if not REDIS_AVAILABLE:
            logger.info("📝 Cache funcionando apenas em memória")
            return
        
        try:
            import os
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            self.redis_client = redis.from_url(redis_url)
            logger.info("✅ Cache Redis inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Erro ao conectar Redis: {e}. Usando cache em memória.")
    
    def _generate_cache_key(self, prompt: str, agent_id: str, context: Optional[str] = None) -> str:
        """Gera chave única para o cache"""
        # Normalizar prompt
        normalized_prompt = prompt.strip().lower()
        
        # Incluir contexto se fornecido
        cache_data = {
            "prompt": normalized_prompt,
            "agent_id": agent_id,
            "context": context
        }
        
        # Gerar hash
        cache_string = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_string.encode()).hexdigest()
    
    async def get_cached_response(
        self, 
        prompt: str, 
        agent_id: str, 
        context: Optional[str] = None
    ) -> Optional[Any]:
        """Busca resposta no cache"""
        self.stats["total_requests"] += 1
        cache_key = self._generate_cache_key(prompt, agent_id, context)
        
        # Tentar cache em memória primeiro
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            entry.hit_count += 1
            self.stats["cache_hits"] += 1
            self.stats["memory_hits"] += 1
            
            logger.debug(f"🎯 Cache hit (memória): {cache_key[:8]}...")
            return self._entry_to_response(entry)
        
        # Tentar Redis se disponível
        if self.redis_client:
            try:
                cached_data = await self.redis_client.get(f"llm_cache:{cache_key}")
                if cached_data:
                    entry_dict = json.loads(cached_data)
                    entry = CacheEntry(**entry_dict)
                    entry.hit_count += 1
                    
                    # Mover para cache em memória
                    self._add_to_memory_cache(cache_key, entry)
                    
                    # Atualizar hit count no Redis
                    await self.redis_client.setex(
                        f"llm_cache:{cache_key}",
                        self.cache_ttl,
                        json.dumps(asdict(entry))
                    )
                    
                    self.stats["cache_hits"] += 1
                    self.stats["redis_hits"] += 1
                    
                    logger.debug(f"🎯 Cache hit (Redis): {cache_key[:8]}...")
                    return self._entry_to_response(entry)
                    
            except Exception as e:
                logger.warning(f"⚠️ Erro ao buscar no Redis: {e}")
        
        self.stats["cache_misses"] += 1
        return None
    
    async def cache_response(
        self,
        prompt: str,
        agent_id: str,
        context: Optional[str],
        response: Any
    ):
        """Armazena resposta no cache"""
        cache_key = self._generate_cache_key(prompt, agent_id, context)
        
        # Criar entrada do cache
        entry = CacheEntry(
            content=response.content,
            model_used=response.model_used,
            provider=response.provider,
            tokens_used=response.tokens_used,
            cost=response.cost,
            timestamp=time.time(),
            agent_id=agent_id,
            context_hash=hashlib.md5(context.encode()).hexdigest() if context else None
        )
        
        # Adicionar ao cache em memória
        self._add_to_memory_cache(cache_key, entry)
        
        # Adicionar ao Redis se disponível
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    f"llm_cache:{cache_key}",
                    self.cache_ttl,
                    json.dumps(asdict(entry))
                )
            except Exception as e:
                logger.warning(f"⚠️ Erro ao salvar no Redis: {e}")
        
        self.stats["cache_saves"] += 1
        logger.debug(f"💾 Resposta cacheada: {cache_key[:8]}...")
    
    def _add_to_memory_cache(self, cache_key: str, entry: CacheEntry):
        """Adiciona entrada ao cache em memória"""
        # Limpar cache se necessário
        if len(self.memory_cache) >= self.max_memory_entries:
            self._cleanup_memory_cache()
        
        self.memory_cache[cache_key] = entry
    
    def _cleanup_memory_cache(self):
        """Limpa entradas antigas do cache em memória"""
        # Ordenar por timestamp e hit_count
        sorted_entries = sorted(
            self.memory_cache.items(),
            key=lambda x: (x[1].hit_count, x[1].timestamp)
        )
        
        # Remover 20% das entradas menos usadas
        entries_to_remove = len(sorted_entries) // 5
        for i in range(entries_to_remove):
            key = sorted_entries[i][0]
            del self.memory_cache[key]
        
        logger.debug(f"🧹 Cache limpo: {entries_to_remove} entradas removidas")
    
    def _entry_to_response(self, entry: CacheEntry) -> Any:
        """Converte entrada do cache para objeto de resposta"""
        from .llm_manager import LLMResponse
        
        return LLMResponse(
            content=entry.content,
            model_used=entry.model_used,
            provider=entry.provider,
            tokens_used=entry.tokens_used,
            cost=entry.cost,
            response_time=0.001,  # Cache é muito rápido
            cached=True,
            metadata={
                "cache_timestamp": entry.timestamp,
                "cache_hit_count": entry.hit_count
            }
        )
    
    async def invalidate_cache(self, pattern: Optional[str] = None):
        """Invalida entradas do cache"""
        if pattern:
            # Invalidar por padrão
            keys_to_remove = [
                key for key in self.memory_cache.keys() 
                if pattern in key
            ]
            for key in keys_to_remove:
                del self.memory_cache[key]
            
            # Invalidar no Redis
            if self.redis_client:
                try:
                    keys = await self.redis_client.keys(f"llm_cache:*{pattern}*")
                    if keys:
                        await self.redis_client.delete(*keys)
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao invalidar Redis: {e}")
        else:
            # Limpar todo o cache
            self.memory_cache.clear()
            if self.redis_client:
                try:
                    keys = await self.redis_client.keys("llm_cache:*")
                    if keys:
                        await self.redis_client.delete(*keys)
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao limpar Redis: {e}")
        
        logger.info(f"🗑️ Cache invalidado: {pattern or 'todos'}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do cache"""
        memory_size = len(self.memory_cache)
        redis_size = 0
        
        if self.redis_client:
            try:
                keys = await self.redis_client.keys("llm_cache:*")
                redis_size = len(keys)
            except Exception:
                redis_size = -1  # Erro
        
        hit_rate = (
            self.stats["cache_hits"] / max(self.stats["total_requests"], 1) * 100
        )
        
        return {
            **self.stats,
            "hit_rate_percent": hit_rate,
            "memory_cache_size": memory_size,
            "redis_cache_size": redis_size,
            "cache_ttl_hours": self.cache_ttl / 3600
        }
    
    async def get_popular_prompts(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retorna prompts mais populares do cache"""
        # Ordenar por hit_count
        sorted_entries = sorted(
            self.memory_cache.items(),
            key=lambda x: x[1].hit_count,
            reverse=True
        )
        
        popular = []
        for i, (key, entry) in enumerate(sorted_entries[:limit]):
            popular.append({
                "rank": i + 1,
                "cache_key": key[:8] + "...",
                "hit_count": entry.hit_count,
                "agent_id": entry.agent_id,
                "model_used": entry.model_used,
                "cost_saved": entry.cost * (entry.hit_count - 1),
                "timestamp": entry.timestamp
            })
        
        return popular
    
    async def optimize_cache(self):
        """Otimiza o cache removendo entradas antigas e pouco usadas"""
        current_time = time.time()
        removed_count = 0
        
        # Remover entradas muito antigas (mais de TTL)
        keys_to_remove = []
        for key, entry in self.memory_cache.items():
            if current_time - entry.timestamp > self.cache_ttl:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.memory_cache[key]
            removed_count += 1
        
        # Limpar cache se ainda muito grande
        if len(self.memory_cache) > self.max_memory_entries * 0.8:
            self._cleanup_memory_cache()
            removed_count += len(keys_to_remove)
        
        logger.info(f"🔧 Cache otimizado: {removed_count} entradas removidas")
        return removed_count