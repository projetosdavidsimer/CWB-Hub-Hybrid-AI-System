#!/usr/bin/env python3
"""
Base Provider - Classe base para provedores de LLM
Melhoria #6 - Integração com Modelos de Linguagem
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import time
import logging

logger = logging.getLogger(__name__)


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


class BaseLLMProvider(ABC):
    """Classe base para todos os provedores de LLM"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.is_initialized = False
        self.api_key = None
        self.rate_limits = {
            "requests_per_minute": 60,
            "tokens_per_minute": 100000
        }
        self.stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0
        }
    
    @abstractmethod
    async def generate_response(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        context: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Gera resposta usando o modelo especificado"""
        pass
    
    @abstractmethod
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Retorna lista de modelos disponíveis"""
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do provedor"""
        pass
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calcula custo baseado no modelo e tokens"""
        # Preços aproximados por 1K tokens (atualizar conforme necessário)
        pricing = {
            # OpenAI
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            
            # Anthropic
            "claude-3-5-sonnet-20240620": {"input": 0.003, "output": 0.015},
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
            
            # Google
            "gemini-pro": {"input": 0.0005, "output": 0.0015},
            "gemini-pro-vision": {"input": 0.0005, "output": 0.0015}
        }
        
        model_pricing = pricing.get(model, {"input": 0.001, "output": 0.002})
        
        input_cost = (input_tokens / 1000) * model_pricing["input"]
        output_cost = (output_tokens / 1000) * model_pricing["output"]
        
        return input_cost + output_cost
    
    def _estimate_tokens(self, text: str) -> int:
        """Estima número de tokens em um texto"""
        # Estimativa aproximada: ~4 caracteres por token
        return len(text) // 4
    
    def _update_stats(self, success: bool, tokens: int, cost: float):
        """Atualiza estatísticas do provedor"""
        self.stats["total_requests"] += 1
        if success:
            self.stats["successful_requests"] += 1
            self.stats["total_tokens"] += tokens
            self.stats["total_cost"] += cost
        else:
            self.stats["failed_requests"] += 1
    
    async def _make_request_with_retry(
        self,
        request_func,
        max_retries: int = 3,
        backoff_factor: float = 1.0
    ):
        """Faz requisição com retry automático"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return await request_func()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = backoff_factor * (2 ** attempt)
                    logger.warning(
                        f"⚠️ Tentativa {attempt + 1} falhou para {self.provider_name}: {e}. "
                        f"Tentando novamente em {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"❌ Todas as tentativas falharam para {self.provider_name}")
        
        raise last_exception
    
    def get_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas do provedor"""
        total_requests = self.stats["total_requests"]
        return {
            **self.stats,
            "success_rate": (
                self.stats["successful_requests"] / max(total_requests, 1) * 100
            ),
            "average_cost_per_request": (
                self.stats["total_cost"] / max(self.stats["successful_requests"], 1)
            ),
            "average_tokens_per_request": (
                self.stats["total_tokens"] / max(self.stats["successful_requests"], 1)
            )
        }
    
    def is_available(self) -> bool:
        """Verifica se o provedor está disponível"""
        return self.is_initialized and self.api_key is not None
    
    async def validate_model(self, model: str) -> bool:
        """Valida se o modelo está disponível"""
        try:
            available_models = await self.get_available_models()
            return any(m["model"] == model for m in available_models)
        except Exception:
            return False