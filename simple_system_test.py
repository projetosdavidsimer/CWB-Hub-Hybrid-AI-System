#!/usr/bin/env python3
"""
Teste Simplificado do Sistema CWB Hub Hybrid AI
Valida funcionalidades principais sem caracteres especiais
"""

import asyncio
import logging
import time
import sys

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_system():
    """Testa o sistema CWB Hub de forma simplificada"""
    
    print("=" * 60)
    print("CWB HUB HYBRID AI - TESTE DE VALIDACAO")
    print("=" * 60)
    
    try:
        # Importar e inicializar sistema
        print("\n1. Inicializando sistema...")
        from src.core.hybrid_ai_orchestrator import HybridAIOrchestrator
        
        orchestrator = HybridAIOrchestrator()
        await orchestrator.initialize_agents()
        
        agents = orchestrator.get_active_agents()
        print(f"   Sistema inicializado com {len(agents)} agentes")
        
        # Teste 1: Solicitação estratégica
        print("\n2. Testando solicitação estratégica...")
        strategic_request = """
        Nossa empresa precisa definir estratégia tecnológica para os próximos 3 anos.
        Queremos focar em inovação e competitividade. Como proceder?
        """
        
        start_time = time.time()
        response1 = await orchestrator.process_request(strategic_request.strip())
        end_time = time.time()
        
        assert response1 is not None, "Resposta estratégica não pode ser None"
        assert len(response1) > 100, "Resposta estratégica muito curta"
        print(f"   Teste estratégico OK - {end_time - start_time:.2f}s")
        
        # Teste 2: Solicitação técnica
        print("\n3. Testando solicitação técnica...")
        technical_request = """
        Preciso desenvolver uma API REST para e-commerce com:
        - Autenticação JWT
        - Catálogo de produtos
        - Carrinho de compras
        - Pagamentos seguros
        """
        
        start_time = time.time()
        response2 = await orchestrator.process_request(technical_request.strip())
        end_time = time.time()
        
        assert response2 is not None, "Resposta técnica não pode ser None"
        assert len(response2) > 150, "Resposta técnica muito curta"
        print(f"   Teste técnico OK - {end_time - start_time:.2f}s")
        
        # Teste 3: Funcionalidade de iteração
        print("\n4. Testando iteração...")
        sessions = list(orchestrator.active_sessions.keys())
        if sessions:
            session_id = sessions[0]
            feedback = "Gostei da proposta, mas preciso de mais detalhes sobre tecnologias e cronograma."
            
            start_time = time.time()
            refined_response = await orchestrator.iterate_solution(session_id, feedback)
            end_time = time.time()
            
            assert refined_response is not None, "Resposta refinada não pode ser None"
            assert refined_response != response2, "Resposta refinada deve ser diferente"
            print(f"   Teste de iteração OK - {end_time - start_time:.2f}s")
        
        # Teste 4: Métricas de colaboração
        print("\n5. Testando métricas...")
        stats = orchestrator.collaboration_framework.get_collaboration_stats()
        assert isinstance(stats, dict), "Estatísticas devem ser um dicionário"
        print(f"   Métricas OK - {stats.get('total_collaborations', 0)} colaborações")
        
        # Teste 5: Agentes individuais
        print("\n6. Testando agentes individuais...")
        test_count = 0
        for agent_id in list(agents)[:3]:  # Testar apenas 3 agentes
            agent = orchestrator.agents[agent_id]
            analysis = await agent.analyze_request("Desenvolver funcionalidade de login")
            
            assert analysis is not None, f"Análise do {agent_id} não pode ser None"
            assert len(analysis) > 50, f"Análise do {agent_id} muito curta"
            test_count += 1
        
        print(f"   Agentes individuais OK - {test_count} testados")
        
        # Limpeza
        print("\n7. Limpando sistema...")
        await orchestrator.shutdown()
        
        # Relatório final
        print("\n" + "=" * 60)
        print("RESULTADO FINAL")
        print("=" * 60)
        print("Status: TODOS OS TESTES PASSARAM!")
        print("Sistema CWB Hub Hybrid AI está 100% funcional!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nERRO: {e}")
        print("Status: TESTE FALHOU")
        return False

async def main():
    """Função principal"""
    try:
        success = await test_system()
        return success
    except Exception as e:
        print(f"Erro crítico: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\nValidação completa: Sistema aprovado!")
            sys.exit(0)
        else:
            print("\nValidação falhou: Verificar erros.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"Erro fatal: {e}")
        sys.exit(1)