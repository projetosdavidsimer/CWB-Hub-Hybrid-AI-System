# CWB Hub External API - Task 16

## 🚀 API REST para Integração com Sistemas Externos

A **CWB Hub External API** é uma interface robusta e segura que permite a sistemas externos integrarem-se com o ecossistema de IA híbrida colaborativa do CWB Hub. Esta API foi desenvolvida pela equipe de 8 especialistas sênior para fornecer acesso programático às capacidades de análise e colaboração do sistema.

## 📋 Características Principais

### 🔐 Autenticação e Segurança
- **API Keys**: Sistema de chaves únicas por parceiro/sistema
- **Permissões Granulares**: Controle fino de acesso (read, write, admin, export, import, webhooks)
- **Rate Limiting**: Limites configuráveis por API key
- **JWT Integration**: Compatibilidade com sistema de autenticação existente

### 🎯 Funcionalidades Core
- **Análise de Projetos**: Processamento com 8 especialistas IA
- **Sistema de Iteração**: Refinamento baseado em feedback
- **Export/Import**: Dados em múltiplos formatos (JSON, CSV, XML, PDF)
- **Webhooks**: Notificações em tempo real para eventos
- **Analytics**: Métricas detalhadas de performance e uso

### 🏗️ Arquitetura
- **FastAPI**: Framework moderno e performático
- **Pydantic**: Validação robusta de dados
- **Redis**: Cache e rate limiting
- **Middleware**: Autenticação, logging e monitoramento
- **OpenAPI/Swagger**: Documentação automática

## 🔧 Configuração e Instalação

### Pré-requisitos
```bash
# Python 3.8+
# Redis Server
# CWB Hub Core System
```

### Instalação
```bash
# Instalar dependências
pip install -r integrations/api/requirements.txt

# Configurar variáveis de ambiente
cp integrations/api/.env.example integrations/api/.env

# Inicializar banco de dados (se necessário)
python integrations/api/setup_database.py
```

### Executar API
```bash
# Desenvolvimento
python integrations/api/external_api.py

# Produção
uvicorn integrations.api.external_api:app --host 0.0.0.0 --port 8002
```

## 🔑 Autenticação

### Obter API Key
```python
from integrations.api.api_key_manager import create_api_key

# Criar nova API key
api_key_data = create_api_key(
    name="Minha Integração",
    description="Integração com sistema XYZ",
    permissions=["read", "write", "export"],
    created_by="admin_user",
    rate_limit_per_hour=1000,
    expires_in_days=365
)

print(f"API Key: {api_key_data['api_key']}")
print(f"Key ID: {api_key_data['key_id']}")
```

### Usar API Key
```bash
# Header de autenticação
Authorization: Bearer YOUR_API_KEY_HERE
```

## 📚 Endpoints Principais

### 🏥 Health Check
```http
GET /external/v1/health
```

**Resposta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "uptime_seconds": 86400,
  "services": {
    "cwb_hub_core": "available",
    "webhook_manager": "available",
    "redis": "available"
  },
  "performance": {
    "total_requests": 1250,
    "avg_response_time_ms": 150
  }
}
```

### 🚀 Criar Projeto
```http
POST /external/v1/projects
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Payload:**
```json
{
  "title": "App de Gestão de Tarefas",
  "description": "Aplicativo mobile para gestão de tarefas com sincronização em nuvem",
  "requirements": [
    "Interface intuitiva",
    "Sincronização em tempo real",
    "Notificações push",
    "Modo offline"
  ],
  "constraints": [
    "Orçamento limitado a R$ 25.000",
    "Prazo de 3 meses"
  ],
  "priority": "high",
  "budget_range": "R$ 20.000 - R$ 25.000",
  "timeline": "3 meses",
  "technology_preferences": ["React Native", "Firebase"],
  "target_audience": "Profissionais e estudantes",
  "business_goals": [
    "Aumentar produtividade",
    "Capturar 1000 usuários em 6 meses"
  ],
  "external_id": "project_001",
  "callback_url": "https://meusite.com/webhook",
  "metadata": {
    "department": "TI",
    "priority_level": 1
  }
}
```

**Resposta:**
```json
{
  "project_id": "ext_proj_1705312200_a1b2c3d4",
  "session_id": "ext_sess_ext_proj_1705312200_a1b2c3d4_e5f6g7h8",
  "title": "App de Gestão de Tarefas",
  "status": "completed",
  "analysis": "## Análise Completa do Projeto\n\n### Visão Geral\nO projeto proposto é um aplicativo mobile...",
  "confidence_score": 94.4,
  "estimated_timeline": "2-4 semanas",
  "estimated_budget": "R$ 15.000 - R$ 30.000",
  "recommended_technologies": ["React Native", "Node.js", "PostgreSQL"],
  "risk_assessment": "Baixo risco - projeto bem definido",
  "next_steps": [
    "Definir arquitetura detalhada",
    "Criar protótipos de interface",
    "Configurar ambiente de desenvolvimento"
  ],
  "agents_involved": [
    "ana_beatriz_costa",
    "carlos_eduardo_santos",
    "sofia_oliveira",
    "gabriel_mendes",
    "isabella_santos",
    "lucas_pereira",
    "mariana_rodrigues",
    "pedro_henrique_almeida"
  ],
  "collaboration_stats": {
    "total_interactions": 8,
    "consensus_reached": true,
    "confidence_level": 94.4
  },
  "created_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:32:30Z",
  "external_id": "project_001",
  "metadata": {
    "department": "TI",
    "priority_level": 1,
    "api_key_id": "cwb_1705312000_a1b2c3d4",
    "processing_time_seconds": 150.5
  }
}
```

### 🔄 Iterar Projeto
```http
POST /external/v1/projects/{project_id}/iterate
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Payload:**
```json
{
  "feedback": "Gostei da proposta, mas preciso focar mais na experiência do usuário. Adicione funcionalidades de gamificação.",
  "focus_areas": ["UX/UI", "Gamificação", "Engajamento"],
  "additional_requirements": [
    "Sistema de pontuação",
    "Badges de conquistas",
    "Ranking entre amigos"
  ],
  "metadata": {
    "iteration_type": "ux_enhancement"
  }
}
```

### 📊 Status do Projeto
```http
GET /external/v1/projects/{project_id}/status
Authorization: Bearer YOUR_API_KEY
```

### 📋 Listar Projetos
```http
GET /external/v1/projects?page=1&page_size=20&sort_by=created_at&sort_order=desc
Authorization: Bearer YOUR_API_KEY
```

### 📤 Exportar Dados
```http
POST /external/v1/export
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

**Payload:**
```json
{
  "format": "json",
  "date_from": "2024-01-01T00:00:00Z",
  "date_to": "2024-01-31T23:59:59Z",
  "project_ids": ["proj_001", "proj_002"],
  "include_metadata": true,
  "include_analytics": true,
  "filters": {
    "status": "completed",
    "confidence_min": 90
  }
}
```

### 📥 Importar Dados
```http
POST /external/v1/import
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

### 🔗 Gerenciar Webhooks
```http
# Criar webhook
POST /external/v1/webhooks

# Listar webhooks
GET /external/v1/webhooks

# Remover webhook
DELETE /external/v1/webhooks/{webhook_id}
```

### 📈 Analytics
```http
GET /external/v1/analytics?date_from=2024-01-01&date_to=2024-01-31
Authorization: Bearer YOUR_API_KEY
```

## 🔗 Webhooks

### Eventos Disponíveis
- `project.created` - Projeto criado
- `project.completed` - Projeto concluído
- `project.failed` - Projeto falhou
- `analysis.started` - Análise iniciada
- `analysis.completed` - Análise concluída
- `iteration.completed` - Iteração concluída

### Configurar Webhook
```json
{
  "url": "https://meusite.com/webhook",
  "events": ["project.created", "project.completed"],
  "secret": "minha_chave_secreta",
  "active": true,
  "retry_count": 3,
  "timeout_seconds": 30
}
```

### Payload do Webhook
```json
{
  "event": "project.completed",
  "timestamp": "2024-01-15T10:32:30Z",
  "data": {
    "project_id": "ext_proj_1705312200_a1b2c3d4",
    "title": "App de Gestão de Tarefas",
    "status": "completed",
    "confidence_score": 94.4
  },
  "webhook_id": "webhook_123",
  "signature": "sha256=abc123..."
}
```

### Verificar Assinatura
```python
import hmac
import hashlib
import json

def verify_webhook_signature(payload, signature, secret):
    expected_signature = hmac.new(
        secret.encode(),
        json.dumps(payload, sort_keys=True, separators=(',', ':')).encode(),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)
```

## 📊 Rate Limiting

### Limites Padrão
- **Usuário**: 100 requisições/hora
- **Pro**: 500 requisições/hora
- **Admin**: 1000 requisições/hora

### Headers de Resposta
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1705315800
```

### Tratamento de Rate Limit
```python
import time
import requests

def make_api_request(url, headers, data=None):
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 429:
        # Rate limit excedido
        reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
        wait_time = reset_time - int(time.time())
        
        if wait_time > 0:
            print(f"Rate limit excedido. Aguardando {wait_time} segundos...")
            time.sleep(wait_time)
            return make_api_request(url, headers, data)
    
    return response
```

## 🛠️ SDKs e Exemplos

### Python SDK
```python
import httpx
from typing import Dict, Any, Optional

class CWBHubClient:
    def __init__(self, api_key: str, base_url: str = "http://localhost:8002/external/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.AsyncClient(base_url=base_url)
    
    def get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        response = await self.client.post(
            "/projects",
            json=project_data,
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        response = await self.client.get(
            f"/projects/{project_id}/status",
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()
    
    async def iterate_project(self, project_id: str, feedback: str) -> Dict[str, Any]:
        response = await self.client.post(
            f"/projects/{project_id}/iterate",
            json={"feedback": feedback},
            headers=self.get_headers()
        )
        response.raise_for_status()
        return response.json()

# Uso
async def main():
    client = CWBHubClient("sua_api_key_aqui")
    
    # Criar projeto
    project = await client.create_project({
        "title": "Meu Projeto",
        "description": "Descrição do projeto",
        "requirements": ["Requisito 1", "Requisito 2"]
    })
    
    print(f"Projeto criado: {project['project_id']}")
    print(f"Análise: {project['analysis'][:200]}...")
```

### JavaScript/Node.js
```javascript
const axios = require('axios');

class CWBHubClient {
    constructor(apiKey, baseURL = 'http://localhost:8002/external/v1') {
        this.apiKey = apiKey;
        this.baseURL = baseURL;
        this.client = axios.create({
            baseURL: baseURL,
            headers: {
                'Authorization': `Bearer ${apiKey}`,
                'Content-Type': 'application/json'
            }
        });
    }
    
    async createProject(projectData) {
        const response = await this.client.post('/projects', projectData);
        return response.data;
    }
    
    async getProjectStatus(projectId) {
        const response = await this.client.get(`/projects/${projectId}/status`);
        return response.data;
    }
    
    async iterateProject(projectId, feedback) {
        const response = await this.client.post(`/projects/${projectId}/iterate`, {
            feedback: feedback
        });
        return response.data;
    }
}

// Uso
const client = new CWBHubClient('sua_api_key_aqui');

client.createProject({
    title: 'Meu Projeto',
    description: 'Descrição do projeto',
    requirements: ['Requisito 1', 'Requisito 2']
}).then(project => {
    console.log(`Projeto criado: ${project.project_id}`);
    console.log(`Análise: ${project.analysis.substring(0, 200)}...`);
});
```

## 🧪 Testes

### Executar Testes
```bash
# Testes unitários
python -m pytest integrations/api/test_external_api.py -v

# Testes de integração
python integrations/api/test_external_api.py

# Testes de carga
python integrations/api/load_test.py
```

### Exemplo de Teste
```python
import asyncio
from integrations.api.test_external_api import TestExternalAPI

async def test_integration():
    tester = TestExternalAPI()
    await tester.run_all_tests()

# Executar
asyncio.run(test_integration())
```

## 📈 Monitoramento e Logs

### Métricas Disponíveis
- **Requisições por minuto/hora**
- **Tempo de resposta médio**
- **Taxa de erro**
- **Uso por API key**
- **Performance dos agentes**
- **Taxa de sucesso dos webhooks**

### Logs Estruturados
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "API_USAGE",
  "data": {
    "key_id": "cwb_1705312000_a1b2c3d4",
    "endpoint": "/projects",
    "method": "POST",
    "status": 200,
    "response_time_ms": 1250,
    "ip": "192.168.1.100"
  }
}
```

## 🔧 Configuração Avançada

### Variáveis de Ambiente
```bash
# .env
CWB_HUB_API_HOST=0.0.0.0
CWB_HUB_API_PORT=8002
CWB_HUB_API_DEBUG=false

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=1

# Rate Limiting
DEFAULT_RATE_LIMIT=1000
BURST_RATE_LIMIT=100

# Webhooks
WEBHOOK_TIMEOUT=30
WEBHOOK_RETRY_COUNT=3

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

### Configuração de Produção
```python
# production_config.py
import os

class ProductionConfig:
    # API
    HOST = "0.0.0.0"
    PORT = 8002
    DEBUG = False
    
    # Security
    CORS_ORIGINS = ["https://meusite.com"]
    TRUSTED_HOSTS = ["meusite.com", "api.meusite.com"]
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Redis
    REDIS_URL = os.getenv("REDIS_URL")
    
    # Monitoring
    SENTRY_DSN = os.getenv("SENTRY_DSN")
    PROMETHEUS_ENABLED = True
```

## 🚨 Tratamento de Erros

### Códigos de Erro
- **400** - Bad Request (dados inválidos)
- **401** - Unauthorized (API key inválida)
- **403** - Forbidden (permissão insuficiente)
- **404** - Not Found (recurso não encontrado)
- **429** - Too Many Requests (rate limit)
- **500** - Internal Server Error (erro interno)
- **503** - Service Unavailable (serviço indisponível)

### Formato de Erro
```json
{
  "error_code": "HTTP_400",
  "error_message": "Dados de entrada inválidos",
  "error_details": {
    "field": "requirements",
    "message": "Campo obrigatório"
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "req_123456",
  "documentation_url": "/external/v1/docs"
}
```

## 📞 Suporte

### Documentação
- **Swagger UI**: `/external/v1/docs`
- **ReDoc**: `/external/v1/redoc`
- **OpenAPI Spec**: `/external/v1/openapi.json`

### Contato
- **GitHub**: https://github.com/projetosdavidsimer/CWB-Hub-Hybrid-AI-System
- **Email**: suporte@cwbhub.com
- **Discord**: CWB Hub Community

### Status da API
- **Status Page**: https://status.cwbhub.com
- **Health Check**: `/external/v1/health`

---

## 🎉 Conclusão

A **CWB Hub External API** oferece uma interface poderosa e flexível para integração com o ecossistema de IA híbrida colaborativa. Com autenticação robusta, rate limiting inteligente, webhooks configuráveis e documentação completa, ela permite que sistemas externos aproveitem toda a capacidade analítica da equipe de 8 especialistas IA do CWB Hub.

**Desenvolvido com ❤️ pela Equipe CWB Hub**