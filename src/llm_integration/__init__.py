#!/usr/bin/env python3
"""
CWB Hub LLM Integration System
Melhoria #6 - Integração com Modelos de Linguagem

Sistema unificado para integração com múltiplos modelos de linguagem:
- OpenAI GPT-4/GPT-4o
- Anthropic Claude 3.5
- Google Gemini Pro
- Sistema de fallback inteligente
- Cache e otimização de custos
"""

from .llm_manager import LLMManager
from .providers import OpenAIProvider, AnthropicProvider, GeminiProvider
from .cache_manager import CacheManager
from .cost_monitor import CostMonitor
from .prompt_optimizer import PromptOptimizer

__version__ = "1.0.0"
__author__ = "CWB Hub Team"

__all__ = [
    "LLMManager",
    "OpenAIProvider", 
    "AnthropicProvider",
    "GeminiProvider",
    "CacheManager",
    "CostMonitor",
    "PromptOptimizer"
]