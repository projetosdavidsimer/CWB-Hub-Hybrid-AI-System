#!/usr/bin/env python3
"""
Script Simplificado para Iniciar Projeto com CWB Hub
Criado por: David Simer
"""

import asyncio
import sys
import os

# Adicionar caminho do CWB Hub
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from usar_cwb_hub import RestaurantProjectManager

async def iniciar_projeto_restaurante():
    """Inicia o projeto de gestão de restaurante"""
    
    print("🏢 CWB HUB HYBRID AI SYSTEM")
    print("👨‍💻 Criado por: David Simer")
    print("📋 Projeto: Gestão de Restaurante")
    print("=" * 50)
    
    # Seu plano de negócio aqui
    meu_plano = """
    SISTEMA DE GESTÃO DE RESTAURANTE
    
    OBJETIVO:
    Criar um sistema completo que automatize a gestão do meu restaurante,
    desde o pedido do cliente até o controle financeiro.
    
    FUNCIONALIDADES PRINCIPAIS:
    1. Controle de Pedidos
       - Comandas digitais
       - Status dos pedidos
       - Integração cozinha-salão
    
    2. Gestão de Estoque
       - Controle de ingredientes
       - Alertas de estoque baixo
       - Relatórios de consumo
    
    3. Controle Financeiro
       - Vendas diárias
       - Relatórios de lucro
       - Controle de gastos
    
    4. App para Garçons
       - Anotar pedidos
       - Status das mesas
       - Comunicação com cozinha
    
    5. Cardápio Digital
       - Para clientes
       - Fácil atualização
       - Fotos dos pratos
    
    REQUISITOS:
    - Sistema web responsivo
    - App mobile simples
    - Funciona offline básico
    - Relatórios em PDF
    - Backup automático
    
    CRONOGRAMA:
    - MVP em 2-3 meses
    - Versão completa em 4-5 meses
    
    ORÇAMENTO:
    - Moderado
    - Tecnologias gratuitas preferencialmente
    - Foco na funcionalidade essencial
    """
    
    # Inicializar gerenciador
    manager = RestaurantProjectManager()
    
    try:
        # Inicializar equipe CWB Hub
        await manager.initialize_team()
        
        # Processar plano de negócio
        print("\n🎯 Enviando plano para a equipe CWB Hub...")
        response = await manager.process_business_plan(meu_plano)
        
        # Aguardar input do usuário para feedback
        print("\n" + "="*50)
        print("💬 AGORA É SUA VEZ!")
        print("A equipe CWB Hub analisou seu plano.")
        print("Você pode dar feedback para refinar a solução.")
        print("="*50)
        
        feedback_usuario = input("\n📝 Digite seu feedback (ou Enter para pular): ").strip()
        
        if feedback_usuario:
            await manager.iterate_solution(feedback_usuario)
        
        # Status final
        await manager.get_project_status()
        
        print("\n🎉 PROJETO INICIADO COM SUCESSO!")
        print("A equipe CWB Hub está pronta para desenvolver seu sistema!")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
    
    finally:
        await manager.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(iniciar_projeto_restaurante())
    except KeyboardInterrupt:
        print("\n⚠️ Projeto interrompido")
    except Exception as e:
        print(f"\n💥 Erro: {e}")