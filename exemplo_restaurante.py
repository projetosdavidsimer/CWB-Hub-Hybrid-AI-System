#!/usr/bin/env python3
"""
Exemplo Específico: CWB Hub para Projeto de Gestão de Restaurante
Criado por: David Simer
"""

import asyncio
import sys
import os

# Adicionar src ao path
sys.path.insert(0, 'src')

from core.hybrid_ai_orchestrator import HybridAIOrchestrator

async def projeto_gestao_restaurante():
    """Demonstra o uso do CWB Hub para projeto de gestão de restaurante"""
    
    print("🏢 CWB HUB HYBRID AI SYSTEM")
    print("👨‍💻 Criado por: David Simer")
    print("🍽️ Projeto: Sistema de Gestão de Restaurante")
    print("=" * 70)
    
    # Plano de negócio específico para restaurante
    plano_restaurante = """
    PROJETO: Sistema de Gestão de Restaurante
    CRIADO POR: David Simer
    
    CONTEXTO DO NEGÓCIO:
    Sou proprietário de um restaurante familiar e preciso automatizar
    os processos para melhorar eficiência e reduzir erros operacionais.
    
    SITUAÇÃO ATUAL:
    - Restaurante com 15 mesas e 5 garçons
    - Comandas em papel (muitos erros e perda de tempo)
    - Controle de estoque manual e desorganizado
    - Relatórios financeiros básicos em planilhas
    - Sistema de delivery desorganizado
    - Comunicação salão-cozinha ineficiente
    
    OBJETIVOS PRINCIPAIS:
    1. Automatizar controle de pedidos e comandas
    2. Melhorar comunicação entre salão e cozinha
    3. Implementar controle automático de estoque
    4. Gerar relatórios financeiros precisos
    5. Criar app simples para garçons usarem
    6. Organizar sistema de delivery
    7. Reduzir erros e aumentar eficiência
    
    FUNCIONALIDADES ESSENCIAIS:
    
    📋 CONTROLE DE PEDIDOS:
    - Comandas digitais por mesa
    - Status dos pedidos em tempo real
    - Histórico de pedidos por cliente
    - Integração com cozinha
    - Controle de pagamentos
    
    📦 GESTÃO DE ESTOQUE:
    - Cadastro de ingredientes e produtos
    - Controle automático de entrada/saída
    - Alertas de estoque baixo
    - Relatórios de consumo por período
    - Integração com fornecedores
    
    💰 CONTROLE FINANCEIRO:
    - Vendas diárias, semanais e mensais
    - Relatórios de lucro e margem
    - Controle de despesas operacionais
    - Análise de performance por garçom
    - Fechamento de caixa automático
    
    📱 APP PARA GARÇONS:
    - Interface simples e intuitiva
    - Anotar pedidos rapidamente
    - Ver status de todas as mesas
    - Comunicação direta com cozinha
    - Funcionalidade offline básica
    
    🍽️ CARDÁPIO DIGITAL:
    - Para clientes consultarem nas mesas
    - Fácil atualização de pratos e preços
    - Fotos atrativas dos pratos
    - Categorização por tipo de comida
    - Indicação de disponibilidade
    
    🚚 SISTEMA DE DELIVERY:
    - Integração com WhatsApp Business
    - Controle de entregas e entregadores
    - Cálculo automático de taxa de entrega
    - Rastreamento de pedidos
    - Tempo estimado de entrega
    
    REQUISITOS TÉCNICOS:
    - Sistema web responsivo (funciona em tablets e celulares)
    - App mobile nativo para garçons (iOS prioritário)
    - Banco de dados confiável e rápido
    - Backup automático diário
    - Interface muito simples (equipe não é técnica)
    - Funciona offline em situações básicas
    - Relatórios exportáveis em PDF
    - Integração com máquinas de cartão
    
    CRONOGRAMA DESEJADO:
    - MVP (funcionalidades básicas): 2-3 meses
    - Versão completa: 4-5 meses
    - Testes com equipe real: 1 mês
    - Implementação gradual: 2 semanas
    
    ORÇAMENTO:
    - Orçamento moderado (não é grande empresa)
    - Preferência por tecnologias gratuitas/open-source
    - Foco nas funcionalidades que resolvem problemas imediatos
    - Possibilidade de expans��o futura conforme crescimento
    
    CONTEXTO DA EQUIPE:
    - Equipe não é técnica (garçons, cozinheiros)
    - Resistência inicial a mudanças
    - Precisa de treinamento simples
    - Interface deve ser muito intuitiva
    - Suporte técnico será necessário
    
    PRIORIDADES:
    1. Controle de pedidos (resolve maior problema atual)
    2. App para garçons (essencial para operação)
    3. Comunicação salão-cozinha
    4. Relatórios básicos de vendas
    5. Controle de estoque
    6. Sistema de delivery
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
        
        print("\n" + "="*70)
        print("📤 ENVIANDO PLANO DE NEGÓCIO PARA ANÁLISE...")
        print("="*70)
        
        # Processar plano de negócio
        response = await orchestrator.process_request(plano_restaurante)
        
        print("\n📥 ANÁLISE COMPLETA DA EQUIPE CWB HUB:")
        print("="*70)
        print(response)
        
        # Feedback específico do dono do restaurante
        print("\n" + "="*70)
        print("💬 FEEDBACK DO PROPRIETÁRIO DO RESTAURANTE:")
        print("="*70)
        
        feedback_proprietario = """
        Excelente análise da equipe! Como proprietário do restaurante, 
        tenho algumas considerações práticas importantes:
        
        PRIORIDADES URGENTES:
        1. Controle de pedidos é CRÍTICO - perdemos muito dinheiro com erros
        2. App para garçons deve ser MUITO simples - eles não são técnicos
        3. Comunicação cozinha-salão precisa ser instantânea
        
        ORÇAMENTO E CRONOGRAMA:
        - Orçamento é limitado, vamos começar com MVP
        - 2-3 meses para MVP está perfeito
        - Preciso ver resultados rápidos para justificar investimento
        
        EQUIPE E USABILIDADE:
        - Meus garçons têm dificuldade com tecnologia
        - Interface precisa ser EXTREMAMENTE intuitiva
        - Treinamento deve ser mínimo (máximo 1 hora)
        - Resistência a mudanças é alta
        
        OPERAÇÃO:
        - Restaurante não pode parar durante implementação
        - Implementação deve ser gradual
        - Backup dos dados é ESSENCIAL
        - Suporte técnico será necessário
        
        ESPECÍFICO:
        - WhatsApp delivery é prioridade (70% dos deliveries vêm por lá)
        - Relatórios simples mas eficazes
        - Funcionar em tablets baratos
        - Integração com máquina de cartão Stone
        
        PERGUNTA: Vocês podem ajustar a proposta focando nessas 
        prioridades e considerando as limitações práticas?
        """
        
        print(feedback_proprietario)
        
        # Obter sessão ativa para iteração
        sessions = list(orchestrator.active_sessions.keys())
        if sessions:
            session_id = sessions[0]
            
            print("\n🔄 REFINANDO SOLUÇÃO COM BASE NO FEEDBACK...")
            refined_response = await orchestrator.iterate_solution(session_id, feedback_proprietario)
            
            print("\n📥 PROPOSTA REFINADA PARA O RESTAURANTE:")
            print("="*70)
            print(refined_response)
            
            # Mostrar estatísticas
            print("\n📊 ESTATÍSTICAS DA CONSULTORIA:")
            print("="*70)
            status = orchestrator.get_session_status(session_id)
            stats = orchestrator.collaboration_framework.get_collaboration_stats()
            print(f"📋 Status da Sessão: {status}")
            print(f"🤝 Colaborações Realizadas: {stats}")
        
        print("\n🎉 CONSULTORIA CONCLUÍDA!")
        print("="*70)
        print("✅ Plano de negócio analisado por 8 profissionais sênior")
        print("✅ Solução técnica completa fornecida")
        print("✅ Proposta refinada para necessidades específicas")
        print("✅ Cronograma e orçamento ajustados")
        print("✅ Considerações práticas incorporadas")
        print("✅ Projeto pronto para desenvolvimento!")
        print()
        print("🎯 PRÓXIMOS PASSOS:")
        print("   1. Aprovação final do plano")
        print("   2. Contratação da equipe de desenvolvimento")
        print("   3. Início do desenvolvimento do MVP")
        print("   4. Testes com equipe do restaurante")
        print("   5. Implementação gradual")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🔚 Encerrando sistema CWB Hub...")
        await orchestrator.shutdown()
        print("✅ Consultoria encerrada com sucesso!")

def main():
    """Função principal"""
    print("🎯 EXEMPLO PRÁTICO: CWB Hub para Gestão de Restaurante")
    print("📋 Demonstra como usar o sistema para um projeto real")
    print("👨‍💻 Criado por: David Simer")
    print()
    
    try:
        asyncio.run(projeto_gestao_restaurante())
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")

if __name__ == "__main__":
    main()