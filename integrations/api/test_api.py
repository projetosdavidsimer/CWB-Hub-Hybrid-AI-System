#!/usr/bin/env python3
"""
Teste da CWB Hub Public API
Melhoria #3 - Integração com APIs Externas
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any

# Configuração da API
API_BASE_URL = "http://localhost:8000"

class CWBHubAPITester:
    """Testador da API CWB Hub"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.api_key = None
        self.token = None
        self.session_id = None
    
    async def test_health_check(self):
        """Testa o health check da API"""
        print("🔍 Testando health check...")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check OK: {data['status']}")
                print(f"   CWB Hub: {data['cwb_hub_status']}")
                print(f"   Redis: {data['redis_status']}")
                return True
            else:
                print(f"❌ Health check falhou: {response.status_code}")
                return False
    
    async def test_api_key_creation(self):
        """Testa a criação de API key"""
        print("\n🔑 Testando criação de API key...")
        
        request_data = {
            "name": "CWB Hub Test Client",
            "email": "test@cwbhub.com",
            "description": "Cliente de teste para validação da API"
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/auth/api-key",
                json=request_data
            )
            
            if response.status_code == 200:
                data = response.json()
                self.api_key = data["api_key"]
                self.token = data["token"]
                
                print(f"✅ API key criada: {self.api_key[:16]}...")
                print(f"   Token expires in: {data['expires_in']} seconds")
                print(f"   Rate limit: {data['usage']['rate_limit']}")
                return True
            else:
                print(f"❌ Falha ao criar API key: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    
    async def test_project_analysis(self):
        """Testa a análise de projeto"""
        print("\n🧠 Testando análise de projeto...")
        
        if not self.token:
            print("❌ Token não disponível")
            return False
        
        request_data = {
            "request": "Preciso desenvolver um sistema de e-commerce completo com as seguintes funcionalidades: catálogo de produtos, carrinho de compras, sistema de pagamento, gestão de pedidos, painel administrativo e app mobile. O sistema deve ser escalável para suportar milhares de usuários simultâneos.",
            "context": "Startup de tecnologia com orçamento moderado, prazo de 6 meses para MVP, equipe de 5 desenvolvedores",
            "priority": "high"
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("   Enviando solicitação para a equipe CWB Hub...")
            start_time = time.time()
            
            response = await client.post(
                f"{self.base_url}/analyze",
                json=request_data,
                headers=headers
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                self.session_id = data["session_id"]
                
                print(f"✅ Análise concluída em {processing_time:.2f}s")
                print(f"   Session ID: {self.session_id}")
                print(f"   Confiança: {data['confidence']*100:.1f}%")
                print(f"   Agentes envolvidos: {len(data['agents_involved'])}")
                print(f"   Colaborações: {data['collaboration_stats']['total_collaborations']}")
                
                # Mostrar parte da análise
                analysis = data["analysis"]
                if len(analysis) > 500:
                    print(f"   Análise (preview): {analysis[:500]}...")
                else:
                    print(f"   Análise: {analysis}")
                
                return True
            else:
                print(f"❌ Falha na análise: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    
    async def test_solution_iteration(self):
        """Testa a iteração de solução"""
        print("\n🔄 Testando iteração de solução...")
        
        if not self.token or not self.session_id:
            print("❌ Token ou session_id não disponível")
            return False
        
        feedback = """
        Excelente análise da equipe! Tenho algumas considerações importantes:
        
        ORÇAMENTO E CRONOGRAMA:
        - O orçamento é mais limitado que o esperado
        - Precisamos focar no MVP essencial primeiro
        - Prazo de 4 meses seria ideal
        
        PRIORIDADES TÉCNICAS:
        - E-commerce web é prioridade máxima
        - App mobile pode vir na segunda fase
        - Integração com pagamento via PIX é essencial
        - Sistema deve funcionar bem no Brasil
        
        EQUIPE:
        - Temos 3 desenvolvedores full-stack
        - 1 designer UX/UI
        - 1 DevOps/infra
        
        Podem ajustar a proposta considerando essas limitações?
        """
        
        request_data = {
            "session_id": self.session_id,
            "feedback": feedback
        }
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            print("   Enviando feedback para refinamento...")
            start_time = time.time()
            
            response = await client.post(
                f"{self.base_url}/iterate/{self.session_id}",
                json=request_data,
                headers=headers
            )
            
            processing_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Iteração concluída em {processing_time:.2f}s")
                print(f"   Iterações: {data['iteration_count']}")
                print(f"   Colaborações: {data['collaboration_stats']['total_collaborations']}")
                
                # Mostrar parte da análise refinada
                refined_analysis = data["refined_analysis"]
                if len(refined_analysis) > 500:
                    print(f"   Análise refinada (preview): {refined_analysis[:500]}...")
                else:
                    print(f"   Análise refinada: {refined_analysis}")
                
                return True
            else:
                print(f"❌ Falha na iteração: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    
    async def test_session_status(self):
        """Testa a consulta de status da sessão"""
        print("\n📊 Testando status da sessão...")
        
        if not self.token or not self.session_id:
            print("❌ Token ou session_id não disponível")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/status/{self.session_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Status obtido com sucesso")
                print(f"   Session ID: {data['session_id']}")
                print(f"   Status: {data['status']}")
                print(f"   Criada em: {data['created_at']}")
                print(f"   Iterações: {data['iterations']}")
                print(f"   Tem solução final: {data['final_solution'] is not None}")
                
                return True
            else:
                print(f"❌ Falha ao obter status: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    
    async def test_list_sessions(self):
        """Testa a listagem de sessões"""
        print("\n📋 Testando listagem de sessões...")
        
        if not self.token:
            print("❌ Token não disponível")
            return False
        
        headers = {"Authorization": f"Bearer {self.token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/sessions",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ Sessões listadas com sucesso")
                print(f"   Total de sessões: {data['total_sessions']}")
                
                for session in data['sessions']:
                    print(f"   - {session['session_id']}: {session['status']} ({session['iterations']} iterações)")
                
                return True
            else:
                print(f"❌ Falha ao listar sessões: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
    
    async def run_all_tests(self):
        """Executa todos os testes"""
        print("🧪 INICIANDO TESTES DA CWB HUB PUBLIC API")
        print("=" * 60)
        
        tests = [
            ("Health Check", self.test_health_check),
            ("API Key Creation", self.test_api_key_creation),
            ("Project Analysis", self.test_project_analysis),
            ("Solution Iteration", self.test_solution_iteration),
            ("Session Status", self.test_session_status),
            ("List Sessions", self.test_list_sessions),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ Erro no teste {test_name}: {e}")
                results.append((test_name, False))
        
        # Resumo dos resultados
        print("\n" + "=" * 60)
        print("📊 RESUMO DOS TESTES")
        print("=" * 60)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ PASSOU" if result else "❌ FALHOU"
            print(f"{status} - {test_name}")
        
        print(f"\n🎯 RESULTADO FINAL: {passed}/{total} testes passaram ({passed/total*100:.1f}%)")
        
        if passed == total:
            print("🎉 TODOS OS TESTES PASSARAM! API está funcionando perfeitamente!")
        else:
            print("⚠️ Alguns testes falharam. Verifique os logs acima.")
        
        return passed == total

async def main():
    """Função principal"""
    print("🚀 CWB Hub Public API - Test Suite")
    print("Melhoria #3 - Integração com APIs Externas")
    print()
    
    # Verificar se a API está rodando
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE_URL}/")
            if response.status_code != 200:
                print(f"❌ API não está respondendo em {API_BASE_URL}")
                print("   Certifique-se de que a API está rodando:")
                print("   cd integrations/api && python main.py")
                return
    except Exception as e:
        print(f"❌ Não foi possível conectar à API em {API_BASE_URL}")
        print(f"   Erro: {e}")
        print("   Certifique-se de que a API está rodando:")
        print("   cd integrations/api && python main.py")
        return
    
    # Executar testes
    tester = CWBHubAPITester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 API CWB Hub está pronta para uso!")
        print("📚 Documentação: http://localhost:8000/docs")
    else:
        print("\n⚠️ Alguns testes falharam. Verifique a implementação.")

if __name__ == "__main__":
    asyncio.run(main())