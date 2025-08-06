#!/usr/bin/env python3
"""
Script de instalação inteligente para dependências do CWB Hub
Resolve automaticamente problemas de compilação e dependências
"""

import subprocess
import sys
import platform
import os
from pathlib import Path


def run_command(command, description=""):
    """Executa comando e trata erros"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - Sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - Erro: {e.stderr}")
        return False


def check_python_version():
    """Verifica versão do Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ é necessário")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
    return True


def upgrade_pip():
    """Atualiza pip para versão mais recente"""
    return run_command(f"{sys.executable} -m pip install --upgrade pip", "Atualizando pip")


def install_basic_dependencies():
    """Instala dependências básicas primeiro"""
    basic_deps = [
        "wheel",
        "setuptools",
        "typing-extensions>=4.8.0",
        "asyncio-mqtt>=0.16.1",
        "dataclasses-json>=0.6.3",
        "structlog>=23.2.0",
        "prometheus-client>=0.19.0"
    ]
    
    for dep in basic_deps:
        if not run_command(f"{sys.executable} -m pip install '{dep}'", f"Instalando {dep}"):
            return False
    return True


def install_pydantic_safely():
    """Instala pydantic de forma segura"""
    print("🔄 Instalando pydantic (pode demorar um pouco)...")
    
    # Tenta instalar versão mais recente primeiro
    if run_command(f"{sys.executable} -m pip install 'pydantic>=2.11.0'", "Instalando pydantic recente"):
        return True
    
    # Se falhar, tenta com --only-binary para forçar wheels
    print("⚠️  Tentando instalação apenas com wheels pré-compilados...")
    if run_command(f"{sys.executable} -m pip install --only-binary=all 'pydantic>=2.8.0'", "Instalando pydantic (wheels only)"):
        return True
    
    # Última tentativa com versão mais antiga estável
    print("⚠️  Tentando versão mais antiga estável...")
    if run_command(f"{sys.executable} -m pip install 'pydantic==2.8.2'", "Instalando pydantic 2.8.2"):
        return True
    
    print("❌ Não foi possível instalar pydantic. Verifique se Rust está instalado.")
    return False


def install_dev_dependencies():
    """Instala dependências de desenvolvimento"""
    dev_deps = [
        "pytest>=7.4.3",
        "pytest-asyncio>=0.21.1",
        "pytest-cov>=4.1.0",
        "black>=23.11.0",
        "flake8>=6.1.0",
        "mypy>=1.7.1"
    ]
    
    for dep in dev_deps:
        if not run_command(f"{sys.executable} -m pip install '{dep}'", f"Instalando {dep}"):
            print(f"⚠️  Falha ao instalar {dep}, continuando...")
    
    return True


def verify_installation():
    """Verifica se a instalação foi bem-sucedida"""
    print("\n🔍 Verificando instalação...")
    
    required_packages = [
        "pydantic",
        "asyncio_mqtt",
        "dataclasses_json",
        "structlog",
        "prometheus_client"
    ]
    
    failed_imports = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - FALHOU")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Pacotes com falha: {', '.join(failed_imports)}")
        return False
    
    print("\n✅ Todas as dependências foram instaladas com sucesso!")
    return True


def show_troubleshooting():
    """Mostra dicas de solução de problemas"""
    print("\n🔧 DICAS DE SOLUÇÃO DE PROBLEMAS:")
    print("=" * 50)
    
    if platform.system() == "Windows":
        print("Windows:")
        print("1. Instale Visual Studio Build Tools")
        print("2. Ou instale Rust: https://rustup.rs/")
        print("3. Use conda: conda install pydantic")
    
    elif platform.system() == "Linux":
        print("Linux:")
        print("1. sudo apt-get install build-essential")
        print("2. curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
        print("3. Use conda: conda install pydantic")
    
    elif platform.system() == "Darwin":
        print("macOS:")
        print("1. xcode-select --install")
        print("2. curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh")
        print("3. Use conda: conda install pydantic")
    
    print("\nAlternativas:")
    print("- Use Python 3.11+ (melhor compatibilidade)")
    print("- Use ambiente virtual: python -m venv venv")
    print("- Use conda em vez de pip")


def main():
    """Função principal"""
    print("🚀 CWB Hub - Instalador Inteligente de Dependências")
    print("=" * 55)
    
    # Verificações iniciais
    if not check_python_version():
        return False
    
    # Atualizar pip
    if not upgrade_pip():
        print("⚠️  Falha ao atualizar pip, continuando...")
    
    # Instalar dependências básicas
    if not install_basic_dependencies():
        print("❌ Falha ao instalar dependências básicas")
        show_troubleshooting()
        return False
    
    # Instalar pydantic de forma segura
    if not install_pydantic_safely():
        print("❌ Falha ao instalar pydantic")
        show_troubleshooting()
        return False
    
    # Instalar dependências de desenvolvimento
    install_dev_dependencies()
    
    # Verificar instalação
    if verify_installation():
        print("\n🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print("Agora você pode executar: python main.py")
        return True
    else:
        show_troubleshooting()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)