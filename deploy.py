#!/usr/bin/env python3
"""
Script de Deploy do CWB Hub Hybrid AI System
Automatiza o processo de deploy e configuração do sistema
"""

import os
import sys
import subprocess
import asyncio
import logging
from pathlib import Path


class CWBHubDeployer:
    """Classe responsável pelo deploy do sistema CWB Hub"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """Configura logging para o deploy"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
    
    def check_requirements(self):
        """Verifica se os requisitos estão instalados"""
        self.logger.info("🔍 Verificando requisitos...")
        
        try:
            import asyncio
            import dataclasses
            self.logger.info("✅ Requisitos básicos encontrados")
            return True
        except ImportError as e:
            self.logger.error(f"❌ Requisito faltando: {e}")
            return False
    
    def install_dependencies(self):
        """Instala dependências do projeto"""
        self.logger.info("📦 Instalando dependências...")
        
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            self.logger.error("❌ Arquivo requirements.txt não encontrado")
            return False
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True, capture_output=True, text=True)
            
            self.logger.info("✅ Dependências instaladas com sucesso")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Erro ao instalar dependências: {e}")
            return False
    
    def run_tests(self):
        """Executa testes do sistema"""
        self.logger.info("🧪 Executando testes...")
        
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/", "-v"
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                self.logger.info("✅ Todos os testes passaram")
                return True
            else:
                self.logger.error("❌ Alguns testes falharam:")
                self.logger.error(result.stdout)
                self.logger.error(result.stderr)
                return False
        except Exception as e:
            self.logger.error(f"❌ Erro ao executar testes: {e}")
            return False
    
    async def validate_system(self):
        """Valida se o sistema está funcionando corretamente"""
        self.logger.info("🔧 Validando sistema...")
        
        try:
            from src.core.hybrid_ai_orchestrator import HybridAIOrchestrator
            
            # Teste básico de inicialização
            orchestrator = HybridAIOrchestrator()
            await orchestrator.initialize_agents()
            
            # Verificar se todos os agentes foram carregados
            agents = orchestrator.get_active_agents()
            expected_count = 8
            
            if len(agents) == expected_count:
                self.logger.info(f"✅ Sistema validado: {len(agents)} agentes ativos")
                await orchestrator.shutdown()
                return True
            else:
                self.logger.error(f"❌ Esperado {expected_count} agentes, encontrado {len(agents)}")
                await orchestrator.shutdown()
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Erro na validação: {e}")
            return False
    
    def create_config_files(self):
        """Cria arquivos de configuração necessários"""
        self.logger.info("⚙️ Criando arquivos de configuração...")
        
        config_dir = self.project_root / "config"
        config_dir.mkdir(exist_ok=True)
        
        # Configuração básica
        config_content = """
# CWB Hub Hybrid AI Configuration

[system]
log_level = INFO
max_sessions = 100
session_timeout = 3600

[agents]
max_collaborations_per_round = 6
collaboration_timeout = 30

[performance]
enable_caching = true
cache_ttl = 300
max_response_length = 10000
        """.strip()
        
        config_file = config_dir / "system.conf"
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        self.logger.info(f"✅ Configuração criada em {config_file}")
        return True
    
    def setup_environment(self):
        """Configura ambiente de execução"""
        self.logger.info("🌍 Configurando ambiente...")
        
        # Criar diretórios necessários
        dirs_to_create = [
            "logs",
            "data",
            "cache",
            "exports"
        ]
        
        for dir_name in dirs_to_create:
            dir_path = self.project_root / dir_name
            dir_path.mkdir(exist_ok=True)
            self.logger.info(f"📁 Diretório criado: {dir_name}")
        
        return True
    
    async def deploy(self):
        """Executa o processo completo de deploy"""
        self.logger.info("🚀 Iniciando deploy do CWB Hub Hybrid AI...")
        
        steps = [
            ("Verificar requisitos", self.check_requirements),
            ("Instalar dependências", self.install_dependencies),
            ("Configurar ambiente", self.setup_environment),
            ("Criar configurações", self.create_config_files),
            ("Executar testes", self.run_tests),
            ("Validar sistema", self.validate_system)
        ]
        
        for step_name, step_func in steps:
            self.logger.info(f"📋 Executando: {step_name}")
            
            if asyncio.iscoroutinefunction(step_func):
                success = await step_func()
            else:
                success = step_func()
            
            if not success:
                self.logger.error(f"❌ Falha em: {step_name}")
                return False
        
        self.logger.info("🎉 Deploy concluído com sucesso!")
        self.logger.info("💡 Para usar o sistema, execute: python main.py")
        return True


async def main():
    """Função principal do script de deploy"""
    deployer = CWBHubDeployer()
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                    CWB HUB HYBRID AI                         ║
    ║                      DEPLOY SCRIPT                          ║
    ║                                                              ║
    ║  Este script irá configurar e validar o sistema completo    ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    success = await deployer.deploy()
    
    if success:
        print("\n✅ Sistema pronto para uso!")
        print("🚀 Execute 'python main.py' para testar")
        sys.exit(0)
    else:
        print("\n❌ Deploy falhou. Verifique os logs acima.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())