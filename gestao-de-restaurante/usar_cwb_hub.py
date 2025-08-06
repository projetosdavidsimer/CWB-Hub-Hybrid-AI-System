#!/usr/bin/env python3
"""
Script para usar o CWB Hub Hybrid AI System no projeto de Gestão de Restaurante
Criado por: David Simer
"""

import sys
import os
import asyncio

# Adicionar o caminho do CWB Hub ao Python path
cwb_hub_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, cwb_hub_path)

from core.hybrid_ai_orchestrator import HybridAIOrchestrator

class RestaurantProjectManager:
    """Gerenciador do projeto usando CWB Hub"""
    
    def __init__(self):
        self.orchestrator = HybridAIOrchestrator()
        self.project_name = "Sistema de Gestão de Restaurante"
        
    async def initialize_team(self):
        """Inicializa a equipe CWB Hub"""
        print("🚀 Inicializando Equipe CWB Hub para o projeto...")
        print(f"📋 Projeto: {self.project_name}")
        print("=" * 60)
        
        await self.orchestrator.initialize_agents()
        
        agents = self.orchestrator.get_active_agents()
        print(f"✅ Equipe inicializada com {len(agents)} profissionais:")
        
        for agent_id in agents:
            agent = self.orchestrator.agents[agent_id]
            print(f"   👤 {agent.profile.name} - {agent.profile.role}")
        
        print("=" * 60)
        return True
    
    async def process_business_plan(self, business_plan):
        """Processa o plano de negócio com a equipe"""
        print("\n🎯 PROCESSANDO PLANO DE NEGÓCIO")
        print("=" * 60)
        
        # Criar solicitação estruturada
        request = f"""
        PROJETO: {self.project_name}
        
        PLANO DE NEGÓCIO:
        {business_plan}
        
        SOLICITAÇÃO PARA A EQUIPE CWB HUB:
        Com base neste plano de negócio, preciso que vocês:
        
        1. ANALISEM o projeto sob suas perspectivas profissionais
        2. COLABOREM para identificar requisitos técnicos e funcionais
        3. PROPONHAM uma solução completa de desenvolvimento
        4. COMUNIQUEM um plano de implementação detalhado
        5. PREPAREM para iterações baseadas em feedback
        
        Quero uma análise completa que cubra:
        - Arquitetura do sistema
        - Tecnologias recomendadas
        - Design da interface
        - Funcionalidades principais
        - Plano de desenvolvimento
        - Estratégia de testes
        - Infraestrutura e deploy
        - Cronograma e gestão
        """
        
        print("📤 Enviando para a equipe CWB Hub...")
        response = await self.orchestrator.process_request(request.strip())
        
        print("\n📥 RESPOSTA DA EQUIPE CWB HUB:")
        print("=" * 60)
        print(response)
        
        return response
    
    async def iterate_solution(self, feedback):
        """Itera a solução com feedback"""
        print("\n🔄 ITERANDO SOLUÇÃO COM FEEDBACK")
        print("=" * 60)
        print(f"Feedback: {feedback}")
        
        # Obter sessão ativa
        sessions = list(self.orchestrator.active_sessions.keys())
        if sessions:
            session_id = sessions[0]
            refined_response = await self.orchestrator.iterate_solution(session_id, feedback)
            
            print("\n📥 SOLUÇÃO REFINADA:")
            print("=" * 60)
            print(refined_response)
            
            return refined_response
        else:
            print("❌ Nenhuma sessão ativa encontrada")
            return None
    
    async def get_project_status(self):
        """Obtém status do projeto"""
        sessions = list(self.orchestrator.active_sessions.keys())
        if sessions:
            status = self.orchestrator.get_session_status(sessions[0])
            stats = self.orchestrator.collaboration_framework.get_collaboration_stats()
            
            print("\n📊 STATUS DO PROJETO:")
            print("=" * 60)
            print(f"Status da Sessão: {status}")
            print(f"Estatísticas: {stats}")
        
    async def shutdown(self):
        """Encerra o sistema"""
        print("\n🔚 Encerrando sistema CWB Hub...")
        await self.orchestrator.shutdown()
        print("✅ Sistema encerrado com sucesso!")

async def main():
    """Função principal - exemplo de uso"""
    
    # Exemplo de plano de negócio
    business_plan = """
    PLANO DE NEGÓCIO - SISTEMA DE GESTÃO DE RESTAURANTE
    
    VISÃO GERAL:
    Desenvolver um sistema completo para gestão de restaurantes que permita:
    - Controle de pedidos e comandas
    - Gestão de estoque e ingredientes
    - Controle financeiro e relatórios
    - Gestão de funcionários e turnos
    - Interface para clientes (cardápio digital)
    - Sistema de delivery integrado
    
    PÚBLICO-ALVO:
    - Restaurantes pequenos e médios
    - Lanchonetes e fast-foods
    - Bares e cafeterias
    
    OBJETIVOS:
    - Automatizar processos manuais
    - Reduzir erros em pedidos
    - Melhorar controle de estoque
    - Aumentar efici��ncia operacional
    - Fornecer insights através de relatórios
    
    REQUISITOS TÉCNICOS INICIAIS:
    - Sistema web responsivo
    - App mobile para garçons
    - Integração com sistemas de pagamento
    - Relatórios em tempo real
    - Backup automático de dados
    - Suporte a múltiplos restaurantes
    
    CRONOGRAMA DESEJADO:
    - MVP em 3 meses
    - Versão completa em 6 meses
    
    ORÇAMENTO:
    - Orçamento moderado
    - Foco em tecnologias open-source
    - Priorizar funcionalidades essenciais
    """
    
    # Inicializar gerenciador do projeto
    manager = RestaurantProjectManager()
    
    try:
        # 1. Inicializar equipe
        await manager.initialize_team()
        
        # 2. Processar plano de negócio
        response = await manager.process_business_plan(business_plan)
        
        # 3. Exemplo de iteração com feedback
        feedback = """
        Gostei muito da proposta! Algumas considerações:
        - Preciso priorizar o controle de pedidos primeiro
        - O app mobile é essencial para os garçons
        - Integração com WhatsApp para delivery seria ótimo
        - Relatórios simples mas eficazes
        - Foco em usabilidade - equipe não é muito técnica
        """
        
        await manager.iterate_solution(feedback)
        
        # 4. Status do projeto
        await manager.get_project_status()
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        # 5. Encerrar sistema
        await manager.shutdown()

if __name__ == "__main__":
    print("🏢 CWB HUB HYBRID AI SYSTEM")
    print("📋 Projeto: Sistema de Gestão de Restaurante")
    print("👨‍💻 Criado por: David Simer")
    print("=" * 60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")