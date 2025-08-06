"""
Analisador de Requisitos da CWB Hub
Analisa solicitações e determina quais agentes devem ser envolvidos
"""

import re
import logging
from typing import List, Dict, Any, Set
from dataclasses import dataclass
from enum import Enum


class RequirementType(Enum):
    STRATEGIC = "strategic"
    ARCHITECTURAL = "architectural"
    DEVELOPMENT = "development"
    DESIGN = "design"
    QUALITY = "quality"
    INFRASTRUCTURE = "infrastructure"
    PROJECT_MANAGEMENT = "project_management"
    MOBILE = "mobile"


@dataclass
class RequirementAnalysis:
    requirement_types: List[RequirementType]
    complexity_score: float
    estimated_effort: str
    key_technologies: List[str]
    stakeholders: List[str]
    priority: int
    relevant_agents: List[str]


class RequirementAnalyzer:
    """
    Analisador inteligente de requisitos que determina:
    - Tipo de requisito (estratégico, técnico, design, etc.)
    - Complexidade e esforço estimado
    - Agentes relevantes para o requisito
    - Tecnologias e competências necessárias
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._initialize_keywords()
        self._initialize_agent_expertise()
    
    def _initialize_keywords(self):
        """Inicializa palavras-chave para classificação de requisitos"""
        self.keywords = {
            RequirementType.STRATEGIC: [
                "estratégia", "visão", "roadmap", "inovação", "competitivo",
                "mercado", "negócio", "roi", "investimento", "crescimento",
                "escalabilidade", "futuro", "tendência", "oportunidade"
            ],
            
            RequirementType.ARCHITECTURAL: [
                "arquitetura", "design", "padrão", "estrutura", "componente",
                "microserviços", "api", "integração", "performance", "escalabilidade",
                "segurança", "banco de dados", "sistema", "módulo", "interface"
            ],
            
            RequirementType.DEVELOPMENT: [
                "desenvolvimento", "código", "implementação", "programação",
                "frontend", "backend", "fullstack", "framework", "biblioteca",
                "algoritmo", "função", "método", "classe", "teste unitário"
            ],
            
            RequirementType.DESIGN: [
                "design", "ux", "ui", "interface", "usuário", "experiência",
                "usabilidade", "wireframe", "protótipo", "layout", "visual",
                "interação", "navegação", "acessibilidade", "responsivo"
            ],
            
            RequirementType.QUALITY: [
                "qualidade", "teste", "qa", "bug", "defeito", "validação",
                "verificação", "automação", "cobertura", "performance",
                "segurança", "confiabilidade", "estabilidade", "monitoramento"
            ],
            
            RequirementType.INFRASTRUCTURE: [
                "infraestrutura", "devops", "deploy", "ci/cd", "pipeline",
                "servidor", "cloud", "aws", "azure", "docker", "kubernetes",
                "monitoramento", "backup", "segurança", "rede", "banco"
            ],
            
            RequirementType.PROJECT_MANAGEMENT: [
                "projeto", "gerenciamento", "planejamento", "cronograma",
                "recursos", "equipe", "sprint", "scrum", "kanban", "agile",
                "entrega", "milestone", "stakeholder", "comunicação", "risco"
            ],
            
            RequirementType.MOBILE: [
                "mobile", "app", "aplicativo", "ios", "android", "smartphone",
                "tablet", "nativo", "híbrido", "react native", "flutter",
                "offline", "push notification", "gps", "câmera", "sensores"
            ]
        }
    
    def _initialize_agent_expertise(self):
        """Mapeia expertise de cada agente"""
        self.agent_expertise = {
            "ana_beatriz_costa": {
                "primary": [RequirementType.STRATEGIC],
                "secondary": [RequirementType.ARCHITECTURAL, RequirementType.INFRASTRUCTURE],
                "keywords": ["estratégia", "visão", "inovação", "liderança", "negócio"]
            },
            
            "carlos_eduardo_santos": {
                "primary": [RequirementType.ARCHITECTURAL],
                "secondary": [RequirementType.DEVELOPMENT, RequirementType.QUALITY],
                "keywords": ["arquitetura", "design", "padrão", "sistema", "performance"]
            },
            
            "sofia_oliveira": {
                "primary": [RequirementType.DEVELOPMENT],
                "secondary": [RequirementType.ARCHITECTURAL, RequirementType.QUALITY],
                "keywords": ["desenvolvimento", "fullstack", "frontend", "backend", "api"]
            },
            
            "gabriel_mendes": {
                "primary": [RequirementType.MOBILE, RequirementType.DEVELOPMENT],
                "secondary": [RequirementType.DESIGN, RequirementType.QUALITY],
                "keywords": ["mobile", "app", "ios", "android", "nativo", "híbrido"]
            },
            
            "isabella_santos": {
                "primary": [RequirementType.DESIGN],
                "secondary": [RequirementType.MOBILE, RequirementType.DEVELOPMENT],
                "keywords": ["design", "ux", "ui", "usuário", "interface", "experiência"]
            },
            
            "lucas_pereira": {
                "primary": [RequirementType.QUALITY],
                "secondary": [RequirementType.DEVELOPMENT, RequirementType.INFRASTRUCTURE],
                "keywords": ["qualidade", "teste", "qa", "automação", "bug", "validação"]
            },
            
            "mariana_rodrigues": {
                "primary": [RequirementType.INFRASTRUCTURE],
                "secondary": [RequirementType.QUALITY, RequirementType.ARCHITECTURAL],
                "keywords": ["infraestrutura", "devops", "cloud", "deploy", "ci/cd"]
            },
            
            "pedro_henrique_almeida": {
                "primary": [RequirementType.PROJECT_MANAGEMENT],
                "secondary": [RequirementType.STRATEGIC, RequirementType.QUALITY],
                "keywords": ["projeto", "gerenciamento", "agile", "scrum", "planejamento"]
            }
        }
    
    async def analyze(self, requirement: str, available_agents: List[str]) -> List[str]:
        """
        Analisa um requisito e retorna lista de agentes relevantes
        
        Args:
            requirement: Texto do requisito a ser analisado
            available_agents: Lista de agentes disponíveis
            
        Returns:
            Lista de IDs dos agentes relevantes, ordenados por relevância
        """
        # Realizar análise completa
        analysis = await self.analyze_detailed(requirement, available_agents)
        
        return analysis.relevant_agents
    
    async def analyze_detailed(self, requirement: str, available_agents: List[str]) -> RequirementAnalysis:
        """
        Realiza análise detalhada do requisito
        
        Args:
            requirement: Texto do requisito
            available_agents: Lista de agentes disponíveis
            
        Returns:
            Análise detalhada do requisito
        """
        requirement_lower = requirement.lower()
        
        # 1. Classificar tipos de requisito
        requirement_types = self._classify_requirement_types(requirement_lower)
        
        # 2. Calcular complexidade
        complexity_score = self._calculate_complexity(requirement_lower)
        
        # 3. Estimar esforço
        estimated_effort = self._estimate_effort(complexity_score, requirement_types)
        
        # 4. Identificar tecnologias
        key_technologies = self._identify_technologies(requirement_lower)
        
        # 5. Identificar stakeholders
        stakeholders = self._identify_stakeholders(requirement_lower)
        
        # 6. Calcular prioridade
        priority = self._calculate_priority(requirement_types, complexity_score)
        
        # 7. Determinar agentes relevantes
        relevant_agents = self._determine_relevant_agents(
            requirement_lower, requirement_types, available_agents
        )
        
        analysis = RequirementAnalysis(
            requirement_types=requirement_types,
            complexity_score=complexity_score,
            estimated_effort=estimated_effort,
            key_technologies=key_technologies,
            stakeholders=stakeholders,
            priority=priority,
            relevant_agents=relevant_agents
        )
        
        self.logger.info(f"Requisito analisado: {len(relevant_agents)} agentes relevantes")
        return analysis
    
    def _classify_requirement_types(self, requirement: str) -> List[RequirementType]:
        """Classifica os tipos de requisito baseado em palavras-chave"""
        types_found = []
        type_scores = {}
        
        for req_type, keywords in self.keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in requirement:
                    score += 1
            
            if score > 0:
                type_scores[req_type] = score
        
        # Ordenar por score e retornar tipos relevantes
        sorted_types = sorted(type_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Incluir tipos com score significativo
        for req_type, score in sorted_types:
            if score >= 1:  # Pelo menos 1 palavra-chave encontrada
                types_found.append(req_type)
        
        # Se nenhum tipo específico foi encontrado, assumir desenvolvimento geral
        if not types_found:
            types_found.append(RequirementType.DEVELOPMENT)
        
        return types_found[:3]  # Máximo 3 tipos principais
    
    def _calculate_complexity(self, requirement: str) -> float:
        """Calcula score de complexidade (0.0 a 1.0)"""
        complexity_indicators = {
            "simples": -0.2, "fácil": -0.2, "básico": -0.1,
            "complexo": 0.3, "difícil": 0.3, "avançado": 0.2,
            "integração": 0.2, "múltiplos": 0.2, "diversos": 0.1,
            "escalável": 0.2, "distribuído": 0.3, "microserviços": 0.3,
            "machine learning": 0.4, "ia": 0.3, "big data": 0.3,
            "tempo real": 0.3, "alta performance": 0.2,
            "segurança": 0.2, "compliance": 0.2
        }
        
        base_score = 0.5  # Score base médio
        
        for indicator, weight in complexity_indicators.items():
            if indicator in requirement:
                base_score += weight
        
        # Considerar tamanho do requisito
        word_count = len(requirement.split())
        if word_count > 100:
            base_score += 0.1
        elif word_count > 200:
            base_score += 0.2
        
        # Normalizar entre 0.0 e 1.0
        return max(0.0, min(1.0, base_score))
    
    def _estimate_effort(self, complexity: float, types: List[RequirementType]) -> str:
        """Estima esforço baseado na complexidade e tipos"""
        # Multiplicador baseado nos tipos
        type_multipliers = {
            RequirementType.STRATEGIC: 1.2,
            RequirementType.ARCHITECTURAL: 1.3,
            RequirementType.DEVELOPMENT: 1.0,
            RequirementType.DESIGN: 0.8,
            RequirementType.QUALITY: 0.9,
            RequirementType.INFRASTRUCTURE: 1.1,
            RequirementType.PROJECT_MANAGEMENT: 0.7,
            RequirementType.MOBILE: 1.1
        }
        
        avg_multiplier = sum(type_multipliers.get(t, 1.0) for t in types) / len(types)
        adjusted_complexity = complexity * avg_multiplier
        
        if adjusted_complexity < 0.3:
            return "Baixo (1-2 sprints)"
        elif adjusted_complexity < 0.6:
            return "Médio (2-4 sprints)"
        elif adjusted_complexity < 0.8:
            return "Alto (4-8 sprints)"
        else:
            return "Muito Alto (8+ sprints)"
    
    def _identify_technologies(self, requirement: str) -> List[str]:
        """Identifica tecnologias mencionadas no requisito"""
        tech_keywords = {
            "react", "vue", "angular", "javascript", "typescript",
            "node.js", "python", "java", "c#", "go", "rust",
            "postgresql", "mysql", "mongodb", "redis",
            "aws", "azure", "gcp", "docker", "kubernetes",
            "microserviços", "api", "rest", "graphql",
            "machine learning", "ia", "blockchain",
            "ios", "android", "react native", "flutter"
        }
        
        found_technologies = []
        for tech in tech_keywords:
            if tech in requirement:
                found_technologies.append(tech)
        
        return found_technologies[:5]  # Máximo 5 tecnologias
    
    def _identify_stakeholders(self, requirement: str) -> List[str]:
        """Identifica stakeholders mencionados"""
        stakeholder_keywords = {
            "usuário", "cliente", "admin", "administrador",
            "gerente", "diretor", "equipe", "desenvolvedor",
            "designer", "analista", "tester", "devops"
        }
        
        found_stakeholders = []
        for stakeholder in stakeholder_keywords:
            if stakeholder in requirement:
                found_stakeholders.append(stakeholder)
        
        return found_stakeholders
    
    def _calculate_priority(self, types: List[RequirementType], complexity: float) -> int:
        """Calcula prioridade (1-10, sendo 10 mais prioritário)"""
        # Prioridades base por tipo
        type_priorities = {
            RequirementType.STRATEGIC: 9,
            RequirementType.QUALITY: 8,
            RequirementType.ARCHITECTURAL: 7,
            RequirementType.INFRASTRUCTURE: 6,
            RequirementType.DEVELOPMENT: 5,
            RequirementType.DESIGN: 5,
            RequirementType.MOBILE: 5,
            RequirementType.PROJECT_MANAGEMENT: 4
        }
        
        # Calcular prioridade média dos tipos
        avg_priority = sum(type_priorities.get(t, 5) for t in types) / len(types)
        
        # Ajustar pela complexidade (requisitos muito complexos podem ter prioridade menor)
        if complexity > 0.8:
            avg_priority -= 1
        elif complexity < 0.3:
            avg_priority += 1
        
        return max(1, min(10, int(avg_priority)))
    
    def _determine_relevant_agents(self, requirement: str, types: List[RequirementType], 
                                 available_agents: List[str]) -> List[str]:
        """Determina agentes relevantes baseado no requisito e tipos"""
        agent_scores = {}
        
        # Calcular scores para cada agente disponível
        for agent_id in available_agents:
            if agent_id not in self.agent_expertise:
                continue
            
            expertise = self.agent_expertise[agent_id]
            score = 0
            
            # Score por tipos primários
            for req_type in types:
                if req_type in expertise["primary"]:
                    score += 10
                elif req_type in expertise["secondary"]:
                    score += 5
            
            # Score por palavras-chave
            for keyword in expertise["keywords"]:
                if keyword in requirement:
                    score += 2
            
            if score > 0:
                agent_scores[agent_id] = score
        
        # Ordenar por score e retornar
        sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Retornar agentes com score significativo
        relevant_agents = []
        for agent_id, score in sorted_agents:
            if score >= 5:  # Score mínimo para relevância
                relevant_agents.append(agent_id)
        
        # Garantir pelo menos um agente (o mais relevante)
        if not relevant_agents and sorted_agents:
            relevant_agents.append(sorted_agents[0][0])
        
        # Limitar número de agentes para evitar sobrecarga
        return relevant_agents[:5]
    
    def get_analysis_summary(self, analysis: RequirementAnalysis) -> str:
        """Retorna resumo da análise em formato legível"""
        types_str = ", ".join([t.value for t in analysis.requirement_types])
        agents_str = ", ".join(analysis.relevant_agents)
        tech_str = ", ".join(analysis.key_technologies) if analysis.key_technologies else "Não especificadas"
        
        return f"""
**Análise de Requisito**

**Tipos:** {types_str}
**Complexidade:** {analysis.complexity_score:.2f} ({analysis.estimated_effort})
**Prioridade:** {analysis.priority}/10
**Tecnologias:** {tech_str}
**Agentes Relevantes:** {agents_str}
**Stakeholders:** {', '.join(analysis.stakeholders) if analysis.stakeholders else 'Não identificados'}
        """.strip()