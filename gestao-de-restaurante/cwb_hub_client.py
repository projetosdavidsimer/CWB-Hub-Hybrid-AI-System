#!/usr/bin/env python3
"""
Cliente CWB Hub para Projeto de Gestão de Restaurante
Criado por: David Simer

Este arquivo resolve os problemas de importação e demonstra como usar
o CWB Hub Hybrid AI System no seu projeto.
"""

import asyncio
import sys
import os
from pathlib import Path

def setup_cwb_hub_path():
    """Configura o caminho para importar o CWB Hub"""
    # Encontrar o diretório do CWB Hub
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent  # Volta para 'Homem da Casa'
    src_path = project_root / 'src'
    
    if src_path.exists():
        sys.path.insert(0, str(src_path))
        return True
    else:
        print(f"❌ Diretório src não encontrado em: {src_path}")
        return False

# Configurar caminho antes de importar
if setup_cwb_hub_path():
    try:
        # Importar módulos do CWB Hub
        from core.hybrid_ai_orchestrator import HybridAIOrchestrator
        CWB_HUB_AVAILABLE = True
    except ImportError as e:
        print(f"❌ Erro ao importar CWB Hub: {e}")
        CWB_HUB_AVAILABLE = False
else:
    CWB_HUB_AVAILABLE = False

class RestaurantProjectManager:
    """Gerenciador do projeto de restaurante usando CWB Hub"""
    
    def __init__(self):
        if not CWB_HUB_AVAILABLE:
            raise RuntimeError("CWB Hub não está disponível")
        
        self.orchestrator = HybridAIOrchestrator()
        self.project_name = "Sistema de Gestão de Restaurante"
        self.creator = "David Simer"
        
    async def initialize_team(self):
        """Inicializa a equipe CWB Hub"""
        print("🏢 CWB HUB HYBRID AI SYSTEM")
        print(f"👨‍💻 Criado por: {self.creator}")
        print(f"📋 Projeto: {self.project_name}")
        print("=" * 60)
        
        print("🚀 Inicializando Equipe CWB Hub...")
        await self.orchestrator.initialize_agents()
        
        agents = self.orchestrator.get_active_agents()
        print(f"✅ Equipe inicializada com {len(agents)} profissionais:")
        
        for agent_id in agents:
            agent = self.orchestrator.agents[agent_id]
            print(f"   👤 {agent.profile.name} - {agent.profile.role}")
        
        print("=" * 60)
        return True
    
    async def analyze_business_plan(self, business_plan):
        """Analisa o plano de negócio com a equipe CWB Hub"""
        print("\n🎯 ANALISANDO PLANO DE NEGÓCIO")
        print("=" * 60)
        
        # Criar solicitação estruturada para a equipe
        request = f"""
        PROJETO: {self.project_name}
        CRIADO POR: {self.creator}
        
        PLANO DE NEGÓCIO:
        {business_plan}
        
        SOLICITAÇÃO PARA A EQUIPE CWB HUB:
        
        Preciso que vocês analisem este plano de negócio e forneçam:
        
        1. ANÁLISE ESTRATÉGICA (Ana - CTO):
           - Viabilidade técnica e comercial
           - Roadmap de desenvolvimento
           - Análise de riscos e oportunidades
        
        2. ARQUITETURA TÉCNICA (Carlos - Arquiteto):
           - Estrutura do sistema
           - Banco de dados recomendado
           - APIs e integrações necessárias
           - Escalabilidade e performance
        
        3. PLANO DE DESENVOLVIMENTO (Sofia - Full Stack):
           - Tecnologias recomendadas
           - Estrutura do código
           - Cronograma de implementação
           - Estimativas de esforço
        
        4. APP MOBILE (Gabriel - Mobile):
           - Especificações do app para garçons
           - Tecnologia mobile recomendada
           - Funcionalidades offline
           - Integração com sistema principal
        
        5. DESIGN E UX (Isabella - UX/UI):
           - Wireframes conceituais
           - Experiência do usuário
           - Interface intuitiva para equipe não técnica
           - Design responsivo
        
        6. QUALIDADE E TESTES (Lucas - QA):
           - Estratégia de testes
           - Automação de testes
           - Controle de qualidade
           - Testes de usabilidade
        
        7. INFRAESTRUTURA (Mariana - DevOps):
           - Hospedagem e deploy
           - Backup e segurança
           - Monitoramento
           - Escalabilidade
        
        8. GESTÃO DO PROJETO (Pedro - PM):
           - Cronograma detalhado
           - Marcos e entregas
           - Gestão de recursos
           - Comunicação com stakeholders
        
        COLABOREM entre vocês para criar uma solução integrada e coesa!
        """
        
        print("📤 Enviando para análise da equipe...")
        response = await self.orchestrator.process_request(request.strip())
        
        print("\n📥 ANÁLISE COMPLETA DA EQUIPE CWB HUB:")
        print("=" * 60)
        print(response)
        
        return response
    
    async def refine_solution(self, feedback):
        """Refina a solução com base no feedback"""
        print("\n🔄 REFINANDO SOLUÇÃO COM FEEDBACK")
        print("=" * 60)
        print(f"💬 Feedback recebido:")
        print(feedback)
        print()
        
        # Obter sessão ativa
        sessions = list(self.orchestrator.active_sessions.keys())
        if sessions:
            session_id = sessions[0]
            print(f"🔄 Iterando solução (Sessão: {session_id})...")
            
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
        print("\n📊 STATUS DO PROJETO:")
        print("=" * 60)
        
        sessions = list(self.orchestrator.active_sessions.keys())
        if sessions:
            session_id = sessions[0]
            status = self.orchestrator.get_session_status(session_id)
            stats = self.orchestrator.collaboration_framework.get_collaboration_stats()
            
            print(f"📋 Sessão Ativa: {session_id}")
            print(f"📈 Status: {status}")
            print(f"🤝 Colaborações: {stats}")
        else:
            print("ℹ️ Nenhuma sessão ativa")
    
    async def shutdown(self):
        """Encerra o sistema"""
        print("\n🔚 Encerrando sistema CWB Hub...")
        await self.orchestrator.shutdown()
        print("✅ Sistema encerrado com sucesso!")

async def exemplo_uso_completo():
    """Exemplo completo de como usar o CWB Hub no projeto"""
    
    # Verificar se CWB Hub está disponível
    if not CWB_HUB_AVAILABLE:
        print("❌ CWB Hub não está disponível")
        print("Certifique-se de que você está na pasta correta e o CWB Hub está instalado")
        return
    
    # Plano de negócio do restaurante
    plano_negocio = """
    SISTEMA DE GESTÃO DE RESTAURANTE
    Criado por: David Simer
    
    CONTEXTO:
    Sou dono de um restaurante familiar e preciso automatizar os processos
    para melhorar a eficiência e reduzir erros.
    
    SITUAÇÃO ATUAL:
    - 15 mesas, 5 garçons
    - Comandas em papel (muitos erros)
    - Controle de estoque manual
    - Relatórios financeiros básicos
    - Sem sistema de delivery organizado
    
    OBJETIVOS:
    1. Automatizar controle de pedidos
    2. Melhorar comunicação salão-cozinha
    3. Controlar estoque automaticamente
    4. Gerar relatórios financeiros
    5. Ter app simples para garçons
    6. Organizar sistema de delivery
    
    FUNCIONALIDADES DESEJADAS:
    
    📋 CONTROLE DE PEDIDOS:
    - Comandas digitais por mesa
    - Status dos pedidos em tempo real
    - Histórico de pedidos por cliente
    - Integração com sistema de pagamento
    
    📦 GESTÃO DE ESTOQUE:
    - Cadastro de ingredientes
    - Controle de entrada/saída
    - Alertas de estoque baixo
    - Relatórios de consumo
    
    💰 CONTROLE FINANCEIRO:
    - Vendas diárias/mensais
    - Relatórios de lucro
    - Controle de despesas
    - Análise de performance
    
    📱 APP PARA GARÇONS:
    - Interface simples e intuitiva
    - Anotar pedidos rapidamente
    - Ver status das mesas
    - Comunicar com cozinha
    
    🍽️ CARDÁPIO DIGITAL:
    - Para clientes consultarem
    - Fácil atualização
    - Fotos dos pratos
    - Preços atualizados
    
    🚚 SISTEMA DE DELIVERY:
    - Integração WhatsApp
    - Controle de entregas
    - Cálculo de taxas
    - Rastreamento
    
    REQUISITOS TÉCNICOS:
    - Sistema web (funciona em tablet/celular)
    - App mobile para garçons
    - Banco de dados confiável
    - Backup automático
    - Interface muito simples (equipe não é técnica)
    - Funciona offline básico
    
    CRONOGRAMA:
    - MVP: 2-3 meses
    - Versão completa: 4-5 meses
    - Testes e ajustes: 1 mês
    
    ORÇAMENTO:
    - Moderado
    - Preferência por tecnologias gratuitas
    - Foco no essencial primeiro
    - Expansão gradual
    """
    
    # Inicializar gerenciador
    manager = RestaurantProjectManager()
    
    try:
        # 1. Inicializar equipe
        await manager.initialize_team()
        
        # 2. Analisar plano de negócio
        response = await manager.analyze_business_plan(plano_negocio)
        
        # 3. Simular feedback do usuário
        feedback = """
        Excelente análise! Algumas considerações importantes:
        
        PRIORIDADES:
        1. Controle de pedidos é URGENTE - maior problema atual
        2. App para garçons é essencial
        3. Relatórios básicos de vendas
        
        ORÇAMENTO:
        - Limitado, vamos começar com MVP
        - Tecnologias simples e baratas
        - Foco no que resolve problemas imediatos
        
        EQUIPE:
        - Não é técnica, interface precisa ser MUITO simples
        - Treinamento mínimo
        - Resistência a mudanças
        
        CRONOGRAMA:
        - 2 meses para MVP está bom
        - Preciso testar com equipe real
        - Implementação gradual
        
        ESPECÍFICO:
        - WhatsApp delivery é prioridade
        - Backup automático é essencial
        - Funcionar em tablets baratos
        
        Podem ajustar a proposta focando nessas prioridades?
        """
        
        # 4. Refinar solução
        await manager.refine_solution(feedback)
        
        # 5. Status do projeto
        await manager.get_project_status()
        
        print("\n🎉 EXEMPLO CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print("✅ Plano de negócio analisado pela equipe completa")
        print("✅ Solução técnica fornecida")
        print("✅ Refinamento baseado em feedback")
        print("✅ Projeto pronto para desenvolvimento!")
        
    except Exception as e:
        print(f"❌ Erro durante execução: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # 6. Encerrar sistema
        await manager.shutdown()

def main():
    """Função principal"""
    print("🎯 CWB HUB CLIENT - GESTÃO DE RESTAURANTE")
    print("👨‍💻 Criado por: David Simer")
    print()
    print("📋 Este script demonstra como usar o CWB Hub no seu projeto")
    print("🔧 Resolve problemas de importação e fornece exemplo prático")
    print()
    
    if not CWB_HUB_AVAILABLE:
        print("❌ CWB Hub não disponível")
        print("Verifique se você está na pasta correta")
        return
    
    try:
        asyncio.run(exemplo_uso_completo())
    except KeyboardInterrupt:
        print("\n⚠️ Execução interrompida pelo usuário")
    except Exception as e:
        print(f"\n💥 Erro fatal: {e}")

if __name__ == "__main__":
    main()