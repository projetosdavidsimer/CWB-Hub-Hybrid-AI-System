#!/usr/bin/env python3
"""
Teste do sistema de persistência CWB Hub
"""
from database.connection import test_connection, health_check
from database.models import populate_initial_data
from database.connection import engine

def main():
    print("🧪 TESTE DO SISTEMA DE PERSISTÊNCIA CWB HUB")
    print("=" * 50)
    
    # Teste 1: Conexão
    print("1. Testando conexão...")
    if test_connection():
        print("✅ Conexão OK")
    else:
        print("❌ Conexão falhou")
        return False
    
    # Teste 2: Health check
    print("\n2. Health check...")
    health = health_check()
    if health['status'] == 'healthy':
        print("✅ Health check OK")
        print(f"   PostgreSQL: {health['database_version']}")
        print(f"   Database: {health['current_database']}")
        print(f"   User: {health['current_user']}")
    else:
        print("❌ Health check falhou")
        return False
    
    # Teste 3: Dados iniciais
    print("\n3. Populando dados iniciais...")
    try:
        populate_initial_data(engine)
        print("✅ Dados iniciais OK")
    except Exception as e:
        print(f"❌ Erro nos dados iniciais: {e}")
        return False
    
    print("\n🎉 SISTEMA DE PERSISTÊNCIA PRONTO!")
    print("🚀 A equipe pode trabalhar com persistência completa!")
    print("\n📋 Tabelas criadas:")
    print("   - users (usuários)")
    print("   - projects (projetos)")
    print("   - sessions (sessões)")
    print("   - agents (agentes)")
    print("   - collaborations (colaborações)")
    print("   - audit_logs (logs de auditoria)")
    print("   - feedbacks (feedbacks)")
    print("   - system_metrics (métricas do sistema)")
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ TODOS OS TESTES PASSARAM!")
        print("🔥 SISTEMA PRONTO PARA A EQUIPE DE AGENTES!")
    else:
        print("\n❌ Alguns testes falharam.")