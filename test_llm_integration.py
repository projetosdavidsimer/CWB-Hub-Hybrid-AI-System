#!/usr/bin/env python3
"""
Teste simples da integração LLM
Melhoria #6 - Integração com Modelos de Linguagem
"""

import asyncio
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.ana_beatriz_costa import AnaBeatrizCosta


async def test_llm_integration():
    """Testa integração LLM com agente Ana Beatriz"""
    print("🧪 Testando integração LLM com CWB Hub")
    print("=" * 50)
    
    # Inicializar agente
    ana = AnaBeatrizCosta()
    print(f"✅ Agente inicializado: {ana.profile.name}")
    
    # Verificar status LLM
    llm_status = await ana.get_llm_health_status()
    print(f"🔍 Status LLM: {llm_status['status']}")
    
    if llm_status['status'] == 'unavailable':
        print("⚠️  Sistema LLM não disponível - testando modo fallback")
    
    # Teste de análise
    print("\n📋 Testando análise de requisição...")
    request = "Preciso desenvolver um sistema de e-commerce escalável com microserviços"
    
    try:
        analysis = await ana.analyze_request(request)
        print("✅ Análise gerada com sucesso!")
        print(f"📝 Resumo: {analysis[:200]}...")
        
        # Verificar se é resposta LLM ou fallback
        if "seria necessário acesso aos modelos de IA avançados" in analysis:
            print("🔄 Usando modo fallback (LLM não disponível)")
        else:
            print("🚀 Usando sistema LLM completo!")
            
    except Exception as e:
        print(f"❌ Erro na análise: {e}")
    
    # Teste de colaboração
    print("\n🤝 Testando colaboração...")
    try:
        collaboration = await ana.collaborate_with(
            "carlos_eduardo_santos", 
            "Arquitetura de microserviços para e-commerce"
        )
        print("✅ Colaboração gerada com sucesso!")
        print(f"📝 Resumo: {collaboration[:200]}...")
        
    except Exception as e:
        print(f"❌ Erro na colaboração: {e}")
    
    # Informações do agente
    print("\n👤 Informações do agente:")
    info = ana.get_agent_info()
    print(f"   Nome: {info['profile']['name']}")
    print(f"   Papel: {info['profile']['role']}")
    print(f"   Interações: {info['status']['interactions_count']}")
    print(f"   Colaborações: {info['status']['collaborations_count']}")
    
    print("\n🎉 Teste concluído!")


if __name__ == "__main__":
    asyncio.run(test_llm_integration())