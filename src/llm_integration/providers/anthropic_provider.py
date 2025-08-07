#!/usr/bin/env python3
"""
Anthropic Provider - Integração com modelos Claude
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
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("⚠️ Anthropic library não instalada. Use: pip install anthropic")


class AnthropicProvider(BaseLLMProvider):
    """Provedor para modelos Anthropic (Claude)"""
    
    def __init__(self):
        super().__init__("anthropic")
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa o cliente Anthropic"""
        if not ANTHROPIC_AVAILABLE:
            logger.error("❌ Anthropic library não disponível")
            return
        
        # Buscar API key
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ ANTHROPIC_API_KEY não encontrada nas variáveis de ambiente")
            return
        
        try:
            # Inicializar cliente
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
            self.is_initialized = True
            logger.info("✅ Anthropic provider inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Anthropic provider: {e}")
    
    async def generate_response(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        context: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Gera resposta usando modelo Claude"""
        if not self.is_available():
            raise Exception("Anthropic provider não está disponível")
        
        start_time = time.time()
        
        try:
            # Preparar mensagens
            messages = []
            if context:
                # Claude usa system message separadamente
                system_message = context
            else:
                system_message = None
            
            messages.append({"role": "user", "content": prompt})
            
            # Configurar parâmetros
            params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens or 4096,
                **kwargs
            }
            
            if system_message:
                params["system"] = system_message
            
            # Fazer requisição
            async def make_request():
                return await self.client.messages.create(**params)
            
            response = await self._make_request_with_retry(make_request)
            
            # Extrair dados da resposta
            content = response.content[0].text
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens
            tokens_used = input_tokens + output_tokens
            
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
                    "stop_reason": response.stop_reason
                }
            )
            
        except Exception as e:
            self._update_stats(False, 0, 0)
            logger.error(f"❌ Erro na requisição Anthropic: {e}")
            raise
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Retorna modelos Claude disponíveis"""
        if not self.is_available():
            return []
        
        try:
            # Lista de modelos suportados
            models = [
                {
                    "model": "claude-3-5-sonnet-20240620",
                    "provider": self.provider_name,
                    "max_tokens": 200000,
                    "cost_per_token": 0.003,
                    "description": "Claude 3.5 Sonnet - Modelo mais avançado"
                },
                {
                    "model": "claude-3-opus-20240229",
                    "provider": self.provider_name,
                    "max_tokens": 200000,
                    "cost_per_token": 0.015,
                    "description": "Claude 3 Opus - Máxima capacidade"
                },
                {
                    "model": "claude-3-sonnet-20240229",
                    "provider": self.provider_name,
                    "max_tokens": 200000,
                    "cost_per_token": 0.003,
                    "description": "Claude 3 Sonnet - Balanceado"
                },
                {
                    "model": "claude-3-haiku-20240307",
                    "provider": self.provider_name,
                    "max_tokens": 200000,
                    "cost_per_token": 0.00025,
                    "description": "Claude 3 Haiku - Rápido e eficiente"
                }
            ]
            
            return models
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter modelos Anthropic: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do provedor Anthropic"""
        if not self.is_available():
            return {
                "status": "unhealthy",
                "error": "Provider não inicializado ou API key ausente"
            }
        
        try:
            # Teste simples com o modelo mais barato
            test_response = await self.generate_response(
                prompt="Hello",
                model="claude-3-haiku-20240307",
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
    
    async def analyze_content(self, text: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analisa conteúdo usando Claude"""
        if not self.is_available():
            raise Exception("Anthropic provider não está disponível")
        
        analysis_prompts = {
            "general": "Analyze this text and provide insights about its content, tone, and key points:",
            "sentiment": "Analyze the sentiment of this text (positive, negative, neutral) and explain why:",
            "summary": "Provide a concise summary of this text:",
            "quality": "Evaluate the quality of this text in terms of clarity, coherence, and usefulness:"
        }
        
        prompt = analysis_prompts.get(analysis_type, analysis_prompts["general"])
        full_prompt = f"{prompt}\n\nText: {text}"
        
        try:
            response = await self.generate_response(
                prompt=full_prompt,
                model="claude-3-haiku-20240307",  # Usar modelo mais barato para análise
                max_tokens=1000,
                temperature=0.3
            )
            
            return {
                "analysis": response.content,
                "analysis_type": analysis_type,
                "cost": response.cost,
                "tokens_used": response.tokens_used
            }
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de conteúdo: {e}")
            raise