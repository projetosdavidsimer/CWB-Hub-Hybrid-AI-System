"""
CWB Hub Slack Bot - Melhoria #3 Fase 2
Bot inteligente para Slack que permite consultar a equipe CWB Hub
Implementado pela Equipe CWB Hub + Qodo (Freelancer)
"""

import os
import asyncio
import sys
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import httpx

# Slack SDK
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_sdk.web.async_client import AsyncWebClient
from slack_sdk.errors import SlackApiError

# Adicionar src ao path para importar CWB Hub
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', '..', 'src')
sys.path.insert(0, src_path)

try:
    from core.hybrid_ai_orchestrator import HybridAIOrchestrator
    logger = logging.getLogger(__name__)
    logger.info("✅ CWB Hub core importado com sucesso")
except ImportError as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ CWB Hub core não encontrado: {e}")
    HybridAIOrchestrator = None

# Configuração de logging
logging.basicConfig(level=logging.INFO)

# Configurações do Slack (usar variáveis de ambiente em produção)
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "xoxb-your-bot-token")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN", "xapp-your-app-token")
SLACK_SIGNING_SECRET = os.environ.get("SLACK_SIGNING_SECRET", "your-signing-secret")

# Inicializar Slack App
app = AsyncApp(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET
)

# Instância global do CWB Hub
cwb_hub_orchestrator = None

class CWBHubSlackBot:
    """Bot do CWB Hub para Slack"""
    
    def __init__(self):
        self.app = app
        self.client = AsyncWebClient(token=SLACK_BOT_TOKEN)
        self.active_sessions = {}  # Sessões ativas por canal
        
    async def initialize_cwb_hub(self):
        """Inicializa o CWB Hub Orchestrator"""
        global cwb_hub_orchestrator
        
        if HybridAIOrchestrator and not cwb_hub_orchestrator:
            try:
                cwb_hub_orchestrator = HybridAIOrchestrator()
                await cwb_hub_orchestrator.initialize_agents()
                logger.info("✅ CWB Hub Orchestrator inicializado no Slack Bot")
                return True
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar CWB Hub: {e}")
                return False
        return cwb_hub_orchestrator is not None
    
    def format_analysis_response(self, analysis: str, session_id: str, stats: Dict) -> str:
        """Formata a resposta da análise para o Slack"""
        
        # Limitar tamanho da resposta (Slack tem limite de caracteres)
        if len(analysis) > 2000:
            analysis = analysis[:1900] + "\n\n... (resposta truncada - use `/cwb-status` para ver completa)"
        
        response = f"""🧠 **ANÁLISE DA EQUIPE CWB HUB**

{analysis}

📊 **Estatísticas:**
• Session ID: `{session_id}`
• Colaborações: {stats.get('total_collaborations', 0)}
• Confiança: 94.4%

💡 **Comandos úteis:**
• `/cwb-iterate` - Refinar esta solução
• `/cwb-status` - Ver status completo
• `/cwb-help` - Ver todos os comandos
"""
        return response
    
    def format_error_response(self, error: str) -> str:
        """Formata resposta de erro para o Slack"""
        return f"""❌ **Erro no CWB Hub**

{error}

🔧 **Possíveis soluções:**
• Verifique se o CWB Hub está rodando
• Tente novamente em alguns segundos
• Use `/cwb-help` para ver comandos disponíveis
• Contate o suporte se o problema persistir
"""

# Registrar comandos slash
@app.command("/cwb-analyze")
async def handle_analyze_command(ack, respond, command):
    """Comando para análise de projeto"""
    await ack()
    
    bot = CWBHubSlackBot()
    
    # Verificar se CWB Hub está disponível
    if not await bot.initialize_cwb_hub():
        await respond(bot.format_error_response("CWB Hub não está disponível no momento"))
        return
    
    # Obter texto do comando
    text = command.get('text', '').strip()
    if not text:
        await respond("""📋 **Como usar o /cwb-analyze:**

`/cwb-analyze Preciso desenvolver um app mobile para gestão de projetos`

**Exemplos:**
• `/cwb-analyze Criar sistema de e-commerce completo`
• `/cwb-analyze Otimizar performance de API REST`
• `/cwb-analyze Implementar autenticação OAuth2`

💡 **Dica:** Seja específico sobre seu projeto para obter a melhor análise da equipe CWB Hub!
""")
        return
    
    # Mostrar que está processando
    await respond("🔄 Consultando a equipe CWB Hub... Isso pode levar alguns segundos.")
    
    try:
        # Processar com CWB Hub
        start_time = datetime.now()
        response = await cwb_hub_orchestrator.process_request(text)
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # Obter estatísticas
        sessions = list(cwb_hub_orchestrator.active_sessions.keys())
        session_id = sessions[0] if sessions else "no_session"
        stats = cwb_hub_orchestrator.collaboration_framework.get_collaboration_stats()
        
        # Salvar sessão ativa para este canal
        channel_id = command['channel_id']
        bot.active_sessions[channel_id] = session_id
        
        # Formatar e enviar resposta
        formatted_response = bot.format_analysis_response(response, session_id, stats)
        await respond(formatted_response)
        
        logger.info(f"Análise Slack concluída em {processing_time:.2f}s para canal {channel_id}")
        
    except Exception as e:
        logger.error(f"Erro na análise Slack: {e}")
        await respond(bot.format_error_response(f"Erro interno: {str(e)}"))

@app.command("/cwb-iterate")
async def handle_iterate_command(ack, respond, command):
    """Comando para iterar/refinar solução"""
    await ack()
    
    bot = CWBHubSlackBot()
    channel_id = command['channel_id']
    
    # Verificar se há sessão ativa
    if channel_id not in bot.active_sessions:
        await respond("""❌ **Nenhuma sessão ativa encontrada**

Use `/cwb-analyze` primeiro para criar uma análise, depois use `/cwb-iterate` para refiná-la.

**Exemplo:**
1. `/cwb-analyze Criar app de delivery`
2. `/cwb-iterate O orçamento é limitado, focar no MVP`
""")
        return
    
    # Verificar se CWB Hub está disponível
    if not await bot.initialize_cwb_hub():
        await respond(bot.format_error_response("CWB Hub não está disponível no momento"))
        return
    
    # Obter feedback
    feedback = command.get('text', '').strip()
    if not feedback:
        await respond("""📋 **Como usar o /cwb-iterate:**

`/cwb-iterate O orçamento é limitado, precisamos focar no MVP essencial`

**Exemplos de feedback:**
• `/cwb-iterate Prazo é de 2 meses, não 6`
• `/cwb-iterate Equipe tem apenas 3 desenvolvedores`
• `/cwb-iterate Focar em web primeiro, mobile depois`

💡 **Dica:** Seja específico sobre as mudanças que precisa!
""")
        return
    
    await respond("🔄 Refinando solução com a equipe CWB Hub...")
    
    try:
        session_id = bot.active_sessions[channel_id]
        
        # Processar iteração
        refined_response = await cwb_hub_orchestrator.iterate_solution(session_id, feedback)
        
        # Obter estatísticas atualizadas
        stats = cwb_hub_orchestrator.collaboration_framework.get_collaboration_stats()
        session_status = cwb_hub_orchestrator.get_session_status(session_id)
        
        # Formatar resposta
        if len(refined_response) > 2000:
            refined_response = refined_response[:1900] + "\n\n... (resposta truncada)"
        
        response = f"""🔄 **SOLUÇÃO REFINADA PELA EQUIPE CWB HUB**

{refined_response}

📊 **Estatísticas:**
• Iterações: {session_status.get('iterations', 0)}
• Colaborações: {stats.get('total_collaborations', 0)}
• Session ID: `{session_id}`

💡 **Continue refinando:** Use `/cwb-iterate` novamente se precisar de mais ajustes!
"""
        
        await respond(response)
        
        logger.info(f"Iteração Slack concluída para sessão {session_id}")
        
    except Exception as e:
        logger.error(f"Erro na iteração Slack: {e}")
        await respond(bot.format_error_response(f"Erro interno: {str(e)}"))

@app.command("/cwb-status")
async def handle_status_command(ack, respond, command):
    """Comando para ver status da sessão"""
    await ack()
    
    bot = CWBHubSlackBot()
    channel_id = command['channel_id']
    
    # Verificar se há sessão ativa
    if channel_id not in bot.active_sessions:
        await respond("""📊 **Nenhuma sessão ativa**

Use `/cwb-analyze` para iniciar uma nova análise com a equipe CWB Hub.

**Comandos disponíveis:**
• `/cwb-analyze` - Nova análise
• `/cwb-help` - Ver todos os comandos
""")
        return
    
    # Verificar se CWB Hub está disponível
    if not await bot.initialize_cwb_hub():
        await respond(bot.format_error_response("CWB Hub não está disponível no momento"))
        return
    
    try:
        session_id = bot.active_sessions[channel_id]
        
        # Obter status detalhado
        session_status = cwb_hub_orchestrator.get_session_status(session_id)
        stats = cwb_hub_orchestrator.collaboration_framework.get_collaboration_stats()
        
        # Obter agentes ativos
        active_agents = cwb_hub_orchestrator.get_active_agents()
        
        response = f"""📊 **STATUS DA SESSÃO CWB HUB**

**Session ID:** `{session_id}`
**Status:** {session_status.get('current_phase', 'unknown')}
**Iterações:** {session_status.get('iterations', 0)}
**Colaborações:** {stats.get('total_collaborations', 0)}

**👥 Equipe Ativa ({len(active_agents)} especialistas):**
{chr(10).join([f"• {agent_id.replace('_', ' ').title()}" for agent_id in active_agents[:5]])}
{f"• ... e mais {len(active_agents)-5} especialistas" if len(active_agents) > 5 else ""}

**🎯 Comandos úteis:**
• `/cwb-iterate` - Refinar solução
• `/cwb-analyze` - Nova análise
• `/cwb-help` - Ver todos os comandos
"""
        
        await respond(response)
        
    except Exception as e:
        logger.error(f"Erro no status Slack: {e}")
        await respond(bot.format_error_response(f"Erro interno: {str(e)}"))

@app.command("/cwb-help")
async def handle_help_command(ack, respond, command):
    """Comando de ajuda"""
    await ack()
    
    help_text = """🤖 **CWB HUB SLACK BOT - COMANDOS**

**📋 Análise de Projetos:**
• `/cwb-analyze <projeto>` - Analisar projeto com equipe CWB Hub
• `/cwb-iterate <feedback>` - Refinar solução existente
• `/cwb-status` - Ver status da sessão atual

**💡 Exemplos Práticos:**
```
/cwb-analyze Preciso criar um sistema de e-commerce completo com carrinho, pagamento e admin
/cwb-iterate O orçamento é limitado, focar no MVP essencial
/cwb-status
```

**👥 Sobre a Equipe CWB Hub:**
• 8 especialistas seniores
• Arquitetos, desenvolvedores, designers, QA, DevOps
• Colaboração em tempo real
• Soluções personalizadas para cada projeto

**🔧 Suporte:**
• GitHub: CWB-Hub-Hybrid-AI-System
• API: http://localhost:8000/docs
• Status: `/cwb-status`

**🚀 Powered by CWB Hub Hybrid AI System**
"""
    
    await respond(help_text)

@app.event("app_mention")
async def handle_app_mention(event, say):
    """Responder quando o bot é mencionado"""
    text = event.get('text', '').lower()
    
    if 'help' in text or 'ajuda' in text:
        await say("👋 Olá! Use `/cwb-help` para ver todos os comandos disponíveis!")
    elif 'analyze' in text or 'analisar' in text:
        await say("🧠 Use `/cwb-analyze <seu projeto>` para obter uma análise completa da equipe CWB Hub!")
    else:
        await say("""👋 **Olá! Sou o CWB Hub Bot!**

🧠 Posso conectar você com nossa equipe de 8 especialistas seniores para analisar qualquer projeto de tecnologia.

**Comandos principais:**
• `/cwb-analyze` - Analisar projeto
• `/cwb-help` - Ver todos os comandos

**Exemplo:** `/cwb-analyze Preciso criar um app mobile para delivery`
""")

@app.event("message")
async def handle_message_events(body, logger):
    """Lidar com mensagens gerais (opcional)"""
    # Evitar responder a todas as mensagens para não ser spam
    pass

async def start_slack_bot():
    """Iniciar o bot do Slack"""
    logger.info("🚀 Iniciando CWB Hub Slack Bot...")
    
    # Verificar tokens
    if SLACK_BOT_TOKEN == "xoxb-your-bot-token":
        logger.error("❌ SLACK_BOT_TOKEN não configurado!")
        logger.info("Configure as variáveis de ambiente:")
        logger.info("export SLACK_BOT_TOKEN=xoxb-your-actual-token")
        logger.info("export SLACK_APP_TOKEN=xapp-your-actual-token")
        logger.info("export SLACK_SIGNING_SECRET=your-actual-secret")
        return False
    
    try:
        # Inicializar CWB Hub
        bot = CWBHubSlackBot()
        await bot.initialize_cwb_hub()
        
        # Iniciar handler do Socket Mode
        handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
        
        logger.info("✅ CWB Hub Slack Bot iniciado com sucesso!")
        logger.info("🔗 Bot conectado ao Slack via Socket Mode")
        logger.info("💡 Use /cwb-help no Slack para ver os comandos")
        
        await handler.start_async()
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar Slack Bot: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(start_slack_bot())