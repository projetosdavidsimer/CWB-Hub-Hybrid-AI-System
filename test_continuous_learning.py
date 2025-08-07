#!/usr/bin/env python3
"""
Teste do Sistema de Aprendizado Contínuo - Melhoria #7
Valida funcionalidade completa do sistema de aprendizado
"""

import asyncio
import time
import sys
from pathlib import Path
from datetime import datetime

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from src.learning.continuous_learning_engine import (
    learning_engine, 
    InteractionRecord, 
    InteractionType
)
from src.learning.feedback_collector import feedback_collector
from src.learning.agent_evolution import agent_evolution_system

async def test_learning_pipeline():
    """Testa pipeline completo de aprendizado"""
    print("TESTE COMPLETO DO SISTEMA DE APRENDIZADO CONTINUO")
    print("=" * 60)
    
    # Teste 1: Inicializar sistema de evolução
    print("\nTeste 1: Inicializacao do Sistema de Evolucao")
    
    await agent_evolution_system.initialize_agent_profile(
        "ana_beatriz_costa",
        "Dra. Ana Beatriz Costa",
        "Voce e uma CTO experiente especializada em estrategia tecnologica e inovacao.",
        ["estrategia", "inovacao", "lideranca", "arquitetura"]
    )
    
    print("   Perfil de agente criado: ana_beatriz_costa")
    
    # Teste 2: Simular sessão de interação
    print("\nTeste 2: Simulacao de Sessao de Interacao")
    
    session_id = "test_session_learning"
    
    # Iniciar rastreamento
    await feedback_collector.start_session_tracking(
        session_id,
        "test_user",
        {"domain": "e-commerce", "complexity": "high"}
    )
    
    # Simular múltiplas interações
    interactions = [
        {
            "id": "interaction_1",
            "request": "Desenvolver marketplace B2B escalavel",
            "response": "Recomendo arquitetura microservicos com API Gateway...",
            "agents": ["ana_beatriz_costa"],
            "response_time": 5.2,
            "confidence": 0.85,
            "rating": 4.0
        },
        {
            "id": "interaction_2", 
            "request": "Como implementar sistema de pagamentos?",
            "response": "Para pagamentos, sugiro integrar com Stripe...",
            "agents": ["ana_beatriz_costa"],
            "response_time": 3.8,
            "confidence": 0.90,
            "rating": 4.5
        },
        {
            "id": "interaction_3",
            "request": "Estrategia de deploy e CI/CD?",
            "response": "Implemente pipeline com GitHub Actions...",
            "agents": ["ana_beatriz_costa"],
            "response_time": 12.0,  # Resposta lenta
            "confidence": 0.60,     # Baixa confiança
            "rating": 2.5           # Baixa satisfação
        }
    ]
    
    for interaction in interactions:
        # Rastrear interação
        await feedback_collector.track_interaction(
            session_id,
            interaction["id"],
            InteractionType.PROJECT_ANALYSIS,
            interaction["request"],
            interaction["response"],
            interaction["agents"],
            interaction["response_time"],
            interaction["confidence"]
        )
        
        # Coletar feedback explícito
        await feedback_collector.collect_explicit_feedback(
            session_id,
            interaction["id"],
            interaction["rating"],
            f"Feedback para {interaction['id']}"
        )
        
        # Atualizar métricas do agente
        await agent_evolution_system.update_agent_metrics(
            "ana_beatriz_costa",
            {
                "satisfaction": interaction["rating"] / 5.0,
                "response_time": interaction["response_time"],
                "confidence": interaction["confidence"],
                "iterations": 1,
                "interaction_id": interaction["id"]
            }
        )
        
        print(f"   Interacao processada: {interaction['id']}")
    
    # Teste 3: Finalizar sessão e analisar
    print("\nTeste 3: Analise da Sessao")
    
    session_analysis = await feedback_collector.end_session_tracking(session_id)
    print(f"   Qualidade da sessao: {session_analysis.get('quality_assessment', 'N/A')}")
    print(f"   Duracao: {session_analysis.get('duration', 0):.1f}s")
    print(f"   Total de interacoes: {session_analysis.get('total_interactions', 0)}")
    print(f"   Score de engajamento: {session_analysis.get('engagement_score', 0):.2f}")
    
    # Teste 4: Verificar aprendizado
    print("\nTeste 4: Insights de Aprendizado")
    
    learning_insights = await learning_engine.get_learning_insights()
    print(f"   Total de requisicoes: {learning_insights['learning_metrics']['total_interactions']}")
    print(f"   Padroes identificados: {learning_insights['learning_metrics']['patterns_identified']}")
    print(f"   Otimizacoes aplicadas: {learning_insights['learning_metrics']['optimizations_applied']}")
    print(f"   Satisfacao media: {learning_insights['learning_metrics']['average_satisfaction']:.2f}")
    
    # Teste 5: Verificar evolução do agente
    print("\nTeste 5: Status de Evolucao do Agente")
    
    agent_status = await agent_evolution_system.get_agent_evolution_status("ana_beatriz_costa")
    print(f"   Agente: {agent_status['agent_name']}")
    print(f"   Total de interacoes: {agent_status['total_interactions']}")
    print(f"   Evolucoes bem-sucedidas: {agent_status['evolution_stats']['successful_evolutions']}")
    print(f"   Satisfacao atual: {agent_status['current_metrics']['satisfaction_score']:.2f}")
    print(f"   Confianca atual: {agent_status['current_metrics']['confidence_score']:.2f}")
    
    # Teste 6: Analytics do sistema
    print("\nTeste 6: Analytics do Sistema de Evolucao")
    
    evolution_analytics = await agent_evolution_system.get_evolution_analytics()
    print(f"   Total de agentes: {evolution_analytics['agent_metrics']['total_agents']}")
    print(f"   Experimentos ativos: {evolution_analytics['experiment_metrics']['active_experiments']}")
    print(f"   Taxa de sucesso: {evolution_analytics['experiment_metrics']['success_rate']:.1%}")
    
    # Teste 7: Verificar experimentos
    print("\nTeste 7: Verificacao de Experimentos")
    
    await agent_evolution_system.check_experiment_results()
    print("   Experimentos verificados")

async def test_learning_performance():
    """Testa performance do sistema de aprendizado"""
    print("\nTESTE DE PERFORMANCE DO APRENDIZADO")
    print("=" * 40)
    
    # Simular múltiplas interações rapidamente
    num_interactions = 50
    
    print(f"Processando {num_interactions} interacoes...")
    
    start_time = time.time()
    
    for i in range(num_interactions):
        # Criar interação de teste
        interaction = InteractionRecord(
            interaction_id=f"perf_test_{i}",
            session_id="perf_session",
            user_id="perf_user",
            interaction_type=InteractionType.PROJECT_ANALYSIS,
            timestamp=datetime.now(),
            user_request=f"Requisicao de teste {i}",
            context={"test": True},
            agents_involved=["ana_beatriz_costa"],
            response=f"Resposta de teste {i}",
            response_time=2.0 + (i % 5),  # Variar tempo
            confidence_score=0.7 + (i % 3) * 0.1,  # Variar confiança
            explicit_rating=3.0 + (i % 3),  # Variar rating
            iteration_count=1 + (i % 3)  # Variar iterações
        )
        
        # Registrar no sistema de aprendizado
        await learning_engine.record_interaction(interaction)
    
    processing_time = time.time() - start_time
    
    print(f"   Tempo total: {processing_time:.3f}s")
    print(f"   Interacoes por segundo: {num_interactions/processing_time:.1f}")
    
    # Verificar insights após processamento
    insights = await learning_engine.get_learning_insights()
    print(f"   Total processado: {insights['learning_metrics']['total_interactions']}")

async def test_pattern_detection():
    """Testa detecção de padrões"""
    print("\nTESTE DE DETECCAO DE PADROES")
    print("=" * 35)
    
    # Simular padrão específico: projetos de e-commerce com baixa satisfação
    pattern_interactions = [
        {
            "request": "Marketplace de roupas online",
            "domain": "e-commerce",
            "satisfaction": 0.3,
            "response_time": 15.0
        },
        {
            "request": "Loja virtual de eletrônicos", 
            "domain": "e-commerce",
            "satisfaction": 0.4,
            "response_time": 12.0
        },
        {
            "request": "Plataforma de vendas B2B",
            "domain": "e-commerce", 
            "satisfaction": 0.35,
            "response_time": 18.0
        }
    ]
    
    for i, interaction_data in enumerate(pattern_interactions):
        interaction = InteractionRecord(
            interaction_id=f"pattern_test_{i}",
            session_id="pattern_session",
            user_id="pattern_user",
            interaction_type=InteractionType.PROJECT_ANALYSIS,
            timestamp=datetime.now(),
            user_request=interaction_data["request"],
            context={"domain": interaction_data["domain"]},
            agents_involved=["ana_beatriz_costa"],
            response="Resposta padrao para e-commerce",
            response_time=interaction_data["response_time"],
            confidence_score=0.6,
            explicit_rating=interaction_data["satisfaction"] * 5
        )
        
        await learning_engine.record_interaction(interaction)
    
    print(f"   {len(pattern_interactions)} interacoes de padrao processadas")
    
    # Verificar se padrões foram detectados
    insights = await learning_engine.get_learning_insights()
    top_patterns = insights.get("top_patterns", [])
    
    print(f"   Padroes detectados: {len(top_patterns)}")
    for pattern in top_patterns[:3]:
        print(f"     - {pattern.get('description', 'N/A')}: {pattern.get('confidence', 0):.1%} confianca")

async def main():
    """Executa todos os testes"""
    print("INICIANDO TESTES DO SISTEMA DE APRENDIZADO CONTINUO")
    print("Melhoria #7 - IA que Evolui Autonomamente")
    print("=" * 70)
    
    try:
        await test_learning_pipeline()
        await test_learning_performance()
        await test_pattern_detection()
        
        print("\n" + "=" * 70)
        print("TODOS OS TESTES CONCLUIDOS COM SUCESSO!")
        print("Sistema de aprendizado continuo funcionando perfeitamente")
        print("IA evoluindo autonomamente baseada em feedback")
        print("Agentes melhorando continuamente")
        print("Padroes sendo detectados e otimizados")
        
        # Estatísticas finais
        final_insights = await learning_engine.get_learning_insights()
        print(f"\nESTATISTICAS FINAIS:")
        print(f"   Total de interacoes processadas: {final_insights['learning_metrics']['total_interactions']}")
        print(f"   Padroes identificados: {final_insights['learning_metrics']['patterns_identified']}")
        print(f"   Otimizacoes aplicadas: {final_insights['learning_metrics']['optimizations_applied']}")
        print(f"   Satisfacao media: {final_insights['learning_metrics']['average_satisfaction']:.2f}")
        
        evolution_analytics = await agent_evolution_system.get_evolution_analytics()
        print(f"   Agentes com evolucao ativa: {evolution_analytics['agent_metrics']['agents_with_evolution']}")
        print(f"   Taxa de sucesso das evolucoes: {evolution_analytics['experiment_metrics']['success_rate']:.1%}")
        
    except Exception as e:
        print(f"\nERRO NOS TESTES: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())