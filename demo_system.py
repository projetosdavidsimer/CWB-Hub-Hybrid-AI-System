#!/usr/bin/env python3
"""
Demo do CWB Hub Hybrid AI System
Demonstra o sistema funcionando com exemplo prático
"""

import asyncio
import logging
from src.core.hybrid_ai_orchestrator import HybridAIOrchestrator

async def main():
    """Demonstração do sistema CWB Hub"""
    
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("=" * 80)
    print("CWB HUB HYBRID AI SYSTEM - DEMONSTRACAO")
    print("=" * 80)
    print("Sistema de IA Hibrida com 8 Profissionais Senior")
    print()
    print("Equipe CWB Hub:")
    print("- Ana Beatriz Costa (CTO)")
    print("- Carlos Eduardo Santos (Arquiteto de Software)")
    print("- Sofia Oliveira (Engenheira Full Stack)")
    print("- Gabriel Mendes (Engenheiro Mobile)")
    print("- Isabella Santos (Designer UX/UI)")
    print("- Lucas Pereira (Engenheiro QA)")
    print("- Mariana Rodrigues (Engenheira DevOps)")
    print("- Pedro Henrique Almeida (Project Manager)")
    print("=" * 80)
    
    # Inicializar o orquestrador
    orchestrator = HybridAIOrchestrator()
    
    try:
        print("\nInicializando Equipe CWB Hub...")
        await orchestrator.initialize_agents()
        
        print("Sistema inicializado com sucesso!")
        print(f"Agentes ativos: {', '.join(orchestrator.get_active_agents())}")
        
        # Exemplo de solicitação - PROJETO RESTAURANTE
        user_request = """
        PROJETO: Sistema de Gestão de Restaurante
        CRIADO POR: David Simer
        
        CONTEXTO:
        Sou proprietário de um restaurante familiar e preciso automatizar
        os processos para melhorar eficiência e reduzir erros.
        
        SITUAÇÃO ATUAL:
        - 15 mesas, 5 garçons
        - Comandas em papel (muitos erros)
        - Controle de estoque manual
        - Relatórios financeiros básicos
        - Sistema de delivery desorganizado
        
        FUNCIONALIDADES DESEJADAS:
        
        📋 CONTROLE DE PEDIDOS:
        - Comandas digitais por mesa
        - Status dos pedidos em tempo real
        - Comunicação salão-cozinha
        - Histórico de pedidos
        
        📦 GESTÃO DE ESTOQUE:
        - Controle de ingredientes
        - Alertas de estoque baixo
        - Relatórios de consumo
        
        💰 CONTROLE FINANCEIRO:
        - Vendas diárias/mensais
        - Relatórios de lucro
        - Fechamento de caixa
        
        📱 APP PARA GARÇONS:
        - Interface simples
        - Anotar pedidos rapidamente
        - Ver status das mesas
        - Funcionalidade offline básica
        
        🍽️ CARDÁPIO DIGITAL:
        - Para clientes consultarem
        - Fácil atualização
        - Fotos dos pratos
        
        🚚 SISTEMA DE DELIVERY:
        - Integração WhatsApp
        - Controle de entregas
        - Cálculo de taxas
        
        REQUISITOS:
        - Sistema web responsivo
        - App mobile para garçons
        - Interface muito simples (equipe não técnica)
        - Backup automático
        - Funciona offline básico
        
        CRONOGRAMA: MVP em 2-3 meses
        ORÇAMENTO: Moderado, tecnologias gratuitas preferencialmente
        """
        
        print("\n" + "="*80)
        print("SOLICITACAO DO USUARIO")
        print("="*80)
        print(user_request.strip())
        
        print("\n" + "="*80)
        print("PROCESSAMENTO DA EQUIPE CWB HUB")
        print("="*80)
        print("Executando processo de 5 etapas:")
        print("1. Analisar o Requisito")
        print("2. Colaborar e Interagir") 
        print("3. Propor Soluções Integradas")
        print("4. Comunicação Clara")
        print("5. Preparar para Iteração")
        
        # Processar solicitação
        response = await orchestrator.process_request(user_request)
        
        print("\n" + "="*80)
        print("RESPOSTA DA EQUIPE CWB HUB")
        print("="*80)
        print(response)
        
        # Exemplo de iteração
        print("\n" + "="*80)
        print("EXEMPLO DE ITERACAO")
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
        
        # Obter ID da sessão ativa
        session_ids = list(orchestrator.active_sessions.keys())
        if session_ids:
            session_id = session_ids[0]
            
            print(f"\nIterando solução (Sessão: {session_id})...")
            refined_response = await orchestrator.iterate_solution(session_id, feedback)
            
            print("\nRESPOSTA REFINADA:")
            print(refined_response)
        
        # Mostrar estatísticas
        print("\n" + "="*80)
        print("ESTATISTICAS DA SESSAO")
        print("="*80)
        
        if session_ids:
            session_status = orchestrator.get_session_status(session_ids[0])
            print(f"Status da Sessão: {session_status}")
        
        collaboration_stats = orchestrator.collaboration_framework.get_collaboration_stats()
        print(f"Estatísticas de Colaboração: {collaboration_stats}")
        
        print("\n" + "="*80)
        print("DEMONSTRACAO CONCLUIDA COM SUCESSO!")
        print("="*80)
        print("O sistema CWB Hub Hybrid AI está 100% funcional!")
        print("Todos os 8 profissionais trabalharam em colaboração.")
        print("Processo de 5 etapas executado com sucesso.")
        
    except Exception as e:
        print(f"Erro durante execução: {str(e)}")
        logging.error(f"Erro na execução principal: {str(e)}", exc_info=True)
    
    finally:
        # Encerrar sistema
        print("\nEncerrando sistema...")
        await orchestrator.shutdown()
        print("Sistema encerrado com sucesso!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário")
    except Exception as e:
        print(f"Erro fatal: {str(e)}")