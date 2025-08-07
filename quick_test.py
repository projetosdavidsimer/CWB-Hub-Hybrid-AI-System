#!/usr/bin/env python3
"""
Script rápido para executar testes essenciais do CWB Hub
Melhoria #5 - Testes Automatizados Completos
"""

import subprocess
import sys
import os

def run_test(test_file, description):
    """Executa um teste específico"""
    print(f"\n🧪 {description}")
    print("-" * 50)
    
    cmd = ["python", "-m", "pytest", test_file, "-v", "--tb=short"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ PASSOU")
        # Contar testes passados
        lines = result.stdout.split('\n')
        for line in lines:
            if "passed" in line and "in" in line:
                print(f"   {line.strip()}")
        return True
    else:
        print("❌ FALHOU")
        print(f"   Erro: {result.stderr}")
        return False

def main():
    """Função principal"""
    print("🎯 TESTES RÁPIDOS CWB HUB")
    print("=" * 50)
    print("Melhoria #5 - Testes Automatizados Completos")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("tests"):
        print("❌ Diretório 'tests' não encontrado!")
        sys.exit(1)
    
    tests = [
        ("tests/test_basic.py", "Testes Básicos do Sistema"),
        # Adicionar outros testes conforme necessário
    ]
    
    passed = 0
    total = len(tests)
    
    for test_file, description in tests:
        if os.path.exists(test_file):
            if run_test(test_file, description):
                passed += 1
        else:
            print(f"\n⚠️  {description}")
            print(f"   Arquivo não encontrado: {test_file}")
    
    print(f"\n🎯 RESULTADO FINAL:")
    print(f"   Passou: {passed}/{total}")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema de testes funcionando corretamente!")
    else:
        print("⚠️  Alguns testes falharam")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)