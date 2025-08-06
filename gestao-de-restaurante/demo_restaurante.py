#!/usr/bin/env python3
"""
DEMONSTRAÇÃO: Como usar CWB Hub para projeto de Gestão de Restaurante
Criado por: David Simer
"""

import asyncio
import sys
import os

# Configurar caminho para importar CWB Hub
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

# Importar componentes do CWB Hub
try:
    from core.hybrid_ai_orchestrator import HybridAIOrchestrator
except ImportError as e:
    print(f"❌ Erro ao importar CWB Hub: {e}")
    print("Certifique-se de que o CWB Hub está na pasta pai")
    sys.exit(1)

async def demonstrar_uso_cwb_hub():
    """Demonstra como usar o CWB Hub para o projeto de restaurante"""
    
    print("🏢 CWB HUB HYBRID AI SYSTEM")
    print("👨‍💻 Criado por: David Simer")
    print("📋 Projeto: Sistema de Gestão de Restaurante")
    print("=" * 60)
    
    # Plano de negócio do restaurante
    plano_negocio = """
    PROJETO: Sistema de Gestão de Restaurante
    CRIADO POR: David Simer
    
    VISÃO GERAL:
    Desenvolver um sistema completo para automatizar a gestão do meu restaurante,
    desde o atendimento ao cliente até o controle financeiro.
    
    FUNCIONALIDADES DESEJADAS:
    
    1. CONTROLE DE PEDIDOS
       - Sistema de comandas digitais
       - Acompanhamento de status dos pedidos
       - Comunicação entre salão e cozinha
       - Histórico de pedidos por cliente
    
    2. GESTÃO DE ESTOQUE
       - Controle de ingredientes e produtos
       - Alertas de estoque baixo
       - Relatórios de consumo
       - Integração com fornecedores
    
    3. CONTROLE FINANCEIRO
       - Registro de vendas diárias
       - Relatórios de lucro e despesas
       - Controle de fluxo de caixa
       - Análise de performance por período
    
    4. APP MOBILE PARA GARÇONS
       - Interface simples para anotar pedidos
       - Visualização do status das mesas
       - Comunicação direta com a cozinha
       - Funcionalidade offline básica
    
    5. CARDÁPIO DIGITAL
       - Interface para clientes
       - Fácil atualização de pratos e preços
       - Fotos dos pratos
       - Categorização por tipo de comida
    
    6. SISTEMA DE DELIVERY
       - Integração com WhatsApp
       - Controle de entregas
       - Cálculo de taxa de entrega
       - Rastreamento de pedidos
    
    REQUISITOS TÉCNICOS:
    - Sistema web responsivo (funciona em tablet/celular)
    - App mobile simples para garçons
    - Banco de dados confiável
    - Backup automático
    - Relatórios em PDF
    - Interface intuitiva (equipe não é técnica)
    
    CRONOGRAMA:
    - MVP (funcionalidades básicas): 2-3 meses
    - Versão completa: 4-5 meses
    - Testes e ajustes: 1 mês
    
    ORÇAMENTO:
    - Orçamento moderado
    - Preferência por tecnologias gratuitas/open-source
    - Foco nas funcionalidades essenciais primeiro
    - Possibilidade de expansão futura
    
    CONTEXTO DO NEGÓCIO:
    - Restaurante familiar de médio porte
    - 15 mesas, 5 garçons
    - Cardápio variado (pratos executivos, à la carte)
    - Delivery próprio
    - Clientela fiel e crescente movimento
    """
    
    # Inicializar CWB Hub
    orchestrator = HybridAIOrchestrator()
    
    try:
        print("\n🚀 INICIALIZANDO EQUIPE CWB HUB...")
        await orchestrator.initialize_agents()
        
        agents = orchestrator.get_active_agents()
        print(f"✅ Equipe inicializada com {len(agents)} profissionais:")
        
        for agent_id in agents:
            agent = orchestrator.agents[agent_id]
            print(f"   👤 {agent.profile.name} - {agent.profile.role}")
        
        print("\n" + "="*60)
        print("📤 ENVIANDO PLANO DE NEGÓCIO PARA A EQUIPE...")
        print("="*60)
        
        # Processar plano de negócio
        response = await orchestrator.process_request(plano_negocio)
        
        print("\n📥 RESPOSTA DA EQUIPE CWB HUB:")
        print("="*60)
        print(response)
        
        # Simular feedback do usuário
        print("\n" + "="*60)
        print("💬 SIMULANDO FEEDBACK DO USUÁRIO...")
        print("="*60)
        
        feedback = """
        Excelente análise da equipe! Tenho algumas considerações:
        
        1. PRIORIDADES: Preciso focar primeiro no controle de pedidos e no app para garçons.
           Isso vai resolver meu maior problema atual.
        
        2. ORÇAMENTO: É limitado, então vamos começar com o MVP e expandir depois.
        
        3. TECNOLOGIA: Gostei da sugestão de tecnologias web. Precisa ser simples de manter.
        
        4. CRONOGRAMA: 2-3 meses para o MVP está perfeito. Posso testar com a equipe.
        
        5. INTEGRAÇÃO: A integração com WhatsApp para delivery é essencial.
        
        6. USABILIDADE: A equipe não é técnica, então a interface precisa ser muito intuitiva.
        
        Podem refinar a proposta focando nessas prioridades?
        """
        
        print(f"Feedback: {feedback}")
        
        # Obter sessão ativa para iteração
        sessions = list(orchestrator.active_sessions.keys())
        if sessions:
            session_id = sessions[0]
            
            print("\n🔄 REFINANDO SOLUÇÃO COM BASE NO FEEDBACK...")
            refined_response = await orchestrator.iterate_solution(session_id, feedback)
            
            print("\n📥 SOLUÇÃO REFINADA:")
            print("="*60)
            print(refined_response)
            
            # Mostrar estatísticas
            print("\n📊 ESTATÍSTICAS DA SESSÃO:")
            print("="*60)
            status = orchestrator.get_session_status(session_id)
            stats = orchestrator.collaboration_framework.get_collaboration_stats()
            print(f"Status: {status}")
            print(f"Colaborações: {stats}")
        
        print("\n🎉 DEMONSTRAÇÃO CONCLUÍDA!")
        print("="*60)
        print("✅ A equipe CWB Hub analisou seu plano de negócio")
        print("✅ Forneceu uma solução técnica completa")
        print("✅ Refinou a proposta com base no seu feedback")
        print("✅ Está pronta para começar o desenvolvimento!")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🔚 Encerrando sistema...")
        await orchestrator.shutdown()
        print("✅ Sistema encerrado com sucesso!")

def main():
    """Função principal"""
    print("🎯 DEMONSTRAÇÃO: Como usar CWB Hub no seu projeto")
    print("📋 Cenário: Você está na pasta 'gestao-de-restaurante' no VSCode")
    print("💡 Você tem um plano de negócio e quer que a equipe CWB Hub analise")
    print()
    
    try:
        asyncio.run(demonstrar_uso_cwb_hub())
    except KeyboardInterrupt:
        print("\n⚠️ Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")

if __name__ == "__main__":
    main()