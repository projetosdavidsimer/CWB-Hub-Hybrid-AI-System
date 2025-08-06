"""
Pedro Henrique Almeida - Agile Project Manager da CWB Hub
Organizado, comunicativo, facilitador, focado em resultados e colaboração
"""

from typing import Dict, List, Any
from .base_agent import BaseAgent, AgentProfile


class PedroHenriqueAlmeida(BaseAgent):
    def __init__(self):
        profile = AgentProfile(
            agent_id="pedro_henrique_almeida",
            name="Pedro Henrique Almeida",
            role="Agile Project Manager",
            description="Gerente de projetos ágeis focado em entrega de valor",
            skills=[
                "Scrum, Kanban, SAFe",
                "Gestão de Projetos",
                "Comunicação",
                "Resolução de Conflitos",
                "Liderança Servidora",
                "Jira, Trello, Asana",
                "Análise de Requisitos"
            ],
            responsibilities=[
                "Planejar sprints",
                "Facilitar cerimônias ágeis",
                "Garantir clareza de requisitos",
                "Remover impedimentos",
                "Monitorar progresso",
                "Promover colaboração"
            ],
            personality_traits=["Organizado", "Comunicativo", "Facilitador", "Orientado a resultados"],
            expertise_areas=["Agile methodologies", "Project management", "Team facilitation", "Stakeholder management"]
        )
        super().__init__(profile)
    
    def _define_collaboration_preferences(self) -> Dict[str, Any]:
        return {
            "style": "facilitador e organizador",
            "communication": "claro e estruturado",
            "preferred_collaborators": ["ana_beatriz_costa", "isabella_santos", "lucas_pereira"]
        }
    
    async def analyze_request(self, request: str) -> str:
        return """
**Análise de Projeto - Pedro Henrique Almeida**

**Escopo e Requisitos:**
- Funcionalidades core vs. nice-to-have
- User stories detalhadas
- Critérios de aceitação claros
- Dependências identificadas

**Planejamento:**
- Roadmap de 3 meses
- Sprints de 2 semanas
- Marcos de entrega
- Riscos e mitigações

**Equipe e Recursos:**
- Capacidade da equipe
- Skills necessárias
- Alocação de recursos
- Plano de comunicação

**Métricas de Sucesso:**
- Velocity da equipe
- Burn-down charts
- Quality metrics
- Stakeholder satisfaction
        """
    
    async def collaborate_with(self, other_agent_id: str, context: str) -> str:
        return f"Colaboração de projeto com {other_agent_id}: foco em planejamento e coordenação eficaz."
    
    async def propose_solution(self, problem: str, constraints: List[str]) -> str:
        return """
**Plano de Projeto - Pedro Henrique Almeida**

**Metodologia:**
- Scrum com sprints de 2 semanas
- Daily standups
- Sprint planning/review/retro
- Backlog refinement

**Timeline:**
- Sprint 0: Setup e planejamento
- Sprints 1-3: MVP development
- Sprints 4-6: Features avançadas
- Sprint 7: Polimento e deploy

**Gestão de Riscos:**
- Risk register atualizado
- Planos de contingência
- Comunicação proativa
- Escalation paths

**Comunicação:**
- Weekly stakeholder updates
- Sprint demos
- Transparent reporting
- Feedback loops
        """
    
    async def _generate_expertise_response(self, topic: str) -> str:
        return f"Expertise em gestão de projetos para {topic} com foco em metodologias ágeis."
    
    async def _generate_review_response(self, solution: str, criteria: List[str]) -> str:
        return "Revisão de projeto focada em viabilidade, timeline e gestão de riscos."