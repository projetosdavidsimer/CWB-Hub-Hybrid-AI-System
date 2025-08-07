#!/usr/bin/env python3
"""
Configuração para integração LLM
Melhoria #6 - Integração com Modelos de Linguagem
"""

import os
from typing import Dict, Any

# Configurações de API Keys
LLM_API_KEYS = {
    "openai": os.getenv("OPENAI_API_KEY"),
    "anthropic": os.getenv("ANTHROPIC_API_KEY"),
    "gemini": os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
}

# Configurações de modelos padrão
DEFAULT_MODELS = {
    "openai": "gpt-4o",
    "anthropic": "claude-3-5-sonnet-20240620",
    "gemini": "gemini-pro"
}

# Configurações de fallback
FALLBACK_CHAIN = [
    "gpt-4o",
    "claude-3-5-sonnet-20240620", 
    "gemini-pro",
    "gpt-4-turbo"
]

# Configurações de cache
CACHE_CONFIG = {
    "enabled": True,
    "ttl_seconds": 3600 * 24 * 7,  # 7 dias
    "max_memory_entries": 1000,
    "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379")
}

# Configurações de custo
COST_CONFIG = {
    "daily_limit": float(os.getenv("LLM_DAILY_LIMIT", "50.0")),
    "weekly_limit": float(os.getenv("LLM_WEEKLY_LIMIT", "300.0")),
    "monthly_limit": float(os.getenv("LLM_MONTHLY_LIMIT", "1000.0")),
    "per_request_limit": float(os.getenv("LLM_REQUEST_LIMIT", "5.0"))
}

# Configurações de rate limiting
RATE_LIMIT_CONFIG = {
    "requests_per_minute": {
        "openai": 60,
        "anthropic": 50,
        "gemini": 60
    },
    "tokens_per_minute": {
        "openai": 100000,
        "anthropic": 80000,
        "gemini": 120000
    }
}

# Configurações de timeout
TIMEOUT_CONFIG = {
    "request_timeout": 30,  # segundos
    "retry_attempts": 3,
    "backoff_factor": 1.5
}

# Configurações de qualidade
QUALITY_CONFIG = {
    "min_confidence_score": 0.7,
    "enable_content_moderation": True,
    "enable_response_validation": True
}

# Mapeamento de agentes para modelos preferidos
AGENT_MODEL_PREFERENCES = {
    "ana_beatriz_costa": {
        "primary": "gpt-4o",
        "fallback": "claude-3-5-sonnet-20240620",
        "temperature": 0.7,
        "max_tokens": 2048
    },
    "carlos_eduardo_santos": {
        "primary": "claude-3-5-sonnet-20240620",
        "fallback": "gpt-4o",
        "temperature": 0.3,
        "max_tokens": 4096
    },
    "sofia_oliveira": {
        "primary": "gpt-4o",
        "fallback": "gemini-pro",
        "temperature": 0.5,
        "max_tokens": 3072
    },
    "gabriel_mendes": {
        "primary": "gpt-4o",
        "fallback": "claude-3-5-sonnet-20240620",
        "temperature": 0.6,
        "max_tokens": 2048
    },
    "isabella_santos": {
        "primary": "claude-3-5-sonnet-20240620",
        "fallback": "gpt-4o",
        "temperature": 0.8,
        "max_tokens": 2048
    },
    "lucas_pereira": {
        "primary": "gpt-4o",
        "fallback": "claude-3-5-sonnet-20240620",
        "temperature": 0.2,
        "max_tokens": 3072
    },
    "mariana_rodrigues": {
        "primary": "claude-3-5-sonnet-20240620",
        "fallback": "gpt-4o",
        "temperature": 0.4,
        "max_tokens": 3072
    },
    "pedro_henrique_almeida": {
        "primary": "gpt-4o",
        "fallback": "claude-3-5-sonnet-20240620",
        "temperature": 0.6,
        "max_tokens": 2048
    }
}

def get_config() -> Dict[str, Any]:
    """Retorna configuração completa"""
    return {
        "api_keys": LLM_API_KEYS,
        "default_models": DEFAULT_MODELS,
        "fallback_chain": FALLBACK_CHAIN,
        "cache": CACHE_CONFIG,
        "cost": COST_CONFIG,
        "rate_limit": RATE_LIMIT_CONFIG,
        "timeout": TIMEOUT_CONFIG,
        "quality": QUALITY_CONFIG,
        "agent_preferences": AGENT_MODEL_PREFERENCES
    }

def validate_config() -> Dict[str, Any]:
    """Valida configuração e retorna status"""
    issues = []
    warnings = []
    
    # Verificar API keys
    for provider, key in LLM_API_KEYS.items():
        if not key:
            issues.append(f"API key não configurada para {provider}")
    
    # Verificar limites de custo
    if COST_CONFIG["daily_limit"] <= 0:
        warnings.append("Limite diário de custo não configurado")
    
    # Verificar configuração Redis
    if CACHE_CONFIG["enabled"] and not CACHE_CONFIG["redis_url"]:
        warnings.append("Cache habilitado mas Redis URL não configurada")
    
    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "providers_available": [
            provider for provider, key in LLM_API_KEYS.items() if key
        ]
    }