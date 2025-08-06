#!/usr/bin/env python3
"""
Script de teste para verificar se a instalação está funcionando corretamente
"""

import sys
import traceback
from pathlib import Path


def test_imports():
    """Testa se todas as dependências podem ser importadas"""
    print("🔍 Testando importações...")
    
    required_modules = [
        ("asyncio", "Biblioteca padrão Python"),
        ("typing", "Biblioteca padrão Python"),
        ("dataclasses", "Biblioteca padrão Python"),
        ("datetime", "Biblioteca padrão Python"),
        ("logging", "Biblioteca padrão Python"),
        ("pydantic", "Validação de dados"),
        ("asyncio_mqtt", "Cliente MQTT assíncrono"),
        ("dataclasses_json", "Serialização JSON"),
        ("structlog", "Logging estruturado"),
        ("prometheus_client", "Métricas Prometheus"),
    ]
    
    failed_imports = []
    
    for module_name, description in required_modules:
        try:
            __import__(module_name)
            print(f"✅ {module_name} - {description}")
        except ImportError as e:
            print(f"❌ {module_name} - FALHOU: {e}")
            failed_imports.append(module_name)
    
    return len(failed_imports) == 0, failed_imports


def test_project_structure():
    """Verifica se a estrutura do projeto está correta"""
    print("\n🔍 Verificando estrutura do projeto...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        "src/core/hybrid_ai_orchestrator.py",
        "src/agents/base_agent.py",
        "src/agents/ana_beatriz_costa.py",
        "src/agents/carlos_eduardo_santos.py",
        "src/agents/sofia_oliveira.py",
        "src/agents/gabriel_mendes.py",
        "src/agents/isabella_santos.py",
        "src/agents/lucas_pereira.py",
        "src/agents/mariana_rodrigues.py",
        "src/agents/pedro_henrique_almeida.py",
        "src/communication/collaboration_framework.py",
        "src/utils/requirement_analyzer.py",
        "src/utils/response_synthesizer.py",
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - AUSENTE")
            missing_files.append(file_path)
    
    return len(missing_files) == 0, missing_files


def test_agent_imports():
    """Testa se os agentes podem ser importados"""
    print("\n🔍 Testando importação dos agentes...")
    
    try:
        sys.path.append(str(Path.cwd()))
        
        from src.agents.ana_beatriz_costa import AnaBeatrizCosta
        from src.agents.carlos_eduardo_santos import CarlosEduardoSantos
        from src.agents.sofia_oliveira import SofiaOliveira
        from src.agents.gabriel_mendes import GabrielMendes
        from src.agents.isabella_santos import IsabellaSantos
        from src.agents.lucas_pereira import LucasPereira
        from src.agents.mariana_rodrigues import MarianaRodrigues
        from src.agents.pedro_henrique_almeida import PedroHenriqueAlmeida
        
        print("✅ Todos os agentes importados com sucesso")
        return True, []
        
    except Exception as e:
        print(f"❌ Erro ao importar agentes: {e}")
        traceback.print_exc()
        return False, [str(e)]


def test_core_system():
    """Testa se o sistema principal pode ser importado"""
    print("\n🔍 Testando sistema principal...")
    
    try:
        sys.path.append(str(Path.cwd()))
        
        from src.core.hybrid_ai_orchestrator import HybridAIOrchestrator
        from src.communication.collaboration_framework import CollaborationFramework
        from src.utils.requirement_analyzer import RequirementAnalyzer
        from src.utils.response_synthesizer import ResponseSynthesizer
        
        print("✅ Sistema principal importado com sucesso")
        return True, []
        
    except Exception as e:
        print(f"❌ Erro ao importar sistema principal: {e}")
        traceback.print_exc()
        return False, [str(e)]


def test_agent_instantiation():
    """Testa se os agentes podem ser instanciados"""
    print("\n🔍 Testando instanciação dos agentes...")
    
    try:
        sys.path.append(str(Path.cwd()))
        
        from src.agents.ana_beatriz_costa import AnaBeatrizCosta
        from src.agents.carlos_eduardo_santos import CarlosEduardoSantos
        
        # Testa instanciação de alguns agentes
        cto = AnaBeatrizCosta()
        architect = CarlosEduardoSantos()
        
        print(f"✅ CTO: {cto.profile.name}")
        print(f"✅ Arquiteto: {architect.profile.name}")
        
        return True, []
        
    except Exception as e:
        print(f"❌ Erro ao instanciar agentes: {e}")
        traceback.print_exc()
        return False, [str(e)]


def main():
    """Função principal de teste"""
    print("🚀 CWB Hub - Teste de Instalação")
    print("=" * 40)
    
    all_tests_passed = True
    all_errors = []
    
    # Teste 1: Importações
    success, errors = test_imports()
    if not success:
        all_tests_passed = False
        all_errors.extend(errors)
    
    # Teste 2: Estrutura do projeto
    success, errors = test_project_structure()
    if not success:
        all_tests_passed = False
        all_errors.extend(errors)
    
    # Teste 3: Importação dos agentes
    success, errors = test_agent_imports()
    if not success:
        all_tests_passed = False
        all_errors.extend(errors)
    
    # Teste 4: Sistema principal
    success, errors = test_core_system()
    if not success:
        all_tests_passed = False
        all_errors.extend(errors)
    
    # Teste 5: Instanciação dos agentes
    success, errors = test_agent_instantiation()
    if not success:
        all_tests_passed = False
        all_errors.extend(errors)
    
    # Resultado final
    print("\n" + "=" * 40)
    if all_tests_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema CWB Hub está pronto para uso")
        print("\nPara executar o sistema:")
        print("python main.py")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print(f"Erros encontrados: {len(all_errors)}")
        for error in all_errors:
            print(f"  - {error}")
        print("\nExecute: python install_dependencies.py")
    
    return all_tests_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)