#!/usr/bin/env python3
"""
Script de instalação e teste do plugin VSCode CWB Hub
Criado por: David Simer
"""

import os
import subprocess
import sys
import json
from pathlib import Path

def run_command(command, cwd=None):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd, 
            capture_output=True, 
            text=True,
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_prerequisites():
    """Verifica pré-requisitos"""
    print("🔍 Verificando pré-requisitos...")
    
    # Verificar Node.js
    success, output = run_command("node --version")
    if not success:
        print("❌ Node.js não encontrado. Instale Node.js 16+ primeiro.")
        return False
    
    node_version = output.strip()
    print(f"✅ Node.js: {node_version}")
    
    # Verificar npm
    success, output = run_command("npm --version")
    if not success:
        print("❌ npm não encontrado.")
        return False
    
    npm_version = output.strip()
    print(f"✅ npm: {npm_version}")
    
    # Verificar VSCode
    success, output = run_command("code --version")
    if not success:
        print("⚠️ VSCode CLI não encontrado. Instale VSCode ou adicione ao PATH.")
        print("   O plugin ainda pode ser testado manualmente.")
    else:
        vscode_version = output.strip().split('\n')[0]
        print(f"✅ VSCode: {vscode_version}")
    
    return True

def install_dependencies():
    """Instala dependências do projeto"""
    print("\n📦 Instalando dependências...")
    
    plugin_dir = Path(__file__).parent
    
    success, output = run_command("npm install", cwd=plugin_dir)
    if not success:
        print(f"❌ Erro ao instalar dependências: {output}")
        return False
    
    print("✅ Dependências instaladas com sucesso!")
    return True

def compile_typescript():
    """Compila o TypeScript"""
    print("\n🔨 Compilando TypeScript...")
    
    plugin_dir = Path(__file__).parent
    
    success, output = run_command("npm run compile", cwd=plugin_dir)
    if not success:
        print(f"❌ Erro na compilação: {output}")
        return False
    
    print("✅ TypeScript compilado com sucesso!")
    return True

def package_extension():
    """Gera o pacote VSIX da extensão"""
    print("\n📦 Gerando pacote VSIX...")
    
    plugin_dir = Path(__file__).parent
    
    # Instalar vsce se não estiver instalado
    success, output = run_command("npm list -g vsce")
    if not success:
        print("📥 Instalando vsce...")
        success, output = run_command("npm install -g vsce")
        if not success:
            print(f"❌ Erro ao instalar vsce: {output}")
            return False
    
    # Gerar pacote
    success, output = run_command("npm run package", cwd=plugin_dir)
    if not success:
        print(f"❌ Erro ao gerar pacote: {output}")
        return False
    
    print("✅ Pacote VSIX gerado com sucesso!")
    
    # Encontrar arquivo VSIX
    vsix_files = list(plugin_dir.glob("*.vsix"))
    if vsix_files:
        print(f"📁 Arquivo gerado: {vsix_files[0].name}")
    
    return True

def test_api_connection():
    """Testa conexão com a API CWB Hub"""
    print("\n🔗 Testando conexão com API CWB Hub...")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API CWB Hub está rodando!")
            return True
        else:
            print(f"⚠️ API retornou status {response.status_code}")
            return False
    except ImportError:
        print("⚠️ Biblioteca 'requests' não encontrada. Instalando...")
        success, output = run_command("pip install requests")
        if success:
            return test_api_connection()
        else:
            print("❌ Não foi possível instalar 'requests'")
            return False
    except Exception as e:
        print(f"⚠️ Não foi possível conectar à API: {e}")
        print("   Certifique-se de que o CWB Hub está rodando em http://localhost:8000")
        return False

def show_installation_instructions():
    """Mostra instruções de instalação manual"""
    print("\n" + "="*60)
    print("📋 INSTRUÇÕES DE INSTALAÇÃO MANUAL")
    print("="*60)
    print()
    print("1. Abra o VSCode")
    print("2. Pressione Ctrl+Shift+P")
    print("3. Digite 'Extensions: Install from VSIX'")
    print("4. Selecione o arquivo .vsix gerado")
    print("5. Reinicie o VSCode")
    print()
    print("OU")
    print()
    print("1. Abra o terminal no diretório do plugin")
    print("2. Execute: code --install-extension cwb-hub-ai-assistant-*.vsix")
    print()
    print("="*60)
    print("🎯 COMO USAR APÓS INSTALAÇÃO")
    print("="*60)
    print()
    print("1. Configure o endpoint da API:")
    print("   - Ctrl+, → Procure 'CWB Hub'")
    print("   - Configure 'cwb-hub.apiEndpoint': 'http://localhost:8000'")
    print()
    print("2. Use os comandos:")
    print("   - Ctrl+Shift+P → 'CWB Hub: Analisar Projeto'")
    print("   - Ctrl+Shift+P → 'CWB Hub: Consultar Equipe'")
    print("   - Clique direito no código → 'CWB Hub: Revisar Código'")
    print()
    print("3. Visualize a equipe na sidebar (ícone de organização)")
    print()

def main():
    """Função principal"""
    print("🚀 INSTALAÇÃO DO PLUGIN CWB HUB VSCODE")
    print("="*50)
    
    # Verificar pré-requisitos
    if not check_prerequisites():
        return False
    
    # Instalar dependências
    if not install_dependencies():
        return False
    
    # Compilar TypeScript
    if not compile_typescript():
        return False
    
    # Gerar pacote
    if not package_extension():
        return False
    
    # Testar API
    api_ok = test_api_connection()
    
    # Mostrar instruções
    show_installation_instructions()
    
    print("\n🎉 PLUGIN PRONTO PARA INSTALAÇÃO!")
    print()
    if api_ok:
        print("✅ API CWB Hub está funcionando")
    else:
        print("⚠️ Inicie o CWB Hub antes de usar o plugin")
    
    print("\n📁 Arquivos gerados:")
    plugin_dir = Path(__file__).parent
    for vsix_file in plugin_dir.glob("*.vsix"):
        print(f"   - {vsix_file.name}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)