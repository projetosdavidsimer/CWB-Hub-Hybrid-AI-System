"""
Classe base para todos os agentes da CWB Hub
Define a interface comum e funcionalidades compartilhadas
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class AgentProfile:
    """Perfil de um agente profissional"""
    agent_id: str
    name: str
    role: str
    description: str
    skills: List[str]
    responsibilities: List[str]
    personality_traits: List[str]
    expertise_areas: List[str]


@dataclass
class AgentContext:
    """Contexto de trabalho do agente"""
    current_project: Optional[str]
    previous_interactions: List[str]
    collaboration_history: Dict[str, Any]
    knowledge_base: Dict[str, Any]


class BaseAgent(ABC):
    """
    Classe base abstrata para todos os agentes profissionais da CWB Hub
    
    Cada agente representa um profissional sênior com:
    - Personalidade única
    - Expertise específica
    - Estilo de comunicação próprio
    - Capacidade de colaboração
    """
    
    def __init__(self, profile: AgentProfile):
        self.profile = profile
        self.context = AgentContext(
            current_project=None,
            previous_interactions=[],
            collaboration_history={},
            knowledge_base={}
        )
        self.logger = logging.getLogger(f"agent.{profile.agent_id}")
        self.is_active = True
        self.collaboration_preferences = self._define_collaboration_preferences()
    
    @abstractmethod
    async def analyze_request(self, request: str) -> str:
        """
        Analisa uma solicitação sob a perspectiva do agente
        
        Args:
            request: Solicitação do usuário
            
        Returns:
            Análise detalhada do agente
        """
        pass
    
    @abstractmethod
    async def collaborate_with(self, other_agent_id: str, context: str) -> str:
        """
        Colabora com outro agente
        
        Args:
            other_agent_id: ID do outro agente
            context: Contexto da colaboração
            
        Returns:
            Contribuição para a colaboração
        """
        pass
    
    @abstractmethod
    async def propose_solution(self, problem: str, constraints: List[str]) -> str:
        """
        Propõe uma solução para um problema
        
        Args:
            problem: Descrição do problema
            constraints: Lista de restrições
            
        Returns:
            Proposta de solução
        """
        pass
    
    @abstractmethod
    def _define_collaboration_preferences(self) -> Dict[str, Any]:
        """
        Define as preferências de colaboração do agente
        
        Returns:
            Dicionário com preferências de colaboração
        """
        pass
    
    async def provide_expertise(self, topic: str) -> str:
        """
        Fornece expertise sobre um tópico específico
        
        Args:
            topic: Tópico sobre o qual fornecer expertise
            
        Returns:
            Conhecimento especializado sobre o tópico
        """
        if not self._is_topic_in_expertise(topic):
            return f"Como {self.profile.role}, este tópico está fora da minha área de expertise principal."
        
        return await self._generate_expertise_response(topic)
    
    async def review_solution(self, solution: str, criteria: List[str]) -> str:
        """
        Revisa uma solução proposta
        
        Args:
            solution: Solução a ser revisada
            criteria: Critérios de avaliação
            
        Returns:
            Feedback sobre a solução
        """
        return await self._generate_review_response(solution, criteria)
    
    def update_context(self, interaction: str, collaborator: Optional[str] = None):
        """
        Atualiza o contexto do agente com nova interação
        
        Args:
            interaction: Descrição da interação
            collaborator: ID do colaborador (se aplicável)
        """
        self.context.previous_interactions.append({
            "timestamp": datetime.now().isoformat(),
            "interaction": interaction,
            "collaborator": collaborator
        })
        
        if collaborator:
            if collaborator not in self.context.collaboration_history:
                self.context.collaboration_history[collaborator] = []
            self.context.collaboration_history[collaborator].append(interaction)
    
    def get_collaboration_style(self) -> str:
        """
        Retorna o estilo de colaboração do agente
        
        Returns:
            Descrição do estilo de colaboração
        """
        return self.collaboration_preferences.get("style", "colaborativo")
    
    def get_communication_style(self) -> str:
        """
        Retorna o estilo de comunicação do agente
        
        Returns:
            Descrição do estilo de comunicação
        """
        return self.collaboration_preferences.get("communication", "direto e técnico")
    
    def _is_topic_in_expertise(self, topic: str) -> bool:
        """
        Verifica se um tópico está na área de expertise do agente
        
        Args:
            topic: Tópico a verificar
            
        Returns:
            True se o tópico está na expertise, False caso contrário
        """
        topic_lower = topic.lower()
        for area in self.profile.expertise_areas:
            if area.lower() in topic_lower or topic_lower in area.lower():
                return True
        return False
    
    @abstractmethod
    async def _generate_expertise_response(self, topic: str) -> str:
        """
        Gera resposta de expertise específica do agente
        
        Args:
            topic: Tópico sobre o qual fornecer expertise
            
        Returns:
            Resposta especializada
        """
        pass
    
    @abstractmethod
    async def _generate_review_response(self, solution: str, criteria: List[str]) -> str:
        """
        Gera resposta de revisão específica do agente
        
        Args:
            solution: Solução a ser revisada
            criteria: Critérios de avaliação
            
        Returns:
            Feedback de revisão
        """
        pass
    
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Retorna informações completas do agente
        
        Returns:
            Dicionário com informações do agente
        """
        return {
            "profile": {
                "agent_id": self.profile.agent_id,
                "name": self.profile.name,
                "role": self.profile.role,
                "description": self.profile.description,
                "skills": self.profile.skills,
                "responsibilities": self.profile.responsibilities,
                "personality_traits": self.profile.personality_traits,
                "expertise_areas": self.profile.expertise_areas
            },
            "status": {
                "is_active": self.is_active,
                "current_project": self.context.current_project,
                "interactions_count": len(self.context.previous_interactions),
                "collaborations_count": len(self.context.collaboration_history)
            },
            "collaboration": {
                "style": self.get_collaboration_style(),
                "communication": self.get_communication_style(),
                "preferences": self.collaboration_preferences
            }
        }
    
    def __str__(self) -> str:
        return f"{self.profile.name} ({self.profile.role})"
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: {self.profile.agent_id}>"