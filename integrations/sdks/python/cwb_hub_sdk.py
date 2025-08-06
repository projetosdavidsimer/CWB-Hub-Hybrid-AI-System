"""
CWB Hub Python SDK - Melhoria #3 Fase 3
SDK Python para integração fácil com o CWB Hub Hybrid AI System
Implementado pela Equipe CWB Hub + Qodo (Freelancer)
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import httpx
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CWBHubResponse:
    """Resposta do CWB Hub"""
    session_id: str
    analysis: str
    confidence: float
    agents_involved: List[str]
    collaboration_stats: Dict[str, Any]
    timestamp: datetime
    processing_time: float
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], processing_time: float = 0.0):
        """Criar instância a partir de dicionário"""
        return cls(
            session_id=data.get("session_id", ""),
            analysis=data.get("analysis", ""),
            confidence=data.get("confidence", 0.0),
            agents_involved=data.get("agents_involved", []),
            collaboration_stats=data.get("collaboration_stats", {}),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.utcnow().isoformat())),
            processing_time=processing_time
        )

@dataclass
class CWBHubSession:
    """Sessão do CWB Hub"""
    session_id: str
    status: str
    created_at: datetime
    iterations: int
    final_solution: Optional[str]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Criar instância a partir de dicionário"""
        return cls(
            session_id=data.get("session_id", ""),
            status=data.get("status", "unknown"),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat())),
            iterations=data.get("iterations", 0),
            final_solution=data.get("final_solution")
        )

class CWBHubError(Exception):
    """Exceção base do CWB Hub SDK"""
    pass

class CWBHubAuthError(CWBHubError):
    """Erro de autenticação"""
    pass

class CWBHubAPIError(CWBHubError):
    """Erro da API"""
    def __init__(self, message: str, status_code: int = None, response_data: Dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data or {}

class CWBHubClient:
    """Cliente Python para o CWB Hub Hybrid AI System"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000",
        timeout: float = 60.0,
        max_retries: int = 3
    ):
        """
        Inicializar cliente CWB Hub
        
        Args:
            api_key: API key para autenticação (obtenha via /auth/api-key)
            base_url: URL base da API CWB Hub
            timeout: Timeout para requests em segundos
            max_retries: Número máximo de tentativas em caso de erro
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.client = httpx.AsyncClient(timeout=timeout)
        self._token = None
        
    async def __aenter__(self):
        """Context manager async entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager async exit"""
        await self.close()
    
    async def close(self):
        """Fechar cliente"""
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Obter headers para requests"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "CWB-Hub-Python-SDK/1.0"
        }
        
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"
        
        return headers
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Fazer request para a API"""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers()
        
        for attempt in range(self.max_retries + 1):
            try:
                response = await self.client.request(
                    method=method,
                    url=url,
                    json=data,
                    params=params,
                    headers=headers
                )
                
                if response.status_code == 401:
                    raise CWBHubAuthError("Token inválido ou expirado")
                
                if response.status_code >= 400:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        pass
                    
                    raise CWBHubAPIError(
                        f"API Error: {response.status_code}",
                        status_code=response.status_code,
                        response_data=error_data
                    )
                
                return response.json()
                
            except httpx.RequestError as e:
                if attempt == self.max_retries:
                    raise CWBHubError(f"Request failed after {self.max_retries + 1} attempts: {e}")
                
                # Backoff exponencial
                await asyncio.sleep(2 ** attempt)
    
    async def authenticate(self, name: str, email: str, description: str = "") -> str:
        """
        Autenticar e obter token
        
        Args:
            name: Nome da aplicação/empresa
            email: Email de contato
            description: Descrição do uso pretendido
            
        Returns:
            Token de autenticação
        """
        data = {
            "name": name,
            "email": email,
            "description": description
        }
        
        response = await self._request("POST", "/auth/api-key", data=data)
        
        self.api_key = response["api_key"]
        self._token = response["token"]
        
        logger.info(f"Autenticado com sucesso: {name}")
        return self._token
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Verificar saúde da API
        
        Returns:
            Status da API
        """
        return await self._request("GET", "/health")
    
    async def analyze(
        self,
        request: str,
        context: Optional[str] = None,
        priority: str = "normal"
    ) -> CWBHubResponse:
        """
        Analisar projeto com a equipe CWB Hub
        
        Args:
            request: Descrição do projeto ou problema
            context: Contexto adicional
            priority: Prioridade (low, normal, high, urgent)
            
        Returns:
            Resposta da análise
        """
        if not self._token:
            raise CWBHubAuthError("Cliente não autenticado. Use authenticate() primeiro.")
        
        data = {
            "request": request,
            "context": context,
            "priority": priority
        }
        
        start_time = time.time()
        response = await self._request("POST", "/analyze", data=data)
        processing_time = time.time() - start_time
        
        logger.info(f"Análise concluída em {processing_time:.2f}s")
        return CWBHubResponse.from_dict(response, processing_time)
    
    async def iterate(self, session_id: str, feedback: str) -> Dict[str, Any]:
        """
        Iterar/refinar uma solução existente
        
        Args:
            session_id: ID da sessão
            feedback: Feedback para refinamento
            
        Returns:
            Solução refinada
        """
        if not self._token:
            raise CWBHubAuthError("Cliente não autenticado. Use authenticate() primeiro.")
        
        data = {
            "session_id": session_id,
            "feedback": feedback
        }
        
        start_time = time.time()
        response = await self._request("POST", f"/iterate/{session_id}", data=data)
        processing_time = time.time() - start_time
        
        logger.info(f"Iteração concluída em {processing_time:.2f}s")
        return response
    
    async def get_session_status(self, session_id: str) -> CWBHubSession:
        """
        Obter status de uma sessão
        
        Args:
            session_id: ID da sessão
            
        Returns:
            Status da sessão
        """
        if not self._token:
            raise CWBHubAuthError("Cliente não autenticado. Use authenticate() primeiro.")
        
        response = await self._request("GET", f"/status/{session_id}")
        return CWBHubSession.from_dict(response)
    
    async def list_sessions(self) -> List[Dict[str, Any]]:
        """
        Listar sessões ativas
        
        Returns:
            Lista de sessões
        """
        if not self._token:
            raise CWBHubAuthError("Cliente não autenticado. Use authenticate() primeiro.")
        
        response = await self._request("GET", "/sessions")
        return response.get("sessions", [])

# Classe síncrona para facilidade de uso
class CWBHubSyncClient:
    """Cliente síncrono para o CWB Hub (wrapper do cliente async)"""
    
    def __init__(self, **kwargs):
        self._async_client = CWBHubClient(**kwargs)
        self._loop = None
    
    def _run_async(self, coro):
        """Executar corrotina de forma síncrona"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(coro)
    
    def authenticate(self, name: str, email: str, description: str = "") -> str:
        """Autenticar (versão síncrona)"""
        return self._run_async(self._async_client.authenticate(name, email, description))
    
    def health_check(self) -> Dict[str, Any]:
        """Health check (versão síncrona)"""
        return self._run_async(self._async_client.health_check())
    
    def analyze(self, request: str, context: Optional[str] = None, priority: str = "normal") -> CWBHubResponse:
        """Analisar projeto (versão síncrona)"""
        return self._run_async(self._async_client.analyze(request, context, priority))
    
    def iterate(self, session_id: str, feedback: str) -> Dict[str, Any]:
        """Iterar solução (versão síncrona)"""
        return self._run_async(self._async_client.iterate(session_id, feedback))
    
    def get_session_status(self, session_id: str) -> CWBHubSession:
        """Obter status da sessão (versão síncrona)"""
        return self._run_async(self._async_client.get_session_status(session_id))
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """Listar sessões (versão síncrona)"""
        return self._run_async(self._async_client.list_sessions())
    
    def close(self):
        """Fechar cliente"""
        self._run_async(self._async_client.close())

# Funções de conveniência
async def quick_analyze(request: str, name: str = "Quick Analysis", email: str = "user@example.com") -> CWBHubResponse:
    """
    Análise rápida sem configuração manual
    
    Args:
        request: Descrição do projeto
        name: Nome da aplicação
        email: Email de contato
        
    Returns:
        Resposta da análise
    """
    async with CWBHubClient() as client:
        await client.authenticate(name, email, "Quick analysis")
        return await client.analyze(request)

def quick_analyze_sync(request: str, name: str = "Quick Analysis", email: str = "user@example.com") -> CWBHubResponse:
    """Versão síncrona da análise rápida"""
    return asyncio.run(quick_analyze(request, name, email))

# Exemplo de uso
if __name__ == "__main__":
    async def example_usage():
        """Exemplo de uso do SDK"""
        print("🚀 CWB Hub Python SDK - Exemplo de Uso")
        print("=" * 50)
        
        # Criar cliente
        async with CWBHubClient() as client:
            try:
                # Autenticar
                print("🔐 Autenticando...")
                await client.authenticate(
                    name="Minha Empresa",
                    email="contato@minhaempresa.com",
                    description="Teste do SDK Python"
                )
                print("✅ Autenticado com sucesso!")
                
                # Health check
                print("\n🔍 Verificando saúde da API...")
                health = await client.health_check()
                print(f"✅ API Status: {health['status']}")
                
                # Análise
                print("\n🧠 Solicitando análise...")
                response = await client.analyze(
                    request="Preciso criar um sistema de e-commerce completo com carrinho, pagamento e painel admin",
                    context="Startup com orçamento limitado, prazo de 4 meses",
                    priority="high"
                )
                
                print(f"✅ Análise concluída!")
                print(f"   Session ID: {response.session_id}")
                print(f"   Confiança: {response.confidence*100:.1f}%")
                print(f"   Agentes: {len(response.agents_involved)}")
                print(f"   Tempo: {response.processing_time:.2f}s")
                print(f"   Análise: {response.analysis[:200]}...")
                
                # Iteração
                print("\n🔄 Refinando solução...")
                iteration = await client.iterate(
                    response.session_id,
                    "O orçamento é mais limitado que esperado. Focar no MVP essencial."
                )
                print("✅ Solução refinada!")
                
                # Status da sessão
                print("\n📊 Verificando status...")
                status = await client.get_session_status(response.session_id)
                print(f"✅ Status: {status.status}")
                print(f"   Iterações: {status.iterations}")
                
                # Listar sessões
                print("\n📋 Listando sessões...")
                sessions = await client.list_sessions()
                print(f"✅ {len(sessions)} sessões ativas")
                
            except CWBHubError as e:
                print(f"❌ Erro: {e}")
    
    # Executar exemplo
    asyncio.run(example_usage())
    
    print("\n" + "=" * 50)
    print("🎉 Exemplo concluído!")
    print("📚 Documentação: https://github.com/cwb-hub/python-sdk")