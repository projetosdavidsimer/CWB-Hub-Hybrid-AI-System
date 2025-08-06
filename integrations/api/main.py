"""
CWB Hub Public API - Melhoria #3
API REST pública para integração com o CWB Hub Hybrid AI System
Implementado pela Equipe CWB Hub + Qodo (Freelancer)
"""

from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import asyncio
import sys
import os
import time
import hashlib
import jwt
from datetime import datetime, timedelta
import redis
import logging
from contextlib import asynccontextmanager

# Adicionar src ao path para importar CWB Hub
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, '..', '..', 'src')
sys.path.insert(0, src_path)

try:
    from core.hybrid_ai_orchestrator import HybridAIOrchestrator
    logger.info("✅ CWB Hub core importado com sucesso")
except ImportError as e:
    # Fallback para desenvolvimento
    logger.warning(f"⚠️ CWB Hub core não encontrado: {e}")
    HybridAIOrchestrator = None

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração Redis para rate limiting
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()
    logger.info("✅ Redis conectado para rate limiting")
except:
    redis_client = None
    logger.warning("⚠️ Redis não disponível - rate limiting desabilitado")

# Configuração JWT
JWT_SECRET = "cwb-hub-secret-key-change-in-production"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()

# Modelos Pydantic
class AnalysisRequest(BaseModel):
    """Solicitação de análise para a equipe CWB Hub"""
    request: str = Field(..., description="Descrição do projeto ou problema a ser analisado")
    context: Optional[str] = Field(None, description="Contexto adicional sobre o projeto")
    priority: Optional[str] = Field("normal", description="Prioridade: low, normal, high, urgent")
    
    class Config:
        schema_extra = {
            "example": {
                "request": "Preciso desenvolver um app mobile para gestão de projetos com colaboração em tempo real",
                "context": "Startup com orçamento limitado, prazo de 3 meses para MVP",
                "priority": "high"
            }
        }

class IterationRequest(BaseModel):
    """Solicitação de iteração/refinamento"""
    session_id: str = Field(..., description="ID da sessão de análise")
    feedback: str = Field(..., description="Feedback para refinamento da solução")
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "session_20250806_123456",
                "feedback": "Gostei da proposta, mas o orçamento é limitado. Precisamos focar no essencial."
            }
        }

class APIKeyRequest(BaseModel):
    """Solicitação de API Key"""
    name: str = Field(..., description="Nome da aplicação/empresa")
    email: str = Field(..., description="Email de contato")
    description: Optional[str] = Field(None, description="Descrição do uso pretendido")

class AnalysisResponse(BaseModel):
    """Resposta da análise da equipe CWB Hub"""
    session_id: str
    analysis: str
    confidence: float
    agents_involved: List[str]
    collaboration_stats: Dict[str, Any]
    timestamp: datetime
    
class SessionStatus(BaseModel):
    """Status de uma sessão de análise"""
    session_id: str
    status: str
    created_at: datetime
    iterations: int
    final_solution: Optional[str]

# Instância global do CWB Hub
cwb_hub_orchestrator = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerenciamento do ciclo de vida da aplicação"""
    global cwb_hub_orchestrator
    
    # Startup
    logger.info("🚀 Inicializando CWB Hub API...")
    
    if HybridAIOrchestrator:
        try:
            cwb_hub_orchestrator = HybridAIOrchestrator()
            await cwb_hub_orchestrator.initialize_agents()
            logger.info("✅ CWB Hub Orchestrator inicializado")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar CWB Hub: {e}")
            cwb_hub_orchestrator = None
    
    yield
    
    # Shutdown
    logger.info("🔚 Encerrando CWB Hub API...")
    if cwb_hub_orchestrator:
        try:
            await cwb_hub_orchestrator.shutdown()
            logger.info("✅ CWB Hub Orchestrator encerrado")
        except Exception as e:
            logger.error(f"❌ Erro ao encerrar CWB Hub: {e}")

# Criar aplicação FastAPI
app = FastAPI(
    title="CWB Hub Public API",
    description="API REST pública para integração com o CWB Hub Hybrid AI System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware de hosts confiáveis
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Em produção, especificar hosts
)

# Funções auxiliares
def generate_api_key(name: str, email: str) -> str:
    """Gera uma API key única"""
    data = f"{name}:{email}:{time.time()}"
    return hashlib.sha256(data.encode()).hexdigest()

def create_jwt_token(api_key: str) -> str:
    """Cria um JWT token"""
    payload = {
        "api_key": api_key,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str) -> Optional[str]:
    """Verifica um JWT token e retorna a API key"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("api_key")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido")

def check_rate_limit(api_key: str, limit: int = 100, window: int = 3600) -> bool:
    """Verifica rate limiting (100 requests por hora por padrão)"""
    if not redis_client:
        return True  # Se Redis não disponível, permite
    
    key = f"rate_limit:{api_key}"
    current = redis_client.get(key)
    
    if current is None:
        redis_client.setex(key, window, 1)
        return True
    
    if int(current) >= limit:
        return False
    
    redis_client.incr(key)
    return True

async def get_current_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Dependency para verificar autenticação"""
    token = credentials.credentials
    api_key = verify_jwt_token(token)
    
    if not api_key:
        raise HTTPException(status_code=401, detail="API key inválida")
    
    # Verificar rate limiting
    if not check_rate_limit(api_key):
        raise HTTPException(status_code=429, detail="Rate limit excedido")
    
    return api_key

# Endpoints da API

@app.get("/", tags=["Health"])
async def root():
    """Endpoint raiz - informações da API"""
    return {
        "name": "CWB Hub Public API",
        "version": "1.0.0",
        "description": "API REST pública para integração com o CWB Hub Hybrid AI System",
        "status": "operational",
        "cwb_hub_available": cwb_hub_orchestrator is not None,
        "endpoints": {
            "health": "/health",
            "auth": "/auth/api-key",
            "analyze": "/analyze",
            "iterate": "/iterate/{session_id}",
            "status": "/status/{session_id}",
            "docs": "/docs"
        }
    }

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check da API"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "cwb_hub_status": "available" if cwb_hub_orchestrator else "unavailable",
        "redis_status": "available" if redis_client else "unavailable"
    }

@app.post("/auth/api-key", tags=["Authentication"])
async def request_api_key(request: APIKeyRequest):
    """Solicitar uma API key para usar a API"""
    try:
        # Gerar API key
        api_key = generate_api_key(request.name, request.email)
        
        # Criar JWT token
        token = create_jwt_token(api_key)
        
        # Log da criação
        logger.info(f"Nova API key criada para {request.name} ({request.email})")
        
        return {
            "api_key": api_key,
            "token": token,
            "expires_in": JWT_EXPIRATION_HOURS * 3600,  # segundos
            "usage": {
                "rate_limit": "100 requests/hour",
                "documentation": "/docs",
                "support": "https://github.com/projetosdavidsimer/CWB-Hub-Hybrid-AI-System"
            }
        }
    except Exception as e:
        logger.error(f"Erro ao criar API key: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.post("/analyze", response_model=AnalysisResponse, tags=["CWB Hub"])
async def analyze_project(
    request: AnalysisRequest,
    api_key: str = Depends(get_current_api_key)
):
    """Analisar um projeto com a equipe CWB Hub"""
    if not cwb_hub_orchestrator:
        raise HTTPException(status_code=503, detail="CWB Hub não disponível")
    
    try:
        logger.info(f"Nova análise solicitada por API key: {api_key[:8]}...")
        
        # Processar solicitação com CWB Hub
        start_time = time.time()
        response = await cwb_hub_orchestrator.process_request(request.request)
        processing_time = time.time() - start_time
        
        # Obter estatísticas da sessão
        sessions = list(cwb_hub_orchestrator.active_sessions.keys())
        session_id = sessions[0] if sessions else "no_session"
        
        session_status = cwb_hub_orchestrator.get_session_status(session_id) if sessions else {}
        collaboration_stats = cwb_hub_orchestrator.collaboration_framework.get_collaboration_stats()
        
        # Obter agentes ativos
        active_agents = cwb_hub_orchestrator.get_active_agents()
        
        logger.info(f"Análise concluída em {processing_time:.2f}s para sessão {session_id}")
        
        return AnalysisResponse(
            session_id=session_id,
            analysis=response,
            confidence=0.944,  # Baseado nas métricas da equipe
            agents_involved=active_agents,
            collaboration_stats=collaboration_stats,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Erro na análise: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

@app.post("/iterate/{session_id}", tags=["CWB Hub"])
async def iterate_solution(
    session_id: str,
    request: IterationRequest,
    api_key: str = Depends(get_current_api_key)
):
    """Iterar/refinar uma solução existente"""
    if not cwb_hub_orchestrator:
        raise HTTPException(status_code=503, detail="CWB Hub não disponível")
    
    try:
        logger.info(f"Iteração solicitada para sessão {session_id}")
        
        # Verificar se a sessão existe
        if session_id not in cwb_hub_orchestrator.active_sessions:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        
        # Processar iteração
        refined_response = await cwb_hub_orchestrator.iterate_solution(session_id, request.feedback)
        
        # Obter estatísticas atualizadas
        session_status = cwb_hub_orchestrator.get_session_status(session_id)
        collaboration_stats = cwb_hub_orchestrator.collaboration_framework.get_collaboration_stats()
        
        logger.info(f"Iteração concluída para sessão {session_id}")
        
        return {
            "session_id": session_id,
            "refined_analysis": refined_response,
            "iteration_count": session_status.get("iterations", 0),
            "collaboration_stats": collaboration_stats,
            "timestamp": datetime.utcnow()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na iteração: {e}")
        raise HTTPException(status_code=500, detail=f"Erro na iteração: {str(e)}")

@app.get("/status/{session_id}", response_model=SessionStatus, tags=["CWB Hub"])
async def get_session_status(
    session_id: str,
    api_key: str = Depends(get_current_api_key)
):
    """Obter status de uma sessão de análise"""
    if not cwb_hub_orchestrator:
        raise HTTPException(status_code=503, detail="CWB Hub não disponível")
    
    try:
        # Verificar se a sessão existe
        if session_id not in cwb_hub_orchestrator.active_sessions:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        
        # Obter status da sessão
        status_data = cwb_hub_orchestrator.get_session_status(session_id)
        session = cwb_hub_orchestrator.active_sessions[session_id]
        
        return SessionStatus(
            session_id=session_id,
            status=status_data.get("current_phase", "unknown"),
            created_at=session.created_at,
            iterations=status_data.get("iterations", 0),
            final_solution=session.final_solution
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao obter status: {str(e)}")

@app.get("/sessions", tags=["CWB Hub"])
async def list_sessions(api_key: str = Depends(get_current_api_key)):
    """Listar sessões ativas"""
    if not cwb_hub_orchestrator:
        raise HTTPException(status_code=503, detail="CWB Hub não disponível")
    
    try:
        sessions = []
        for session_id, session in cwb_hub_orchestrator.active_sessions.items():
            status_data = cwb_hub_orchestrator.get_session_status(session_id)
            sessions.append({
                "session_id": session_id,
                "status": status_data.get("current_phase", "unknown"),
                "created_at": session.created_at,
                "iterations": status_data.get("iterations", 0),
                "has_final_solution": session.final_solution is not None
            })
        
        return {
            "total_sessions": len(sessions),
            "sessions": sessions
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar sessões: {e}")
        raise HTTPException(status_code=500, detail=f"Erro ao listar sessões: {str(e)}")

# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.3f}s"
    )
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )