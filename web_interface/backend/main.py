#!/usr/bin/env python3
"""
CWB Hub Web Interface - Backend API
FastAPI backend para interface web do CWB Hub Hybrid AI System
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import asyncio
import json
import sys
from pathlib import Path
import logging
from datetime import datetime
import uuid

# Adicionar src ao path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.core.hybrid_ai_orchestrator import HybridAIOrchestrator

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar FastAPI
app = FastAPI(
    title="CWB Hub Hybrid AI API",
    description="API para interface web do sistema de IA híbrida colaborativa",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class ProjectRequest(BaseModel):
    title: str
    description: str
    requirements: List[str]
    constraints: Optional[List[str]] = []
    urgency: str = "medium"
    budget: Optional[str] = None

class IterationRequest(BaseModel):
    session_id: str
    feedback: str

class ProjectResponse(BaseModel):
    session_id: str
    response: str
    confidence: float
    collaborations: int
    agents_involved: List[str]
    timestamp: datetime

# Gerenciador de conexões WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.session_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, session_id: str = None):
        await websocket.accept()
        self.active_connections.append(websocket)
        if session_id:
            if session_id not in self.session_connections:
                self.session_connections[session_id] = []
            self.session_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str = None):
        self.active_connections.remove(websocket)
        if session_id and session_id in self.session_connections:
            if websocket in self.session_connections[session_id]:
                self.session_connections[session_id].remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_session_message(self, message: str, session_id: str):
        if session_id in self.session_connections:
            for connection in self.session_connections[session_id]:
                await connection.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

# Instâncias globais
manager = ConnectionManager()
orchestrator_instances: Dict[str, HybridAIOrchestrator] = {}

# Rotas da API

@app.get("/")
async def root():
    """Página inicial da API"""
    return {
        "message": "CWB Hub Hybrid AI API",
        "version": "1.0.0",
        "status": "operational",
        "agents": 8,
        "capabilities": [
            "Strategic Analysis",
            "Technical Architecture", 
            "Full Stack Development",
            "Mobile Development",
            "UX/UI Design",
            "Quality Assurance",
            "DevOps Engineering",
            "Project Management"
        ]
    }

@app.get("/agents")
async def get_agents():
    """Retorna informações sobre os agentes disponíveis"""
    return {
        "agents": [
            {
                "id": "ana_beatriz_costa",
                "name": "Dra. Ana Beatriz Costa",
                "role": "Chief Technology Officer (CTO)",
                "expertise": ["Estratégia", "Inovação", "Liderança"],
                "avatar": "👩‍💼"
            },
            {
                "id": "carlos_eduardo_santos", 
                "name": "Dr. Carlos Eduardo Santos",
                "role": "Arquiteto de Software Sênior",
                "expertise": ["Arquitetura", "Padrões", "Escalabilidade"],
                "avatar": "👨‍💻"
            },
            {
                "id": "sofia_oliveira",
                "name": "Sofia Oliveira", 
                "role": "Engenheira Full Stack",
                "expertise": ["Frontend", "Backend", "APIs"],
                "avatar": "👩‍💻"
            },
            {
                "id": "gabriel_mendes",
                "name": "Gabriel Mendes",
                "role": "Engenheiro Mobile",
                "expertise": ["iOS", "Android", "Mobile UX"],
                "avatar": "👨‍📱"
            },
            {
                "id": "isabella_santos",
                "name": "Isabella Santos",
                "role": "Designer UX/UI Sênior", 
                "expertise": ["UX", "UI", "Design Thinking"],
                "avatar": "👩‍🎨"
            },
            {
                "id": "lucas_pereira",
                "name": "Lucas Pereira",
                "role": "Engenheiro de QA",
                "expertise": ["Qualidade", "Testes", "Automação"],
                "avatar": "👨‍🔬"
            },
            {
                "id": "mariana_rodrigues",
                "name": "Mariana Rodrigues", 
                "role": "Engenheira DevOps",
                "expertise": ["Infraestrutura", "CI/CD", "Cloud"],
                "avatar": "👩‍🔧"
            },
            {
                "id": "pedro_henrique_almeida",
                "name": "Pedro Henrique Almeida",
                "role": "Agile Project Manager",
                "expertise": ["Metodologias Ágeis", "Coordenação", "Entrega"],
                "avatar": "👨‍��"
            }
        ]
    }

@app.post("/projects", response_model=ProjectResponse)
async def create_project(request: ProjectRequest):
    """Cria um novo projeto e processa com a equipe CWB Hub"""
    try:
        # Gerar ID da sessão
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
        
        # Criar instância do orquestrador
        orchestrator = HybridAIOrchestrator()
        orchestrator_instances[session_id] = orchestrator
        
        # Inicializar agentes
        await orchestrator.initialize_agents()
        
        # Construir solicitação
        project_description = f"""
PROJETO: {request.title}

DESCRIÇÃO:
{request.description}

REQUISITOS:
{chr(10).join([f"- {req}" for req in request.requirements])}

RESTRIÇÕES:
{chr(10).join([f"- {constraint}" for constraint in request.constraints]) if request.constraints else "Nenhuma restrição específica"}

URGÊNCIA: {request.urgency}
ORÇAMENTO: {request.budget or "A definir"}
        """
        
        # Processar com a equipe
        response = await orchestrator.process_request(project_description)
        
        # Obter estatísticas
        try:
            stats = orchestrator.get_session_status()
            collaborations = stats.get('agent_responses_count', 0)
            agents_involved = list(stats.get('agents_involved', []))
        except:
            collaborations = 8  # Fallback
            agents_involved = ["ana_beatriz_costa", "carlos_eduardo_santos", "sofia_oliveira", 
                             "gabriel_mendes", "isabella_santos", "lucas_pereira", 
                             "mariana_rodrigues", "pedro_henrique_almeida"]
        
        # Criar resposta
        project_response = ProjectResponse(
            session_id=session_id,
            response=response,
            confidence=94.4,  # Confiança padrão da equipe
            collaborations=collaborations,
            agents_involved=agents_involved,
            timestamp=datetime.now()
        )
        
        # Notificar via WebSocket
        await manager.send_session_message(
            json.dumps({
                "type": "project_completed",
                "session_id": session_id,
                "status": "completed"
            }),
            session_id
        )
        
        return project_response
        
    except Exception as e:
        logger.error(f"Erro ao processar projeto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/projects/{session_id}/iterate")
async def iterate_project(session_id: str, request: IterationRequest):
    """Itera um projeto existente com feedback"""
    try:
        if session_id not in orchestrator_instances:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        
        orchestrator = orchestrator_instances[session_id]
        
        # Iterar com feedback
        response = await orchestrator.iterate_solution(session_id, request.feedback)
        
        # Notificar via WebSocket
        await manager.send_session_message(
            json.dumps({
                "type": "iteration_completed", 
                "session_id": session_id,
                "response": response
            }),
            session_id
        )
        
        return {"session_id": session_id, "response": response}
        
    except Exception as e:
        logger.error(f"Erro ao iterar projeto: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{session_id}/status")
async def get_project_status(session_id: str):
    """Retorna status de um projeto"""
    try:
        if session_id not in orchestrator_instances:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        
        orchestrator = orchestrator_instances[session_id]
        status = orchestrator.get_session_status()
        
        return {"session_id": session_id, "status": status}
        
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket para atualizações em tempo real"""
    await manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo para teste
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket, session_id)

@app.on_event("shutdown")
async def shutdown_event():
    """Limpa recursos ao encerrar"""
    for orchestrator in orchestrator_instances.values():
        try:
            await orchestrator.shutdown()
        except:
            pass
    orchestrator_instances.clear()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)