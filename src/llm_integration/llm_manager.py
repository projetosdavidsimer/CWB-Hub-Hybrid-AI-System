#!/usr/bin/env python3
"""
LLM Manager - Gerenciador central de modelos de linguagem
Melhoria #6 - Integração com Modelos de Linguagem
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import time
import json

from .providers.base_provider import BaseLLMProvider
from .providers.openai_provider import OpenAIProvider
from .providers.anthropic_provider import AnthropicProvider
from .providers.gemini_provider import GeminiProvider
from .cache_manager import CacheManager
from ..utils.advanced_cache import cache_manager as advanced_cache, cache_llm_response, get_cached_llm_response
from .cost_monitor import CostMonitor
from .prompt_optimizer import PromptOptimizer

logger = logging.getLogger(__name__)


class LLMModel(Enum):
    """Modelos de LLM disponíveis"""
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet-20240620"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    GEMINI_PRO = "gemini-pro"
    GEMINI_PRO_VISION = "gemini-pro-vision"


@dataclass
class LLMRequest:
    """Estrutura de requisição para LLM"""
    prompt: str
    agent_id: str
    context: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: float = 0.7
    model_preference: Optional[LLMModel] = None
    use_cache: bool = True
    priority: str = "normal"  # low, normal, high, critical


@dataclass
class LLMResponse:
    """Estrutura de resposta do LLM"""
    content: str
    model_used: str
    provider: str
    tokens_used: int
    cost: float
    response_time: float
    cached: bool = False
    confidence_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class LLMManager:
    """Gerenciador central de modelos de linguagem"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.cache_manager = CacheManager()
        self.advanced_cache = advanced_cache
        self.cost_monitor = CostMonitor()
        self.prompt_optimizer = PromptOptimizer()
        
        # Configurações
        self.fallback_chain = [
            LLMModel.GPT_4O,
            LLMModel.CLAUDE_3_5_SONNET,
            LLMModel.GEMINI_PRO,
            LLMModel.GPT_4_TURBO
        ]
        
        # Estatísticas
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "cache_hits": 0,
            "total_cost": 0.0,
            "average_response_time": 0.0
        }
        
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Inicializa os provedores de LLM"""
        try:
            # OpenAI
            self.providers["openai"] = OpenAIProvider()
            logger.info("✅ OpenAI provider inicializado")
        except Exception as e:
            logger.warning(f"⚠️ OpenAI provider não disponível: {e}")
        
        try:
            # Anthropic
            self.providers["anthropic"] = AnthropicProvider()
            logger.info("✅ Anthropic provider inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Anthropic provider não disponível: {e}")
        
        try:
            # Google Gemini
            self.providers["gemini"] = GeminiProvider()
            logger.info("✅ Gemini provider inicializado")
        except Exception as e:
            logger.warning(f"⚠️ Gemini provider não disponível: {e}")
    
    async def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Gera resposta usando o melhor modelo disponível"""
        start_time = time.time()
        self.stats["total_requests"] += 1
        
        try:
            # Verificar cache avançado primeiro
            if request.use_cache:
                # Gerar hash do prompt para cache
                import hashlib
                prompt_data = f"{request.prompt}:{request.agent_id}:{request.context or ''}"
                prompt_hash = hashlib.md5(prompt_data.encode()).hexdigest()
                
                # Tentar cache avançado
                cached_content = await get_cached_llm_response(
                    prompt_hash, 
                    request.model_preference.value if request.model_preference else "default"
                )
                
                if cached_content:
                    self.stats["cache_hits"] += 1
                    return LLMResponse(
                        content=cached_content,
                        model_used="cached",
                        provider="cache",
                        tokens_used=0,
                        cost=0.0,
                        response_time=0.001,
                        cached=True
                    )
                
                # Fallback para cache original
                cached_response = await self.cache_manager.get_cached_response(
                    request.prompt, request.agent_id, request.context
                )
                if cached_response:
                    self.stats["cache_hits"] += 1
                    cached_response.cached = True
                    return cached_response
            
            # Otimizar prompt
            optimized_prompt = await self.prompt_optimizer.optimize_prompt(
                request.prompt, request.agent_id
            )
            request.prompt = optimized_prompt
            
            # Determinar modelo a usar
            model_to_use = self._select_best_model(request)
            
            # Gerar resposta
            response = await self._generate_with_fallback(request, model_to_use)
            
            # Monitorar custos
            await self.cost_monitor.track_usage(
                response.model_used, response.tokens_used, response.cost
            )
            
            # Cache da resposta no sistema avançado
            if request.use_cache and response.content:
                # Cache avançado
                import hashlib
                prompt_data = f"{request.prompt}:{request.agent_id}:{request.context or ''}"
                prompt_hash = hashlib.md5(prompt_data.encode()).hexdigest()
                
                await cache_llm_response(
                    prompt_hash, 
                    response.content,
                    response.model_used
                )
                
                # Cache original (fallback)
                await self.cache_manager.cache_response(
                    request.prompt, request.agent_id, request.context, response
                )
            
            # Atualizar estatísticas
            self.stats["successful_requests"] += 1
            self.stats["total_cost"] += response.cost
            
            response_time = time.time() - start_time
            response.response_time = response_time
            self._update_average_response_time(response_time)
            
            return response
            
        except Exception as e:
            self.stats["failed_requests"] += 1
            logger.error(f"❌ Erro ao gerar resposta: {e}")
            
            # Resposta de fallback
            return LLMResponse(
                content=f"Desculpe, ocorreu um erro ao processar sua solicitação: {str(e)}",
                model_used="fallback",
                provider="system",
                tokens_used=0,
                cost=0.0,
                response_time=time.time() - start_time,
                cached=False
            )
    
    def _select_best_model(self, request: LLMRequest) -> LLMModel:
        """Seleciona o melhor modelo baseado na requisição"""
        # Se há preferência específica, usar ela
        if request.model_preference:
            return request.model_preference
        
        # Seleção baseada na prioridade
        if request.priority == "critical":
            return LLMModel.GPT_4O
        elif request.priority == "high":
            return LLMModel.CLAUDE_3_5_SONNET
        elif request.priority == "low":
            return LLMModel.GEMINI_PRO
        else:
            return LLMModel.GPT_4O  # Default
    
    async def _generate_with_fallback(self, request: LLMRequest, primary_model: LLMModel) -> LLMResponse:
        """Gera resposta com sistema de fallback"""
        # Criar lista de modelos para tentar
        models_to_try = [primary_model]
        for model in self.fallback_chain:
            if model != primary_model and model not in models_to_try:
                models_to_try.append(model)
        
        last_error = None
        
        for model in models_to_try:
            try:
                provider = self._get_provider_for_model(model)
                if not provider:
                    continue
                
                response = await provider.generate_response(
                    prompt=request.prompt,
                    model=model.value,
                    max_tokens=request.max_tokens,
                    temperature=request.temperature,
                    context=request.context
                )
                
                return response
                
            except Exception as e:
                last_error = e
                logger.warning(f"⚠️ Falha com modelo {model.value}: {e}")
                continue
        
        # Se todos falharam, levantar último erro
        raise last_error or Exception("Todos os modelos falharam")
    
    def _get_provider_for_model(self, model: LLMModel) -> Optional[BaseLLMProvider]:
        """Retorna o provedor apropriado para o modelo"""
        if model.value.startswith("gpt"):
            return self.providers.get("openai")
        elif model.value.startswith("claude"):
            return self.providers.get("anthropic")
        elif model.value.startswith("gemini"):
            return self.providers.get("gemini")
        return None
    
    def _update_average_response_time(self, response_time: float):
        """Atualiza tempo médio de resposta"""
        current_avg = self.stats["average_response_time"]
        total_requests = self.stats["successful_requests"]
        
        if total_requests == 1:
            self.stats["average_response_time"] = response_time
        else:
            self.stats["average_response_time"] = (
                (current_avg * (total_requests - 1) + response_time) / total_requests
            )
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Retorna lista de modelos disponíveis"""
        models = []
        
        for provider_name, provider in self.providers.items():
            try:
                provider_models = await provider.get_available_models()
                for model in provider_models:
                    models.append({
                        "model": model["model"],
                        "provider": provider_name,
                        "status": "available",
                        "cost_per_token": model.get("cost_per_token", 0),
                        "max_tokens": model.get("max_tokens", 4096)
                    })
            except Exception as e:
                logger.warning(f"⚠️ Erro ao obter modelos de {provider_name}: {e}")
        
        return models
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do sistema LLM"""
        health_status = {
            "status": "healthy",
            "providers": {},
            "statistics": self.stats.copy(),
            "cache_status": await self.cache_manager.get_cache_stats(),
            "advanced_cache_status": await self.advanced_cache.health_check(),
            "advanced_cache_stats": self.advanced_cache.get_stats(),
            "cost_status": await self.cost_monitor.get_cost_summary()
        }
        
        # Verificar cada provedor
        for provider_name, provider in self.providers.items():
            try:
                provider_health = await provider.health_check()
                health_status["providers"][provider_name] = provider_health
            except Exception as e:
                health_status["providers"][provider_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
                health_status["status"] = "degraded"
        
        return health_status
    
    async def optimize_for_agent(self, agent_id: str, task_type: str) -> Dict[str, Any]:
        """Otimiza configurações para um agente específico"""
        return await self.prompt_optimizer.get_agent_optimization(agent_id, task_type)
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do sistema"""
        return {
            **self.stats,
            "success_rate": (
                self.stats["successful_requests"] / max(self.stats["total_requests"], 1) * 100
            ),
            "cache_hit_rate": (
                self.stats["cache_hits"] / max(self.stats["total_requests"], 1) * 100
            )
        }


# Instância global do gerenciador
llm_manager = LLMManager()