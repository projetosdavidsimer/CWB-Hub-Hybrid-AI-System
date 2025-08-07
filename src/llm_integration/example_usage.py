#!/usr/bin/env python3
"""
Exemplo de uso da integração LLM
Melhoria #6 - Integração com Modelos de Linguagem
"""

import asyncio
import logging
from llm_manager import LLMManager, LLMRequest, LLMModel

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_basic_usage():
    """Exemplo básico de uso"""
    print("🚀 Exemplo básico de uso da integração LLM")
    
    # Inicializar gerenciador
    llm_manager = LLMManager()
    
    # Criar requisição
    request = LLMRequest(
        prompt="Como implementar um sistema de cache distribuído?",
        agent_id="carlos_eduardo_santos",
        context="Estamos desenvolvendo uma aplicação web de alta escala",
        temperature=0.3,
        max_tokens=1024
    )
    
    # Gerar resposta
    response = await llm_manager.generate_response(request)
    
    print(f"✅ Resposta gerada:")
    print(f"   Modelo: {response.model_used}")
    print(f"   Provedor: {response.provider}")
    print(f"   Tokens: {response.tokens_used}")
    print(f"   Custo: ${response.cost:.4f}")
    print(f"   Tempo: {response.response_time:.2f}s")
    print(f"   Cache: {'Sim' if response.cached else 'Não'}")
    print(f"\n📝 Conteúdo:\n{response.content[:200]}...")


async def example_multiple_agents():
    """Exemplo com múltiplos agentes"""
    print("\n🤝 Exemplo com múltiplos agentes")
    
    llm_manager = LLMManager()
    
    # Requisições para diferentes agentes
    requests = [
        LLMRequest(
            prompt="Qual a melhor arquitetura para um e-commerce?",
            agent_id="carlos_eduardo_santos",
            priority="high"
        ),
        LLMRequest(
            prompt="Como melhorar a UX do checkout?",
            agent_id="isabella_santos",
            priority="high"
        ),
        LLMRequest(
            prompt="Estratégia de testes para e-commerce",
            agent_id="lucas_pereira",
            priority="normal"
        )
    ]
    
    # Processar em paralelo
    tasks = [llm_manager.generate_response(req) for req in requests]
    responses = await asyncio.gather(*tasks)
    
    for i, response in enumerate(responses):
        agent_id = requests[i].agent_id
        print(f"\n👤 Resposta de {agent_id}:")
        print(f"   Modelo: {response.model_used}")
        print(f"   Custo: ${response.cost:.4f}")
        print(f"   Resumo: {response.content[:100]}...")


async def example_with_fallback():
    """Exemplo demonstrando sistema de fallback"""
    print("\n🔄 Exemplo com sistema de fallback")
    
    llm_manager = LLMManager()
    
    # Requisição com modelo específico que pode falhar
    request = LLMRequest(
        prompt="Explique machine learning em termos simples",
        agent_id="ana_beatriz_costa",
        model_preference=LLMModel.GPT_4,  # Pode não estar disponível
        temperature=0.7
    )
    
    response = await llm_manager.generate_response(request)
    
    print(f"✅ Resposta com fallback:")
    print(f"   Modelo solicitado: {request.model_preference.value}")
    print(f"   Modelo usado: {response.model_used}")
    print(f"   Funcionou fallback: {'Sim' if response.model_used != request.model_preference.value else 'Não'}")


async def example_cache_demonstration():
    """Exemplo demonstrando cache"""
    print("\n💾 Exemplo demonstrando cache")
    
    llm_manager = LLMManager()
    
    request = LLMRequest(
        prompt="O que é DevOps?",
        agent_id="mariana_rodrigues",
        use_cache=True
    )
    
    # Primeira requisição
    print("📤 Primeira requisição (sem cache)...")
    response1 = await llm_manager.generate_response(request)
    print(f"   Tempo: {response1.response_time:.2f}s")
    print(f"   Cache: {'Sim' if response1.cached else 'Não'}")
    
    # Segunda requisição (deve usar cache)
    print("📤 Segunda requisição (com cache)...")
    response2 = await llm_manager.generate_response(request)
    print(f"   Tempo: {response2.response_time:.2f}s")
    print(f"   Cache: {'Sim' if response2.cached else 'Não'}")
    
    # Verificar se o conteúdo é o mesmo
    print(f"   Conteúdo idêntico: {'Sim' if response1.content == response2.content else 'Não'}")


async def example_cost_monitoring():
    """Exemplo de monitoramento de custos"""
    print("\n💰 Exemplo de monitoramento de custos")
    
    llm_manager = LLMManager()
    
    # Fazer algumas requisições
    requests = [
        LLMRequest(prompt=f"Pergunta {i+1}: Como otimizar performance?", agent_id="sofia_oliveira")
        for i in range(3)
    ]
    
    total_cost = 0
    for i, request in enumerate(requests):
        response = await llm_manager.generate_response(request)
        total_cost += response.cost
        print(f"   Requisição {i+1}: ${response.cost:.4f}")
    
    print(f"💵 Custo total: ${total_cost:.4f}")
    
    # Obter estatísticas
    stats = llm_manager.get_stats()
    print(f"📊 Estatísticas:")
    print(f"   Total de requisições: {stats['total_requests']}")
    print(f"   Taxa de sucesso: {stats['success_rate']:.1f}%")
    print(f"   Taxa de cache: {stats['cache_hit_rate']:.1f}%")


async def example_health_check():
    """Exemplo de health check"""
    print("\n🏥 Exemplo de health check")
    
    llm_manager = LLMManager()
    
    health = await llm_manager.health_check()
    
    print(f"🔍 Status geral: {health['status']}")
    print(f"📈 Estatísticas: {health['statistics']}")
    
    print("\n🔌 Status dos provedores:")
    for provider, status in health['providers'].items():
        emoji = "✅" if status['status'] == 'healthy' else "❌"
        print(f"   {emoji} {provider}: {status['status']}")
        if 'error' in status:
            print(f"      Erro: {status['error']}")


async def example_model_selection():
    """Exemplo de seleção de modelos"""
    print("\n🎯 Exemplo de seleção de modelos")
    
    llm_manager = LLMManager()
    
    # Obter modelos disponíveis
    models = await llm_manager.get_available_models()
    
    print("📋 Modelos disponíveis:")
    for model in models[:5]:  # Mostrar apenas os primeiros 5
        print(f"   • {model['model']} ({model['provider']})")
        print(f"     Custo: ${model['cost_per_token']:.6f}/token")
        print(f"     Max tokens: {model['max_tokens']}")


async def main():
    """Função principal com todos os exemplos"""
    print("🎯 CWB Hub - Exemplos de Integração LLM")
    print("=" * 50)
    
    try:
        await example_basic_usage()
        await example_multiple_agents()
        await example_with_fallback()
        await example_cache_demonstration()
        await example_cost_monitoring()
        await example_health_check()
        await example_model_selection()
        
        print("\n🎉 Todos os exemplos executados com sucesso!")
        
    except Exception as e:
        print(f"\n❌ Erro durante execução: {e}")
        logger.exception("Erro nos exemplos")


if __name__ == "__main__":
    # Executar exemplos
    asyncio.run(main())