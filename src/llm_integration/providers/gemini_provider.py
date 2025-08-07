#!/usr/bin/env python3
"""
Google Gemini Provider - Integração com modelos Gemini
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
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("⚠️ Google Generative AI library não instalada. Use: pip install google-generativeai")


class GeminiProvider(BaseLLMProvider):
    """Provedor para modelos Google Gemini"""
    
    def __init__(self):
        super().__init__("gemini")
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Inicializa o cliente Gemini"""
        if not GEMINI_AVAILABLE:
            logger.error("❌ Google Generative AI library não disponível")
            return
        
        # Buscar API key
        self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("⚠️ GOOGLE_API_KEY ou GEMINI_API_KEY não encontrada nas variáveis de ambiente")
            return
        
        try:
            # Configurar API key
            genai.configure(api_key=self.api_key)
            self.is_initialized = True
            logger.info("✅ Gemini provider inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Gemini provider: {e}")
    
    async def generate_response(
        self,
        prompt: str,
        model: str,
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        context: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Gera resposta usando modelo Gemini"""
        if not self.is_available():
            raise Exception("Gemini provider não está disponível")
        
        start_time = time.time()
        
        try:
            # Inicializar modelo
            model_instance = genai.GenerativeModel(model)
            
            # Preparar prompt
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nUser: {prompt}"
            
            # Configurar parâmetros de geração
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens or 4096,
                **kwargs
            )
            
            # Fazer requisição
            async def make_request():
                # Gemini não tem async nativo, então usamos thread pool
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        executor,
                        lambda: model_instance.generate_content(
                            full_prompt,
                            generation_config=generation_config
                        )
                    )
            
            response = await self._make_request_with_retry(make_request)
            
            # Extrair dados da resposta
            content = response.text
            
            # Estimar tokens (Gemini não fornece contagem exata)
            input_tokens = self._estimate_tokens(full_prompt)
            output_tokens = self._estimate_tokens(content)
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
                    "finish_reason": getattr(response, 'finish_reason', 'completed')
                }
            )
            
        except Exception as e:
            self._update_stats(False, 0, 0)
            logger.error(f"❌ Erro na requisição Gemini: {e}")
            raise
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Retorna modelos Gemini disponíveis"""
        if not self.is_available():
            return []
        
        try:
            # Lista de modelos suportados
            models = [
                {
                    "model": "gemini-pro",
                    "provider": self.provider_name,
                    "max_tokens": 32768,
                    "cost_per_token": 0.0005,
                    "description": "Gemini Pro - Modelo principal"
                },
                {
                    "model": "gemini-pro-vision",
                    "provider": self.provider_name,
                    "max_tokens": 16384,
                    "cost_per_token": 0.0005,
                    "description": "Gemini Pro Vision - Com capacidades visuais"
                },
                {
                    "model": "gemini-1.5-pro",
                    "provider": self.provider_name,
                    "max_tokens": 1048576,  # 1M tokens
                    "cost_per_token": 0.0035,
                    "description": "Gemini 1.5 Pro - Contexto estendido"
                },
                {
                    "model": "gemini-1.5-flash",
                    "provider": self.provider_name,
                    "max_tokens": 1048576,
                    "cost_per_token": 0.00035,
                    "description": "Gemini 1.5 Flash - Rápido e eficiente"
                }
            ]
            
            return models
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter modelos Gemini: {e}")
            return []
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do provedor Gemini"""
        if not self.is_available():
            return {
                "status": "unhealthy",
                "error": "Provider não inicializado ou API key ausente"
            }
        
        try:
            # Teste simples
            test_response = await self.generate_response(
                prompt="Hello",
                model="gemini-pro",
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
    
    async def generate_with_image(self, prompt: str, image_data: bytes, model: str = "gemini-pro-vision") -> LLMResponse:
        """Gera resposta com análise de imagem"""
        if not self.is_available():
            raise Exception("Gemini provider não está disponível")
        
        start_time = time.time()
        
        try:
            # Inicializar modelo com visão
            model_instance = genai.GenerativeModel(model)
            
            # Preparar imagem
            import PIL.Image
            import io
            image = PIL.Image.open(io.BytesIO(image_data))
            
            # Fazer requisição
            async def make_request():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    loop = asyncio.get_event_loop()
                    return await loop.run_in_executor(
                        executor,
                        lambda: model_instance.generate_content([prompt, image])
                    )
            
            response = await self._make_request_with_retry(make_request)
            
            # Processar resposta
            content = response.text
            input_tokens = self._estimate_tokens(prompt) + 1000  # Estimativa para imagem
            output_tokens = self._estimate_tokens(content)
            tokens_used = input_tokens + output_tokens
            cost = self._calculate_cost(model, input_tokens, output_tokens)
            
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
                    "has_image": True
                }
            )
            
        except Exception as e:
            self._update_stats(False, 0, 0)
            logger.error(f"❌ Erro na análise de imagem Gemini: {e}")
            raise
    
    async def count_tokens(self, text: str, model: str = "gemini-pro") -> int:
        """Conta tokens usando API do Gemini"""
        if not self.is_available():
            return self._estimate_tokens(text)
        
        try:
            model_instance = genai.GenerativeModel(model)
            
            # Usar thread pool para operação síncrona
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    executor,
                    lambda: model_instance.count_tokens(text)
                )
            
            return result.total_tokens
            
        except Exception as e:
            logger.warning(f"⚠️ Erro ao contar tokens, usando estimativa: {e}")
            return self._estimate_tokens(text)