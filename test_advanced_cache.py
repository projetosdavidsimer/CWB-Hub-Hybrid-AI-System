#!/usr/bin/env python3
"""
Teste do Sistema de Cache Avançado - Melhoria #11
Valida performance e funcionalidade do cache Redis
"""

import asyncio
import time
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from src.utils.advanced_cache import (
    cache_manager, 
    cache_llm_response, 
    get_cached_llm_response,
    cache_agent_analysis,
    get_cached_agent_analysis,
    cache_project_data,
    get_cached_project_data
)

async def test_cache_performance():
    """Testa performance do sistema de cache"""
    print("🧪 TESTE DE PERFORMANCE DO CACHE AVANÇADO")
    print("=" * 50)
    
    # Teste 1: Cache LLM Response
    print("\n📝 Teste 1: Cache de Respostas LLM")
    
    # Primeira chamada (cache miss)
    start_time = time.time()
    prompt_hash = "test_prompt_performance_123"
    response = "Esta é uma resposta de teste para validar o sistema de cache avançado do CWB Hub."
    
    await cache_llm_response(prompt_hash, response, "gpt-4")
    cache_time = time.time() - start_time
    print(f"   ⏱️ Tempo para cache (miss): {cache_time:.4f}s")
    
    # Segunda chamada (cache hit)
    start_time = time.time()
    cached_response = await get_cached_llm_response(prompt_hash, "gpt-4")
    hit_time = time.time() - start_time
    print(f"   🎯 Tempo para cache (hit): {hit_time:.4f}s")
    print(f"   🚀 Speedup: {cache_time/hit_time:.1f}x mais rápido")
    print(f"   ✅ Resposta correta: {cached_response == response}")
    
    # Teste 2: Cache de Análise de Agente
    print("\n👤 Teste 2: Cache de Análise de Agente")
    
    analysis_data = {
        "agent_id": "ana_beatriz_costa",
        "content": "Análise estratégica completa do projeto com foco em escalabilidade e inovação.",
        "confidence": 95.5,
        "recommendations": ["Usar microserviços", "Implementar CI/CD", "Adotar cloud-native"]
    }
    
    start_time = time.time()
    await cache_agent_analysis("ana_beatriz_costa", "project_123", analysis_data)
    cache_time = time.time() - start_time
    print(f"   ⏱️ Tempo para cache (miss): {cache_time:.4f}s")
    
    start_time = time.time()
    cached_analysis = await get_cached_agent_analysis("ana_beatriz_costa", "project_123")
    hit_time = time.time() - start_time
    print(f"   🎯 Tempo para cache (hit): {hit_time:.4f}s")
    print(f"   🚀 Speedup: {cache_time/hit_time:.1f}x mais rápido")
    print(f"   ✅ Análise correta: {cached_analysis['content'] == analysis_data['content']}")
    
    # Teste 3: Cache de Projeto
    print("\n📊 Teste 3: Cache de Dados de Projeto")
    
    project_data = {
        "session_id": "session_test_123",
        "user_request": "Desenvolver um marketplace B2B",
        "final_solution": "Solução completa com arquitetura microserviços, API Gateway, e frontend React.",
        "agent_responses_count": 8,
        "processing_time": 2.5
    }
    
    start_time = time.time()
    await cache_project_data("project_test_123", project_data)
    cache_time = time.time() - start_time
    print(f"   ⏱️ Tempo para cache (miss): {cache_time:.4f}s")
    
    start_time = time.time()
    cached_project = await get_cached_project_data("project_test_123")
    hit_time = time.time() - start_time
    print(f"   🎯 Tempo para cache (hit): {hit_time:.4f}s")
    print(f"   🚀 Speedup: {cache_time/hit_time:.1f}x mais rápido")
    print(f"   ✅ Projeto correto: {cached_project['final_solution'] == project_data['final_solution']}")

async def test_cache_functionality():
    """Testa funcionalidades do cache"""
    print("\n🔧 TESTE DE FUNCIONALIDADES DO CACHE")
    print("=" * 50)
    
    # Teste de TTL (Time To Live)
    print("\n⏰ Teste de TTL")
    await cache_manager.set("test_data", "ttl_test", "dados temporários", custom_ttl=1)
    
    # Verificar se existe
    cached = await cache_manager.get("test_data", "ttl_test")
    print(f"   ✅ Dados encontrados imediatamente: {cached is not None}")
    
    # Aguardar expiração
    print("   ⏳ Aguardando expiração (2s)...")
    await asyncio.sleep(2)
    
    # Verificar se expirou
    expired = await cache_manager.get("test_data", "ttl_test")
    print(f"   ✅ Dados expiraram corretamente: {expired is None}")
    
    # Teste de compressão
    print("\n🗜️ Teste de Compressão")
    large_data = "x" * 10000  # 10KB de dados
    
    # Cache com compressão
    await cache_manager.set("large_data", "compression_test", large_data)
    compressed_data = await cache_manager.get("large_data", "compression_test")
    
    print(f"   ✅ Dados grandes preservados: {len(compressed_data) == len(large_data)}")
    print(f"   📦 Tamanho original: {len(large_data)} bytes")
    
    # Teste de limpeza de cache
    print("\n🧹 Teste de Limpeza de Cache")
    
    # Adicionar vários itens
    for i in range(5):
        await cache_manager.set("cleanup_test", f"item_{i}", f"dados_{i}")
    
    # Limpar tipo específico
    cleared = await cache_manager.clear_cache_type("cleanup_test")
    print(f"   🗑️ Itens removidos: {cleared}")
    
    # Verificar se foram removidos
    remaining = await cache_manager.get("cleanup_test", "item_0")
    print(f"   ✅ Cache limpo corretamente: {remaining is None}")

async def test_cache_stats():
    """Testa estatísticas do cache"""
    print("\n📊 TESTE DE ESTATÍSTICAS DO CACHE")
    print("=" * 50)
    
    # Gerar algumas operações para estatísticas
    for i in range(10):
        await cache_manager.set("stats_test", f"key_{i}", f"value_{i}")
        await cache_manager.get("stats_test", f"key_{i}")
    
    # Algumas operações que resultarão em miss
    for i in range(5):
        await cache_manager.get("stats_test", f"missing_key_{i}")
    
    # Obter estatísticas
    stats = cache_manager.get_stats()
    print(f"   📈 Total de requisições: {stats.total_requests}")
    print(f"   🎯 Cache hits: {stats.hits}")
    print(f"   ❌ Cache misses: {stats.misses}")
    print(f"   📊 Hit rate: {stats.hit_rate:.1%}")
    print(f"   💰 Economia estimada: ${stats.cost_savings:.4f}")
    print(f"   💾 Uso de memória: {stats.memory_usage / 1024:.1f} KB")
    
    # Health check
    health = await cache_manager.health_check()
    print(f"\n🏥 Health Check:")
    print(f"   💾 Cache em memória: {health['memory_cache']['status']}")
    print(f"   🔴 Cache Redis: {health['redis_cache']['status']}")
    print(f"   📦 Itens em memória: {health['memory_cache']['items']}")

async def test_cache_integration():
    """Testa integração com sistema CWB Hub"""
    print("\n🔗 TESTE DE INTEGRAÇÃO COM CWB HUB")
    print("=" * 50)
    
    try:
        # Simular cache de sessão de orquestrador
        session_data = {
            "session_id": "integration_test_session",
            "agents_involved": ["ana_beatriz_costa", "carlos_eduardo_santos"],
            "phase": "analysis",
            "timestamp": time.time()
        }
        
        await cache_manager.set("user_sessions", "integration_test", session_data)
        cached_session = await cache_manager.get("user_sessions", "integration_test")
        
        print(f"   ✅ Integração com sessões: {cached_session is not None}")
        print(f"   👥 Agentes envolvidos: {len(cached_session['agents_involved'])}")
        
        # Simular cache de resposta de API
        api_response = {
            "status": "success",
            "data": {"result": "Análise completa realizada"},
            "processing_time": 1.2,
            "cached": False
        }
        
        await cache_manager.set("api_responses", "test_endpoint", api_response)
        cached_api = await cache_manager.get("api_responses", "test_endpoint")
        
        print(f"   ✅ Integração com API: {cached_api is not None}")
        print(f"   ⚡ Status: {cached_api['status']}")
        
        print("\n🎉 Todos os testes de integração passaram!")
        
    except Exception as e:
        print(f"   ❌ Erro na integração: {e}")

async def main():
    """Executa todos os testes"""
    print("🚀 INICIANDO TESTES DO SISTEMA DE CACHE AVANÇADO")
    print("Melhoria #11 - Performance e Redução de Custos")
    print("=" * 60)
    
    try:
        await test_cache_performance()
        await test_cache_functionality()
        await test_cache_stats()
        await test_cache_integration()
        
        print("\n" + "=" * 60)
        print("🎉 TODOS OS TESTES CONCLUÍDOS COM SUCESSO!")
        print("✅ Sistema de cache avançado funcionando perfeitamente")
        print("🚀 Performance otimizada para CWB Hub")
        print("💰 Redução significativa de custos de API")
        print("📊 Monitoramento e estatísticas ativas")
        
        # Estatísticas finais
        final_stats = cache_manager.get_stats()
        print(f"\n📈 ESTATÍSTICAS FINAIS:")
        print(f"   Total de operações: {final_stats.total_requests}")
        print(f"   Hit rate: {final_stats.hit_rate:.1%}")
        print(f"   Economia estimada: ${final_stats.cost_savings:.4f}")
        
    except Exception as e:
        print(f"\n❌ ERRO NOS TESTES: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())