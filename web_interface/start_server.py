#!/usr/bin/env python3
"""
Script para iniciar o servidor web do CWB Hub
"""

import subprocess
import sys
import os
from pathlib import Path
import webbrowser
import time
import threading

def install_requirements():
    """Instala dependências necessárias"""
    print("📦 Instalando dependências...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", 
            str(Path(__file__).parent / "requirements.txt")
        ], check=True)
        print("✅ Dependências instaladas com sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False

def start_backend():
    """Inicia o servidor backend"""
    print("🚀 Iniciando servidor backend...")
    backend_path = Path(__file__).parent / "backend" / "main.py"
    
    try:
        # Iniciar servidor em processo separado
        process = subprocess.Popen([
            sys.executable, str(backend_path)
        ], cwd=str(Path(__file__).parent.parent))
        
        print("✅ Servidor backend iniciado!")
        print("🌐 API disponível em: http://localhost:8000")
        print("📚 Documentação em: http://localhost:8000/docs")
        
        return process
    except Exception as e:
        print(f"❌ Erro ao iniciar backend: {e}")
        return None

def open_frontend():
    """Abre o frontend no navegador"""
    print("🌐 Abrindo interface web...")
    frontend_path = Path(__file__).parent / "frontend" / "index.html"
    
    # Aguardar um pouco para o backend inicializar
    time.sleep(3)
    
    try:
        webbrowser.open(f"file://{frontend_path.absolute()}")
        print("✅ Interface web aberta no navegador!")
    except Exception as e:
        print(f"❌ Erro ao abrir navegador: {e}")
        print(f"📂 Abra manualmente: {frontend_path.absolute()}")

def main():
    """Função principal"""
    print("🌐 CWB HUB WEB INTERFACE LAUNCHER")
    print("=" * 50)
    
    # Verificar se estamos no diretório correto
    if not (Path(__file__).parent / "backend" / "main.py").exists():
        print("❌ Arquivos do backend não encontrados!")
        print("Execute este script da pasta web_interface/")
        return
    
    # Instalar dependências
    if not install_requirements():
        print("❌ Falha na instalação de dependências")
        return
    
    # Iniciar backend
    backend_process = start_backend()
    if not backend_process:
        print("❌ Falha ao iniciar backend")
        return
    
    # Abrir frontend em thread separada
    frontend_thread = threading.Thread(target=open_frontend)
    frontend_thread.daemon = True
    frontend_thread.start()
    
    print("\n" + "=" * 50)
    print("🎉 CWB HUB WEB INTERFACE ATIVO!")
    print("=" * 50)
    print("📱 Interface: Aberta no navegador")
    print("🔗 Backend API: http://localhost:8000")
    print("📖 Documentação: http://localhost:8000/docs")
    print("🛑 Para parar: Ctrl+C")
    print("=" * 50)
    
    try:
        # Aguardar até o usuário parar
        backend_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Parando servidor...")
        backend_process.terminate()
        backend_process.wait()
        print("✅ Servidor parado!")

if __name__ == "__main__":
    main()