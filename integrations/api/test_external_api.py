#!/usr/bin/env python3
"""
CWB Hub External API Tests - Task 16
Testes para a API externa de integração
Implementado pela Equipe CWB Hub
"""

import asyncio
import pytest
import httpx
import json
import time
from datetime import datetime
from typing import Dict, Any

# Configurações de teste
API_BASE_URL = "http://localhost:8002/external/v1"
TEST_API_KEY = None  # Será criado durante os testes

class TestExternalAPI:
    """Testes para a API externa do CWB Hub"""
    
    def __init__(self):
        self.client = httpx.AsyncClient(base_url=API_BASE_URL)
        self.api_key = None
        self.test_project_id = None
    
    async def setup(self):
        """Configuração inicial dos testes"""
        print("🔧 Configurando testes da API externa...")
        
        # Criar API key para testes
        from api_key_manager import create_api_key
        
        key_data = create_api_key(
            name="Test External API",
            description="Chave para testes da API externa",
            permissions=["read", "write", "export", "import", "webhooks"],
            created_by="test_system",
            rate_limit_per_hour=1000
        )
        
        self.api_key = key_data["api_key"]
        print(f"✅ API key de teste criada: {key_data['key_id']}")
    
    async def teardown(self):
        """Limpeza após os testes"""
        await self.client.aclose()
        print("🧹 Testes finalizados")
    
    def get_headers(self) -> Dict[str, str]:
        """Obter headers com autenticação"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def test_health_check(self):
        """Testar health check"""
        print("\n🏥 Testando health check...")
        
        response = await self.client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data
        assert "performance" in data
        
        print("✅ Health check funcionando")
    
    async def test_api_info(self):
        """Testar endpoint de informações da API"""
        print("\n📋 Testando informações da API...")
        
        response = await self.client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "CWB Hub External API"
        assert data["version"] == "1.0.0"
        assert "features" in data
        assert "documentation" in data
        
        print("✅ Informações da API OK")
    
    async def test_create_project(self):
        """Testar criação de projeto"""
        print("\n🚀 Testando criação de projeto...")
        
        project_data = {\n            \"title\": \"App de Gestão de Tarefas\",\n            \"description\": \"Aplicativo mobile para gestão de tarefas pessoais e profissionais com sincronização em nuvem\",\n            \"requirements\": [\n                \"Interface intuitiva e responsiva\",\n                \"Sincronização em tempo real\",\n                \"Notificações push\",\n                \"Modo offline\",\n                \"Relatórios de produtividade\"\n            ],\n            \"constraints\": [\n                \"Orçamento limitado a R$ 25.000\",\n                \"Prazo de 3 meses\",\n                \"Compatibilidade com iOS e Android\"\n            ],\n            \"priority\": \"high\",\n            \"budget_range\": \"R$ 20.000 - R$ 25.000\",\n            \"timeline\": \"3 meses\",\n            \"technology_preferences\": [\"React Native\", \"Firebase\", \"Node.js\"],\n            \"target_audience\": \"Profissionais e estudantes\",\n            \"business_goals\": [\n                \"Aumentar produtividade dos usuários\",\n                \"Capturar 1000 usuários em 6 meses\",\n                \"Gerar receita recorrente\"\n            ],\n            \"external_id\": \"test_project_001\",\n            \"metadata\": {\n                \"test_case\": \"create_project\",\n                \"created_by\": \"automated_test\"\n            }\n        }\n        \n        response = await self.client.post(\n            \"/projects\",\n            json=project_data,\n            headers=self.get_headers()\n        )\n        \n        assert response.status_code == 200\n        data = response.json()\n        \n        assert \"project_id\" in data\n        assert \"session_id\" in data\n        assert data[\"title\"] == project_data[\"title\"]\n        assert data[\"status\"] == \"completed\"\n        assert data[\"confidence_score\"] > 90\n        assert len(data[\"agents_involved\"]) > 0\n        assert \"analysis\" in data\n        assert len(data[\"analysis\"]) > 100  # Análise substancial\n        \n        self.test_project_id = data[\"project_id\"]\n        \n        print(f\"✅ Projeto criado: {self.test_project_id}\")\n        print(f\"   Confiança: {data['confidence_score']}%\")\n        print(f\"   Agentes: {len(data['agents_involved'])}\")\n    \n    async def test_get_project_status(self):\n        \"\"\"Testar obtenção de status do projeto\"\"\"\n        print(\"\\n📊 Testando status do projeto...\")\n        \n        if not self.test_project_id:\n            await self.test_create_project()\n        \n        response = await self.client.get(\n            f\"/projects/{self.test_project_id}/status\",\n            headers=self.get_headers()\n        )\n        \n        assert response.status_code == 200\n        data = response.json()\n        \n        assert data[\"project_id\"] == self.test_project_id\n        assert \"session_id\" in data\n        assert \"status\" in data\n        assert \"progress_percentage\" in data\n        assert \"current_phase\" in data\n        \n        print(f\"✅ Status obtido: {data['status']}\")\n        print(f\"   Progresso: {data['progress_percentage']}%\")\n        print(f\"   Fase: {data['current_phase']}\")\n    \n    async def test_iterate_project(self):\n        \"\"\"Testar iteração de projeto\"\"\"\n        print(\"\\n🔄 Testando iteração do projeto...\")\n        \n        if not self.test_project_id:\n            await self.test_create_project()\n        \n        iteration_data = {\n            \"feedback\": \"Gostei da proposta, mas preciso focar mais na experiência do usuário. Adicione funcionalidades de gamificação para aumentar o engajamento.\",\n            \"focus_areas\": [\"UX/UI\", \"Gamificação\", \"Engajamento\"],\n            \"additional_requirements\": [\n                \"Sistema de pontuação\",\n                \"Badges de conquistas\",\n                \"Ranking entre amigos\"\n            ],\n            \"metadata\": {\n                \"iteration_type\": \"ux_enhancement\",\n                \"requested_by\": \"product_owner\"\n            }\n        }\n        \n        response = await self.client.post(\n            f\"/projects/{self.test_project_id}/iterate\",\n            json=iteration_data,\n            headers=self.get_headers()\n        )\n        \n        assert response.status_code == 200\n        data = response.json()\n        \n        assert data[\"project_id\"] == self.test_project_id\n        assert data[\"iteration_number\"] >= 1\n        assert \"refined_analysis\" in data\n        assert data[\"confidence_improvement\"] > 0\n        assert \"changes_summary\" in data\n        \n        print(f\"✅ Iteração concluída: #{data['iteration_number']}\")\n        print(f\"   Melhoria: +{data['confidence_improvement']}%\")\n    \n    async def test_list_projects(self):\n        \"\"\"Testar listagem de projetos\"\"\"\n        print(\"\\n📋 Testando listagem de projetos...\")\n        \n        response = await self.client.get(\n            \"/projects?page=1&page_size=10\",\n            headers=self.get_headers()\n        )\n        \n        assert response.status_code == 200\n        data = response.json()\n        \n        assert \"items\" in data\n        assert \"total_items\" in data\n        assert \"total_pages\" in data\n        assert \"current_page\" in data\n        assert \"has_next\" in data\n        assert \"has_previous\" in data\n        \n        print(f\"✅ Projetos listados: {data['total_items']} total\")\n        print(f\"   Página: {data['current_page']}/{data['total_pages']}\")\n    \n    async def test_export_data(self):\n        \"\"\"Testar export de dados\"\"\"\n        print(\"\\n📤 Testando export de dados...\")\n        \n        export_data = {\n            \"format\": \"json\",\n            \"include_metadata\": True,\n            \"include_analytics\": True,\n            \"filters\": {\n                \"test_export\": True\n            }\n        }\n        \n        response = await self.client.post(\n            \"/export\",\n            json=export_data,\n            headers=self.get_headers()\n        )\n        \n        assert response.status_code == 200\n        data = response.json()\n        \n        assert \"export_id\" in data\n        assert data[\"format\"] == \"json\"\n        assert \"file_url\" in data\n        assert \"file_size_bytes\" in data\n        assert \"records_count\" in data\n        assert \"created_at\" in data\n        \n        print(f\"✅ Export criado: {data['export_id']}\")\n        print(f\"   Registros: {data['records_count']}\")\n        print(f\"   Tamanho: {data['file_size_bytes']} bytes\")\n    \n    async def test_import_data(self):\n        \"\"\"Testar import de dados\"\"\"\n        print(\"\\n📥 Testando import de dados...\")\n        \n        import_data = {\n            \"format\": \"json\",\n            \"data\": [\n                {\n                    \"title\": \"Projeto Importado 1\",\n                    \"description\": \"Descrição do projeto importado para teste\",\n                    \"requirements\": [\"Requisito 1\", \"Requisito 2\"],\n                    \"status\": \"imported\",\n                    \"external_id\": \"import_test_001\"\n                },\n                {\n                    \"title\": \"Projeto Importado 2\",\n                    \"description\": \"Outro projeto importado para teste\",\n                    \"requirements\": [\"Requisito A\", \"Requisito B\"],\n                    \"status\": \"imported\",\n                    \"external_id\": \"import_test_002\"\n                }\n            ],\n            \"validate_only\": False,\n            \"overwrite_existing\": False,\n            \"metadata\": {\n                \"import_source\": \"automated_test\",\n                \"batch_id\": \"test_batch_001\"\n            }\n        }\n        \n        response = await self.client.post(\n            \"/import\",\n            json=import_data,\n            headers=self.get_headers()\n        )\n        \n        assert response.status_code == 200\n        data = response.json()\n        \n        assert \"import_id\" in data\n        assert data[\"status\"] in [\"completed\", \"completed_with_errors\"]\n        assert data[\"records_processed\"] == 2\n        assert data[\"records_imported\"] >= 0\n        assert \"validation_errors\" in data\n        assert \"warnings\" in data\n        \n        print(f\"✅ Import processado: {data['import_id']}\")\n        print(f\"   Processados: {data['records_processed']}\")\n        print(f\"   Importados: {data['records_imported']}\")\n        print(f\"   Erros: {data['records_failed']}\")\n    \n    async def test_webhooks(self):\n        \"\"\"Testar sistema de webhooks\"\"\"\n        print(\"\\n🔗 Testando webhooks...\")\n        \n        # Criar webhook\n        webhook_data = {\n            \"url\": \"https://httpbin.org/post\",\n            \"events\": [\"project.created\", \"project.completed\"],\n            \"secret\": \"test_webhook_secret_123\",\n            \"active\": True,\n            \"retry_count\": 3,\n            \"timeout_seconds\": 30,\n            \"metadata\": {\n                \"test_webhook\": True,\n                \"environment\": \"test\"\n            }\n        }\n        \n        response = await self.client.post(\n            \"/webhooks\",\n            json=webhook_data,\n            headers=self.get_headers()\n        )\n        \n        assert response.status_code == 200\n        data = response.json()\n        \n        assert \"webhook_id\" in data\n        assert data[\"url\"] == webhook_data[\"url\"]\n        assert data[\"events\"] == webhook_data[\"events\"]\n        assert data[\"active\"] == True\n        \n        webhook_id = data[\"webhook_id\"]\n        print(f\"✅ Webhook criado: {webhook_id}\")\n        \n        # Listar webhooks\n        response = await self.client.get(\n            \"/webhooks\",\n            headers=self.get_headers()\n        )\n        \n        assert response.status_code == 200\n        webhooks = response.json()\n        \n        assert isinstance(webhooks, list)\n        assert len(webhooks) >= 1\n        \n        print(f\"✅ Webhooks listados: {len(webhooks)}\")\n        \n        # Remover webhook\n        response = await self.client.delete(\n            f\"/webhooks/{webhook_id}\",\n            headers=self.get_headers()\n        )\n        \n        assert response.status_code == 200\n        print(f\"✅ Webhook removido: {webhook_id}\")\n    \n    async def test_analytics(self):\n        \"\"\"Testar analytics\"\"\"\n        print(\"\\n📈 Testando analytics...\")\n        \n        response = await self.client.get(\n            \"/analytics\",\n            headers=self.get_headers()\n        )\n        \n        assert response.status_code == 200\n        data = response.json()\n        \n        assert \"period_start\" in data\n        assert \"period_end\" in data\n        assert \"total_projects\" in data\n        assert \"completed_projects\" in data\n        assert \"failed_projects\" in data\n        assert \"average_completion_time\" in data\n        assert \"average_confidence_score\" in data\n        assert \"top_technologies\" in data\n        assert \"agent_performance\" in data\n        assert \"api_usage_stats\" in data\n        \n        print(f\"✅ Analytics gerado\")\n        print(f\"   Projetos: {data['total_projects']}\")\n        print(f\"   Concluídos: {data['completed_projects']}\")\n        print(f\"   Confiança média: {data['average_confidence_score']:.1f}%\")\n    \n    async def test_authentication_errors(self):\n        \"\"\"Testar erros de autenticação\"\"\"\n        print(\"\\n🔒 Testando erros de autenticação...\")\n        \n        # Sem API key\n        response = await self.client.get(\"/projects\")\n        assert response.status_code == 401\n        \n        # API key inválida\n        invalid_headers = {\"Authorization\": \"Bearer invalid_key_123\"}\n        response = await self.client.get(\"/projects\", headers=invalid_headers)\n        assert response.status_code == 401\n        \n        print(\"✅ Erros de autenticação funcionando corretamente\")\n    \n    async def run_all_tests(self):\n        \"\"\"Executar todos os testes\"\"\"\n        print(\"🧪 INICIANDO TESTES DA API EXTERNA\")\n        print(\"=\" * 50)\n        \n        try:\n            await self.setup()\n            \n            # Testes básicos\n            await self.test_health_check()\n            await self.test_api_info()\n            await self.test_authentication_errors()\n            \n            # Testes de projetos\n            await self.test_create_project()\n            await self.test_get_project_status()\n            await self.test_iterate_project()\n            await self.test_list_projects()\n            \n            # Testes de dados\n            await self.test_export_data()\n            await self.test_import_data()\n            \n            # Testes de webhooks\n            await self.test_webhooks()\n            \n            # Testes de analytics\n            await self.test_analytics()\n            \n            print(\"\\n🎉 TODOS OS TESTES PASSARAM!\")\n            print(\"=\" * 50)\n            \n        except Exception as e:\n            print(f\"\\n❌ TESTE FALHOU: {e}\")\n            raise\n        finally:\n            await self.teardown()\n\nasync def main():\n    \"\"\"Função principal para executar os testes\"\"\"\n    tester = TestExternalAPI()\n    await tester.run_all_tests()\n\nif __name__ == \"__main__\":\n    print(\"🚀 CWB Hub External API - Test Suite\")\n    print(\"Certifique-se de que a API está rodando em http://localhost:8002\")\n    print()\n    \n    try:\n        asyncio.run(main())\n    except KeyboardInterrupt:\n        print(\"\\n⏹️ Testes interrompidos pelo usuário\")\n    except Exception as e:\n        print(f\"\\n💥 Erro nos testes: {e}\")\n        exit(1)