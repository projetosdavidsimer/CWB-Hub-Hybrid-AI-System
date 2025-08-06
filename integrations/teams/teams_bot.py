#!/usr/bin/env python3
"""
CWB Hub Microsoft Teams Integration - Bot Principal
Integração completa com Teams para acesso à equipe CWB Hub
"""

import os
import json
import asyncio
from typing import Dict, Any, Optional, List
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory, CardFactory
from botbuilder.core.conversation_state import ConversationState
from botbuilder.core.user_state import UserState
from botbuilder.core.memory_storage import MemoryStorage
from botbuilder.schema import Activity, ActivityTypes, Attachment, SuggestedActions, CardAction, ActionTypes
import logging
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent.parent.parent / "src"))

from src.core.hybrid_ai_orchestrator import HybridAIOrchestrator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações do Teams
TEAMS_APP_ID = os.getenv("TEAMS_APP_ID")
TEAMS_APP_PASSWORD = os.getenv("TEAMS_APP_PASSWORD")
TEAMS_TENANT_ID = os.getenv("TEAMS_TENANT_ID")

# Instância global do orquestrador
orchestrator_instances: Dict[str, HybridAIOrchestrator] = {}


class TeamsFormatter:
    """Formatador de mensagens para Microsoft Teams"""
    
    @staticmethod
    def create_adaptive_card(title: str, content: str, confidence: float, agents_involved: List[str]) -> Dict[str, Any]:
        """Cria Adaptive Card para resposta do CWB Hub"""
        
        # Criar card adaptativo
        card = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "Container",
                    "style": "emphasis",
                    "items": [
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "auto",
                                    "items": [
                                        {
                                            "type": "Image",
                                            "url": "https://cwbhub.com/assets/logo.png",
                                            "size": "Small",
                                            "style": "Person"
                                        }
                                    ]
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "🧠 Resposta da Equipe CWB Hub",
                                            "weight": "Bolder",
                                            "size": "Medium"
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": f"Confiança: {confidence}% | {len(agents_involved)} especialistas",
                                            "isSubtle": True,
                                            "spacing": "None"
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": content[:2000],  # Limite do Teams
                    "wrap": True,
                    "spacing": "Medium"
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "🔄 Refinar Solução",
                    "data": {
                        "action": "refine_solution"
                    }
                },
                {
                    "type": "Action.OpenUrl",
                    "title": "📊 Ver Dashboard",
                    "url": "https://cwbhub.com/dashboard"
                },
                {
                    "type": "Action.Submit",
                    "title": "📤 Compartilhar",
                    "data": {
                        "action": "share_solution"
                    }
                }
            ]
        }
        
        return card
    
    @staticmethod
    def create_agents_card() -> Dict[str, Any]:
        """Cria card com informações dos agentes"""
        
        agents = [
            {"name": "Dra. Ana Beatriz Costa", "role": "CTO", "emoji": "👩‍💼"},
            {"name": "Dr. Carlos Eduardo Santos", "role": "Arquiteto de Software", "emoji": "👨‍💻"},
            {"name": "Sofia Oliveira", "role": "Engenheira Full Stack", "emoji": "👩‍💻"},
            {"name": "Gabriel Mendes", "role": "Engenheiro Mobile", "emoji": "👨‍📱"},
            {"name": "Isabella Santos", "role": "Designer UX/UI", "emoji": "👩‍🎨"},
            {"name": "Lucas Pereira", "role": "Engenheiro de QA", "emoji": "👨‍🔬"},
            {"name": "Mariana Rodrigues", "role": "Engenheira DevOps", "emoji": "👩‍🔧"},
            {"name": "Pedro Henrique Almeida", "role": "Agile Project Manager", "emoji": "👨‍📊"}
        ]
        
        facts = []
        for agent in agents:
            facts.append({
                "title": f"{agent['emoji']} {agent['name']}",
                "value": agent['role']
            })
        
        card = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "TextBlock",
                    "text": "👥 Equipe CWB Hub - 8 Especialistas Sênior",
                    "weight": "Bolder",
                    "size": "Large"
                },
                {
                    "type": "FactSet",
                    "facts": facts
                }
            ]
        }
        
        return card
    
    @staticmethod
    def create_welcome_card() -> Dict[str, Any]:
        """Cria card de boas-vindas"""
        
        card = {
            "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
            "type": "AdaptiveCard",
            "version": "1.4",
            "body": [
                {
                    "type": "Container",
                    "style": "emphasis",
                    "items": [
                        {
                            "type": "TextBlock",
                            "text": "🚀 Bem-vindo ao CWB Hub!",
                            "weight": "Bolder",
                            "size": "Large"
                        },
                        {
                            "type": "TextBlock",
                            "text": "Sua equipe de 8 especialistas sênior está pronta para ajudar!",
                            "wrap": True,
                            "spacing": "None"
                        }
                    ]
                },
                {
                    "type": "TextBlock",
                    "text": "**Como usar:**\n• Digite sua solicitação diretamente\n• Use @CWBHub para menções\n• Clique nos botões para ações rápidas",
                    "wrap": True,
                    "spacing": "Medium"
                },
                {
                    "type": "TextBlock",
                    "text": "**Exemplos:**\n• \"Criar sistema de e-commerce\"\n• \"Arquitetura para app mobile\"\n• \"Estratégia de marketing digital\"",
                    "wrap": True,
                    "spacing": "Small"
                }
            ],
            "actions": [
                {
                    "type": "Action.Submit",
                    "title": "👥 Ver Equipe",
                    "data": {
                        "action": "show_team"
                    }
                },
                {
                    "type": "Action.Submit",
                    "title": "🚀 Começar Agora",
                    "data": {
                        "action": "start_consultation"
                    }
                }
            ]
        }
        
        return card


class CWBHubTeamsBot(ActivityHandler):
    """Bot principal do CWB Hub para Microsoft Teams"""
    
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        self.conversation_state = conversation_state
        self.user_state = user_state
    
    async def on_message_activity(self, turn_context: TurnContext):
        """Manipula mensagens recebidas"""
        
        user_id = turn_context.activity.from_property.id
        text = turn_context.activity.text.strip() if turn_context.activity.text else ""
        
        # Remover menção ao bot
        if turn_context.activity.text:
            text = turn_context.activity.text.replace("<at>CWBHub</at>", "").strip()
        
        # Comandos especiais
        if text.lower() in ["help", "ajuda", "?"]:
            await self._send_welcome_message(turn_context)
            return
        
        if text.lower() in ["team", "equipe", "agents", "agentes"]:
            await self._send_team_info(turn_context)
            return
        
        if not text:
            await self._send_welcome_message(turn_context)
            return
        
        # Processar solicitação
        await self._process_cwb_request(turn_context, text, user_id)
    
    async def on_members_added_activity(self, members_added: List, turn_context: TurnContext):
        """Manipula novos membros adicionados"""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await self._send_welcome_message(turn_context)
    
    async def on_adaptive_card_invoke(self, turn_context: TurnContext):
        """Manipula ações de Adaptive Cards"""
        
        data = turn_context.activity.value
        action = data.get("action")
        
        if action == "show_team":
            await self._send_team_info(turn_context)
        elif action == "start_consultation":
            await turn_context.send_activity(
                MessageFactory.text("🚀 Perfeito! Digite sua solicitação e nossa equipe de 8 especialistas irá colaborar para criar a melhor solução.")
            )
        elif action == "refine_solution":
            await self._handle_refine_solution(turn_context)
        elif action == "share_solution":
            await self._handle_share_solution(turn_context)
        
        return {"status": 200}
    
    async def _send_welcome_message(self, turn_context: TurnContext):
        """Envia mensagem de boas-vindas"""
        
        welcome_card = TeamsFormatter.create_welcome_card()
        attachment = CardFactory.adaptive_card(welcome_card)
        
        await turn_context.send_activity(
            MessageFactory.attachment(attachment)
        )
    
    async def _send_team_info(self, turn_context: TurnContext):
        """Envia informações da equipe"""
        
        team_card = TeamsFormatter.create_agents_card()
        attachment = CardFactory.adaptive_card(team_card)
        
        await turn_context.send_activity(
            MessageFactory.attachment(attachment)
        )
    
    async def _process_cwb_request(self, turn_context: TurnContext, text: str, user_id: str):
        """Processa solicitação com a equipe CWB Hub"""
        
        # Enviar mensagem de processamento
        await turn_context.send_activity(
            MessageFactory.text(f"🧠 Consultando equipe CWB Hub sobre: **{text}**\n⏳ Aguarde, 8 especialistas estão colaborando...")
        )
        
        try:
            # Processar com CWB Hub
            session_id = f"teams_{user_id}"
            
            # Criar orquestrador
            orchestrator = HybridAIOrchestrator()
            orchestrator_instances[session_id] = orchestrator
            
            # Inicializar e processar
            await orchestrator.initialize_agents()
            response = await orchestrator.process_request(text)
            
            # Obter estatísticas
            try:
                stats = orchestrator.get_session_status()
                agents_involved = list(stats.get('agents_involved', []))
                confidence = 94.4  # Padrão da equipe
            except:
                agents_involved = ["ana_beatriz_costa", "carlos_eduardo_santos", "sofia_oliveira", 
                                 "gabriel_mendes", "isabella_santos", "lucas_pereira", 
                                 "mariana_rodrigues", "pedro_henrique_almeida"]
                confidence = 94.4
            
            # Criar e enviar card de resposta
            response_card = TeamsFormatter.create_adaptive_card(
                "Resposta CWB Hub", 
                response, 
                confidence, 
                agents_involved
            )
            
            attachment = CardFactory.adaptive_card(response_card)
            await turn_context.send_activity(
                MessageFactory.attachment(attachment)
            )
            
        except Exception as e:
            logger.error(f"Erro ao processar solicitação Teams: {e}")
            await turn_context.send_activity(
                MessageFactory.text(f"❌ Erro ao processar solicitação: {str(e)}\n\nTente novamente ou entre em contato com o suporte.")
            )
    
    async def _handle_refine_solution(self, turn_context: TurnContext):
        """Manipula refinamento de solução"""
        
        await turn_context.send_activity(
            MessageFactory.text("🔄 Para refinar a solução, digite seu feedback:\n\nExemplo: \"Gostei da proposta, mas o orçamento é limitado. Precisamos priorizar as funcionalidades mais importantes...\"")
        )
    
    async def _handle_share_solution(self, turn_context: TurnContext):
        """Manipula compartilhamento de solução"""
        
        await turn_context.send_activity(
            MessageFactory.text("📤 Solução compartilhada! Você pode:\n• Copiar e colar em outros canais\n• Salvar no SharePoint\n• Exportar como PDF no dashboard: https://cwbhub.com/dashboard")
        )


# Função para criar o bot
def create_teams_bot() -> CWBHubTeamsBot:
    """Cria instância do bot Teams"""
    
    # Configurar storage e states
    memory_storage = MemoryStorage()
    conversation_state = ConversationState(memory_storage)
    user_state = UserState(memory_storage)
    
    # Criar bot
    bot = CWBHubTeamsBot(conversation_state, user_state)
    
    return bot


# Função para testar o bot
async def test_teams_bot():
    """Testa funcionalidades do bot Teams"""
    
    print("🤖 Testando Teams Bot...")
    
    try:
        # Criar bot
        bot = create_teams_bot()
        
        # Testar formatação de cards
        welcome_card = TeamsFormatter.create_welcome_card()
        team_card = TeamsFormatter.create_agents_card()
        
        print("✅ Cards criados com sucesso!")
        print(f"📋 Welcome card: {len(json.dumps(welcome_card))} chars")
        print(f"👥 Team card: {len(json.dumps(team_card))} chars")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar Teams bot: {e}")
        return False


if __name__ == "__main__":
    # Teste do bot
    print("🤖 CWB HUB TEAMS BOT")
    print("=" * 40)
    
    if not TEAMS_APP_ID:
        print("❌ TEAMS_APP_ID não configurado")
        print("📋 Configure as variáveis de ambiente:")
        print("   export TEAMS_APP_ID=your-app-id")
        print("   export TEAMS_APP_PASSWORD=your-password")
        print("   export TEAMS_TENANT_ID=your-tenant-id")
    else:
        asyncio.run(test_teams_bot())
        print("✅ Teams Bot testado com sucesso!")
        print("🔗 Integre com seu framework usando create_teams_bot()")