"""
Exemplo de uso do SDK Python do CWB Hub Hybrid AI System
"""
from cwb_hub_sdk import CWBHubClient

API_URL = "http://localhost:8000"  # Altere para o endpoint da sua API
API_KEY = "SUA_API_KEY_AQUI"  # Opcional, se necessário

client = CWBHubClient(api_url=API_URL, api_key=API_KEY)

# Verificar status da API
print("Status da API:", client.health())

# Enviar projeto para análise
project_data = {
    "title": "App Mobile de Gestão de Projetos",
    "description": "Preciso desenvolver um app mobile para gestão de projetos com colaboração em tempo real, dashboard e integração com Slack.",
    "requirements": [
        "Colaboração em tempo real",
        "Sincronização offline",
        "Dashboard de métricas",
        "Integração com Slack",
        "Interface intuitiva"
    ]
}
response = client.analyze(project_data)
print("Resposta da equipe CWB Hub:", response)

# Iterar solução com feedback
session_id = response.get("session_id")
if session_id:
    feedback = "O orçamento é limitado, priorize funcionalidades essenciais."
    refined = client.iterate(session_id, feedback)
    print("Solução refinada:", refined)

# Consultar status da sessão
if session_id:
    status = client.status(session_id)
    print("Status da sessão:", status)

# Listar sessões recentes
print("Sessões recentes:", client.sessions())
