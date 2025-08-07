#!/usr/bin/env python3
"""
Script para executar todos os testes do CWB Hub
Melhoria #5 - Testes Automatizados Completos
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def print_header(title):
    """Imprime cabeçalho formatado"""
    print("\n" + "="*70)
    print(f"🧪 {title}")
    print("="*70)

def print_section(title):
    """Imprime seção formatada"""
    print(f"\n📋 {title}")
    print("-"*50)

def run_command(command, description):
    """Executa comando e retorna resultado"""
    print(f"▶️  {description}")
    print(f"   Comando: {' '.join(command)}")
    
    start_time = time.time()
    result = subprocess.run(command, capture_output=True, text=True)
    end_time = time.time()
    
    duration = end_time - start_time
    
    if result.returncode == 0:
        print(f"   ✅ Sucesso ({duration:.2f}s)")
        return True, result.stdout, result.stderr
    else:
        print(f"   ❌ Falhou ({duration:.2f}s)")
        print(f"   Erro: {result.stderr}")
        return False, result.stdout, result.stderr

def check_dependencies():
    """Verifica se dependências estão instaladas"""
    print_section("Verificando Dependências")
    
    required_packages = [
        "pytest",
        "pytest-asyncio", 
        "pytest-cov",
        "pytest-timeout",
        # "pytest-xdist"  # Opcional para execução paralela
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (não instalado)")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Pacotes faltando: {', '.join(missing_packages)}")
        print("   Para instalar: pip install " + " ".join(missing_packages))
        return False
    
    return True

def run_unit_tests():
    """Executa testes unitários"""
    print_section("Testes Unitários")
    
    commands = [
        (["python", "-m", "pytest", "tests/test_agents.py", "-v"], "Testes dos Agentes"),
        (["python", "-m", "pytest", "tests/test_orchestrator.py", "-v"], "Testes do Orquestrador"),
    ]
    
    results = []
    for command, description in commands:
        success, stdout, stderr = run_command(command, description)
        results.append((description, success, stdout, stderr))
    
    return results

def run_integration_tests():
    """Executa testes de integração"""
    print_section("Testes de Integração")
    
    commands = [
        (["python", "-m", "pytest", "tests/test_persistence.py", "-v"], "Testes de Persistência"),
    ]
    
    results = []
    for command, description in commands:
        success, stdout, stderr = run_command(command, description)
        results.append((description, success, stdout, stderr))
    
    return results

def run_performance_tests():
    """Executa testes de performance"""
    print_section("Testes de Performance")
    
    commands = [
        (["python", "-m", "pytest", "tests/", "-m", "performance", "-v"], "Testes de Performance"),
    ]
    
    results = []
    for command, description in commands:
        success, stdout, stderr = run_command(command, description)
        results.append((description, success, stdout, stderr))
    
    return results

def run_coverage_tests():
    """Executa testes com cobertura"""
    print_section("Análise de Cobertura")
    
    commands = [
        (["python", "-m", "pytest", "tests/", "--cov=src", "--cov=persistence", 
          "--cov-report=html", "--cov-report=term-missing"], "Cobertura de Código"),
    ]
    
    results = []
    for command, description in commands:
        success, stdout, stderr = run_command(command, description)
        results.append((description, success, stdout, stderr))
    
    return results

def run_all_tests():
    """Executa todos os testes"""
    print_section("Todos os Testes")
    
    commands = [
        (["python", "-m", "pytest", "tests/", "-v", "--tb=short"], "Execução Completa"),
    ]
    
    results = []
    for command, description in commands:
        success, stdout, stderr = run_command(command, description)
        results.append((description, success, stdout, stderr))
    
    return results

def generate_report(all_results):
    """Gera relatório final"""
    print_header("RELATÓRIO FINAL DE TESTES")
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for category, results in all_results.items():
        print(f"\n📊 {category}:")
        
        for description, success, stdout, stderr in results:
            status = "✅ PASSOU" if success else "❌ FALHOU"
            print(f"   {status} - {description}")
            
            if success:
                passed_tests += 1
            else:
                failed_tests += 1
            total_tests += 1
    
    print(f"\n🎯 RESUMO GERAL:")
    print(f"   Total de testes: {total_tests}")
    print(f"   Passou: {passed_tests}")
    print(f"   Falhou: {failed_tests}")
    
    if failed_tests == 0:
        print(f"   Taxa de sucesso: 100% 🎉")
        print(f"\n✅ TODOS OS TESTES PASSARAM!")
        print(f"🚀 Sistema pronto para produção!")
    else:
        success_rate = (passed_tests / total_tests) * 100
        print(f"   Taxa de sucesso: {success_rate:.1f}%")
        print(f"\n⚠️  {failed_tests} teste(s) falharam")
        print(f"🔧 Correções necessárias antes do deploy")
    
    return failed_tests == 0

def main():
    """Função principal"""
    print_header("SISTEMA DE TESTES AUTOMATIZADOS CWB HUB")
    print("Melhoria #5 - Testes Automatizados Completos")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("tests"):
        print("❌ Diretório 'tests' não encontrado!")
        print("   Execute este script a partir do diretório raiz do projeto")
        sys.exit(1)
    
    # Verificar dependências
    if not check_dependencies():
        print("\n❌ Dependências faltando. Instale os pacotes necessários primeiro.")
        sys.exit(1)
    
    # Executar diferentes tipos de teste
    all_results = {}
    
    try:
        # Testes unitários
        all_results["Testes Unitários"] = run_unit_tests()
        
        # Testes de integração
        all_results["Testes de Integração"] = run_integration_tests()
        
        # Testes de performance
        all_results["Testes de Performance"] = run_performance_tests()
        
        # Análise de cobertura (opcional)
        try:
            all_results["Análise de Cobertura"] = run_coverage_tests()
        except Exception as e:
            print(f"⚠️  Análise de cobertura falhou: {e}")
        
        # Execução completa
        all_results["Execução Completa"] = run_all_tests()
        
    except KeyboardInterrupt:
        print("\n⚠️  Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro durante execução dos testes: {e}")
        sys.exit(1)
    
    # Gerar relatório final
    success = generate_report(all_results)
    
    # Código de saída
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()