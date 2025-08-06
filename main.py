"""
CWB Hub Hybrid AI - Exemplo de Uso
Demonstra como usar o sistema de IA híbrida da equipe CWB Hub
"""

import asyncio
import logging
from src.core.hybrid_ai_orchestrator import HybridAIOrchestrator


async def main():
    """Exemplo de uso do sistema CWB Hub Hybrid AI"""
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Inicializar o orquestrador
    orchestrator = HybridAIOrchestrator()
    
    try:
        print("🚀 Inicializando Equipe CWB Hub...")
        await orchestrator.initialize_agents()
        
        print("\n✅ Equipe inicializada com sucesso!")
        print(f"👥 Agentes ativos: {', '.join(orchestrator.get_active_agents())}")
        
        # Exemplo de solicitação
        user_request = """
        Preciso desenvolver um aplicativo mobile para gestão de projetos que permita:
        - Colaboração em tempo real entre equipes
        - Sincronização offline
        - Dashboard com métricas de performance
        - Integração com ferramentas existentes
        - Interface intuitiva e acessível
        
        O aplicativo deve ser escalável para suportar milhares de usuários e 
        garantir alta disponibilidade e segurança dos dados.
        """
        
        print("\n" + "="*80)
        print("📋 SOLICITAÇÃO DO USUÁRIO")
        print("="*80)
        print(user_request.strip())
        
        print("\n" + "="*80)
        print("🧠 PROCESSAMENTO DA EQUIPE CWB HUB")
        print("="*80)
        
        # Processar solicitação
        response = await orchestrator.process_request(user_request)
        
        print("\n" + "="*80)
        print("💡 RESPOSTA DA EQUIPE CWB HUB")
        print("="*80)
        print(response)
        
        # Exemplo de iteração
        print("\n" + "="*80)
        print("🔄 EXEMPLO DE ITERAÇÃO")
        print("="*80)
        
        feedback = """
        Gostei da proposta! Mas tenho algumas considerações:
        - O orçamento é limitado, precisamos priorizar funcionalidades
        - O prazo é de 3 meses para o MVP
        - Precisamos focar primeiro em iOS, Android vem depois
        - A integração com Slack é prioritária
        """
        
        print("Feedback do usuário:")
        print(feedback.strip())
        
        # Obter ID da sessão ativa (simplificado para exemplo)
        session_ids = list(orchestrator.active_sessions.keys())
        if session_ids:
            session_id = session_ids[0]
            
            print(f"\n🔄 Iterando solução (Sessão: {session_id})...")
            refined_response = await orchestrator.iterate_solution(session_id, feedback)
            
            print("\n💡 RESPOSTA REFINADA:")
            print(refined_response)
        
        # Mostrar estatísticas
        print("\n" + "="*80)
        print("📊 ESTATÍSTICAS DA SESSÃO")
        print("="*80)
        
        if session_ids:
            session_status = orchestrator.get_session_status(session_ids[0])
            print(f"Status da Sessão: {session_status}")
        
        collaboration_stats = orchestrator.collaboration_framework.get_collaboration_stats()
        print(f"Estatísticas de Colaboração: {collaboration_stats}")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {str(e)}")
        logging.error(f"Erro na execução principal: {str(e)}", exc_info=True)
    
    finally:
        # Encerrar sistema
        print("\n🔚 Encerrando sistema...")
        await orchestrator.shutdown()
        print("✅ Sistema encerrado com sucesso!")


def run_example():
    """Executa o exemplo de forma síncrona"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro fatal: {str(e)}")


if __name__ == "__main__":
    # Set UTF-8 encoding for console output
    import sys
    import io
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    print("""
    ================================================================
    |                    CWB HUB HYBRID AI                         |
    |                                                              |
    |  Sistema de IA Hibrida com 8 Profissionais Senior          |
    |                                                              |
    |  Ana Beatriz Costa - CTO                                     |
    |  Carlos Eduardo Santos - Arquiteto de Software              |
    |  Sofia Oliveira - Engenheira Full Stack                     |
    |  Gabriel Mendes - Engenheiro Mobile                          |
    |  Isabella Santos - Designer UX/UI                           |
    |  Lucas Pereira - Engenheiro de QA                            |
    |  Mariana Rodrigues - Engenheira DevOps                      |
    |  Pedro Henrique Almeida - Agile Project Manager             |
    |                                                              |
    ================================================================
    """)
    
    run_example()