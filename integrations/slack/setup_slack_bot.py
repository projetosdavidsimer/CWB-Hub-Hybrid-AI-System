#!/usr/bin/env python3
"""
Setup do CWB Hub Slack Bot
Melhoria #3 Fase 2 - Configuração e teste do bot
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def install_dependencies():
    """Instalar dependências do Slack Bot"""
    print("📦 Instalando dependências do Slack Bot...")
    
    try:
        # Instalar dependências das integrações
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "../requirements.txt"
        ])
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def create_env_template():
    """Criar template de variáveis de ambiente"""
    env_template = """# CWB Hub Slack Bot - Environment Variables
# Copie este arquivo para .env e configure com seus tokens reais

# Slack Bot Token (começa com xoxb-)
SLACK_BOT_TOKEN=xoxb-your-bot-token-here

# Slack App Token (começa com xapp-)
SLACK_APP_TOKEN=xapp-your-app-token-here

# Slack Signing Secret
SLACK_SIGNING_SECRET=your-signing-secret-here

# Opcional: Configurações adicionais
SLACK_LOG_LEVEL=INFO
CWB_HUB_API_URL=http://localhost:8000
"""
    
    env_file = Path(".env.template")
    with open(env_file, "w") as f:
        f.write(env_template)
    
    print(f"✅ Template criado: {env_file}")
    print("📝 Configure suas credenciais copiando .env.template para .env")

def check_environment():
    """Verificar se as variáveis de ambiente estão configuradas"""
    required_vars = [
        "SLACK_BOT_TOKEN",
        "SLACK_APP_TOKEN", 
        "SLACK_SIGNING_SECRET"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.environ.get(var) or os.environ.get(var).startswith("your-"):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Variáveis de ambiente não configuradas:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Configure as variáveis de ambiente:")
        print("   1. Copie .env.template para .env")
        print("   2. Configure os tokens reais do Slack")
        print("   3. Execute: source .env (Linux/Mac) ou set no Windows")
        return False
    
    print("✅ Variáveis de ambiente configuradas!")
    return True

def show_slack_setup_instructions():
    """Mostrar instruções para configurar o Slack App"""
    instructions = """
🔧 CONFIGURAÇÃO DO SLACK APP

Para usar o CWB Hub Slack Bot, você precisa criar um Slack App:

1. **Criar Slack App:**
   - Acesse: https://api.slack.com/apps
   - Clique em "Create New App"
   - Escolha "From scratch"
   - Nome: "CWB Hub Bot"
   - Workspace: Seu workspace

2. **Configurar OAuth & Permissions:**
   - Vá em "OAuth & Permissions"
   - Adicione Bot Token Scopes:
     * app_mentions:read
     * channels:history
     * chat:write
     * commands
     * im:history
     * im:write
   - Instale o app no workspace
   - Copie o "Bot User OAuth Token" (xoxb-...)

3. **Configurar Socket Mode:**
   - Vá em "Socket Mode"
   - Enable Socket Mode
   - Copie o "App-Level Token" (xapp-...)

4. **Configurar Slash Commands:**
   - Vá em "Slash Commands"
   - Adicione os comandos:
     * /cwb-analyze - Analisar projeto
     * /cwb-iterate - Refinar solução
     * /cwb-status - Ver status
     * /cwb-help - Ajuda

5. **Configurar Event Subscriptions:**
   - Vá em "Event Subscriptions"
   - Enable Events
   - Subscribe to bot events:
     * app_mention
     * message.im

6. **Obter Signing Secret:**
   - Vá em "Basic Information"
   - Copie o "Signing Secret"

7. **Configurar Variáveis:**
   - Configure as variáveis no arquivo .env
   - SLACK_BOT_TOKEN=xoxb-...
   - SLACK_APP_TOKEN=xapp-...
   - SLACK_SIGNING_SECRET=...

8. **Testar:**
   - Execute: python slack_bot.py
   - No Slack: @CWB Hub Bot help
   - Ou use: /cwb-help
"""
    
    print(instructions)

async def test_slack_bot():
    """Testar o Slack Bot"""
    print("🧪 Testando CWB Hub Slack Bot...")
    
    if not check_environment():
        return False
    
    try:
        # Importar e testar o bot
        from slack_bot import CWBHubSlackBot, start_slack_bot
        
        print("✅ Imports do Slack Bot OK")
        
        # Testar inicialização básica
        bot = CWBHubSlackBot()
        print("✅ Instância do bot criada")
        
        # Testar inicialização do CWB Hub
        cwb_available = await bot.initialize_cwb_hub()
        if cwb_available:
            print("✅ CWB Hub disponível")
        else:
            print("⚠️ CWB Hub não disponível (modo desenvolvimento)")
        
        print("✅ Slack Bot pronto para uso!")
        print("\n🚀 Para iniciar o bot:")
        print("   python slack_bot.py")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de import: {e}")
        print("💡 Instale as dependências: pip install -r ../requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        return False

def main():
    """Função principal"""
    print("🤖 CWB HUB SLACK BOT - SETUP")
    print("Melhoria #3 Fase 2 - Integração com Slack")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("slack_bot.py"):
        print("❌ Execute este script do diretório integrations/slack/")
        return
    
    # Instalar dependências
    if not install_dependencies():
        return
    
    # Criar template de ambiente
    create_env_template()
    
    # Mostrar instruções
    show_slack_setup_instructions()
    
    # Verificar ambiente
    env_ok = check_environment()
    
    if env_ok:
        # Testar bot
        try:
            asyncio.run(test_slack_bot())
        except KeyboardInterrupt:
            print("\n⚠️ Teste interrompido pelo usuário")
    else:
        print("\n⚠️ Configure as variáveis de ambiente antes de testar")
    
    print("\n🎉 Setup do Slack Bot concluído!")
    print("📚 Documentação: https://api.slack.com/bolt-python")

if __name__ == "__main__":
    main()