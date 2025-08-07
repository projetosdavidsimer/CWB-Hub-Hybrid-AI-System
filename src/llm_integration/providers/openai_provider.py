#!/usr/bin/env python3
"""
OpenAI Provider - Integração com modelos OpenAI
Melhoria #6 - Integração com Modelos de Linguagem
"""

import os
import asyncio
import time
import logging
from typing import Dict, List, Optional, Any

from .base_provider import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("⚠️ OpenAI library não instalada. Use: pip install openai")


class OpenAIProvider(BaseLLMProvider):
    """Provedor para modelos OpenAI (GPT-4, GPT-4o, etc.)"""
    
    def __init__(self):
        super().__init__("openai")
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa o cliente OpenAI"""
        if not OPENAI_AVAILABLE:
            logger.error("❌ OpenAI library não disponível")
            return
        
        # Buscar API key
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ OPENAI_API_KEY não encontrada nas variáveis de ambiente")
            return
        
        try:
            # Inicializar cliente
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            self.is_initialized = True
            logger.info("✅ OpenAI provider inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar OpenAI provider: {e}")
    
    async def generate_response(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        context: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Gera resposta usando modelo OpenAI"""
        if not self.is_available():
            raise Exception("OpenAI provider não está disponível")
        
        start_time = time.time()
        
        try:
            # Preparar mensagens
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})
            
            # Configurar parâmetros
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,
                **kwargs
            }
            
            # Fazer requisição
            async def make_request():
                return await self.client.chat.completions.create(**params)
            
            response = await self._make_request_with_retry(make_request)
            
            # Extrair dados da resposta
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            
            # Calcular custo
            cost = self._calculate_cost(model, input_tokens, output_tokens)
            
            # Atualizar estatísticas
            self._update_stats(True, tokens_used, cost)
            
            return LLMResponse(
                content=content,
                model_used=model,
                provider=self.provider_name,
                tokens_used=tokens_used,
                cost=cost,
                response_time=time.time() - start_time,
                metadata={
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "finish_reason": response.choices[0].finish_reason
                }
            )
            
        except Exception as e:
            self._update_stats(False, 0, 0)
            logger.error(f"❌ Erro na requisição OpenAI: {e}")
            raise
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Retorna modelos OpenAI disponíveis"""
        if not self.is_available():
            return []
        
        try:
            # Lista de modelos suportados (OpenAI não tem endpoint público para isso)
            models = [
                {
                    "model": "gpt-4",
                    "provider": self.provider_name,
                    "max_tokens": 8192,
                    "cost_per_token": 0.03,
                    "description": "GPT-4 modelo base"
                },
                {
                    "model": "gpt-4-turbo",
                    "provider": self.provider_name,
                    "max_tokens": 128000,
                    "cost_per_token": 0.01,
                    "description": "GPT-4 Turbo com contexto estendido"
                },
                {
                    "model": "gpt-4o",
                    "provider": self.provider_name,
                    "max_tokens": 128000,
                    "cost_per_token": 0.005,
                    "description": "GPT-4o modelo otimizado"
                },
                {
                    "model": "gpt-3.5-turbo",
                    "provider": self.provider_name,
                    "max_tokens": 16384,
                    "cost_per_token": 0.001,
                    "description": "GPT-3.5 Turbo modelo rápido"
                }
            ]
            
            return models
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter modelos OpenAI: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do provedor OpenAI"""
        if not self.is_available():
            return {
                "status": "unhealthy",
                "error": "Provider não inicializado ou API key ausente"
            }
        
        try:
            # Teste simples com o modelo mais barato
            test_response = await self.generate_response(
                prompt="Hello",
                model="gpt-3.5-turbo",
                max_tokens=5,
                temperature=0
            )
            
            return {
                "status": "healthy",
                "provider": self.provider_name,
                "test_response_time": test_response.response_time,
                "available_models": len(await self.get_available_models()),
                "stats": self.get_stats()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": self.provider_name,
                "error": str(e)
            }
    
    async def get_embeddings(self, text: str, model: str = "text-embedding-ada-002") -> List[float]:
        """Gera embeddings usando OpenAI"""
        if not self.is_available():
            raise Exception("OpenAI provider não está disponível")
        
        try:
            response = await self.client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar embeddings: {e}")
            raise
    
    async def moderate_content(self, text: str) -> Dict[str, Any]:
        """Modera conteúdo usando OpenAI Moderation"""
        if not self.is_available():
            raise Exception("OpenAI provider não está disponível")
        
        try:
            response = await self.client.moderations.create(input=text)
            result = response.results[0]
            
            return {
                "flagged": result.flagged,
                "categories": dict(result.categories),
                "category_scores": dict(result.category_scores)
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na moderação de conteúdo: {e}")
            raise