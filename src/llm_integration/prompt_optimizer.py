#!/usr/bin/env python3
"""
Prompt Optimizer - Sistema de otimização de prompts por agente
Melhoria #6 - Integração com Modelos de Linguagem
"""

import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """Template de prompt para um agente"""
    agent_id: str
    task_type: str
    template: str
    variables: List[str]
    optimization_notes: str
    performance_score: float = 0.0


@dataclass
class OptimizationRule:
    """Regra de otimização"""
    rule_id: str
    description: str
    pattern: str
    replacement: str
    applies_to: List[str]  # Lista de agent_ids ou "all"


class PromptOptimizer:
    """Otimizador de prompts para agentes CWB Hub"""
    
    def __init__(self):
        self.agent_templates: Dict[str, Dict[str, PromptTemplate]] = {}
        self.optimization_rules: List[OptimizationRule] = []
        self.agent_personalities = {}
        
        self._initialize_agent_personalities()
        self._initialize_optimization_rules()
        self._initialize_agent_templates()
    
    def _initialize_agent_personalities(self):
        """Inicializa personalidades dos agentes"""
        self.agent_personalities = {
            "ana_beatriz_costa": {
                "role": "Chief Technology Officer",
                "style": "estratégico, visionário, focado em inovação",
                "expertise": "liderança tecnológica, estratégia de produto, transformação digital",
                "communication": "executivo, direto, orientado a resultados"
            },
            "carlos_eduardo_santos": {
                "role": "Arquiteto de Software Sênior",
                "style": "técnico, detalhista, focado em qualidade",
                "expertise": "arquitetura de sistemas, padrões de design, escalabilidade",
                "communication": "técnico, preciso, orientado a melhores práticas"
            },
            "sofia_oliveira": {
                "role": "Engenheira Full Stack",
                "style": "prático, versátil, focado em implementação",
                "expertise": "desenvolvimento web, APIs, integração de sistemas",
                "communication": "prático, claro, orientado a soluções"
            },
            "gabriel_mendes": {
                "role": "Engenheiro Mobile",
                "style": "inovador, focado em UX, orientado a performance",
                "expertise": "desenvolvimento mobile, UX mobile, otimização",
                "communication": "moderno, focado no usuário, orientado a experiência"
            },
            "isabella_santos": {
                "role": "Designer UX/UI Sênior",
                "style": "criativo, empático, focado no usuário",
                "expertise": "design de experiência, pesquisa de usuário, prototipagem",
                "communication": "visual, empático, orientado ao usuário"
            },
            "lucas_pereira": {
                "role": "Engenheiro de QA",
                "style": "meticuloso, sistemático, focado em qualidade",
                "expertise": "testes automatizados, qualidade de software, CI/CD",
                "communication": "sistemático, detalhado, orientado a qualidade"
            },
            "mariana_rodrigues": {
                "role": "Engenheira DevOps",
                "style": "eficiente, automatizado, focado em confiabilidade",
                "expertise": "infraestrutura, automação, monitoramento",
                "communication": "eficiente, técnico, orientado a automação"
            },
            "pedro_henrique_almeida": {
                "role": "Agile Project Manager",
                "style": "colaborativo, organizador, focado em entrega",
                "expertise": "metodologias ágeis, gestão de equipes, entrega contínua",
                "communication": "colaborativo, organizador, orientado a resultados"
            }
        }
    
    def _initialize_optimization_rules(self):
        """Inicializa regras de otimização"""
        self.optimization_rules = [
            OptimizationRule(
                rule_id="remove_redundancy",
                description="Remove redundâncias e repetições",
                pattern=r"\b(\w+)\s+\1\b",
                replacement=r"\1",
                applies_to=["all"]
            ),
            OptimizationRule(
                rule_id="technical_precision",
                description="Adiciona precisão técnica para agentes técnicos",
                pattern=r"sistema",
                replacement="sistema/arquitetura",
                applies_to=["carlos_eduardo_santos", "sofia_oliveira", "mariana_rodrigues"]
            ),
            OptimizationRule(
                rule_id="user_focus",
                description="Enfatiza foco no usuário para designers",
                pattern=r"interface",
                replacement="experiência do usuário e interface",
                applies_to=["isabella_santos", "gabriel_mendes"]
            ),
            OptimizationRule(
                rule_id="quality_emphasis",
                description="Enfatiza qualidade para QA",
                pattern=r"teste",
                replacement="teste abrangente e validação de qualidade",
                applies_to=["lucas_pereira"]
            ),
            OptimizationRule(
                rule_id="strategic_context",
                description="Adiciona contexto estratégico para liderança",
                pattern=r"solução",
                replacement="solução estratégica alinhada aos objetivos de negócio",
                applies_to=["ana_beatriz_costa", "pedro_henrique_almeida"]
            )
        ]
    
    def _initialize_agent_templates(self):
        """Inicializa templates base para cada agente"""
        base_templates = {
            "analysis": """Como {role}, analise o seguinte requisito considerando sua expertise em {expertise}:

Requisito: {prompt}

Forneça uma análise {style} que inclua:
1. Avaliação técnica/estratégica
2. Considerações importantes
3. Recomendações específicas
4. Próximos passos

Mantenha um tom {communication} e foque em soluções práticas.""",
            
            "collaboration": """Como {role}, colabore na seguinte discussão:

Contexto: {context}
Tópico: {prompt}

Contribua com sua perspectiva em {expertise}, mantendo um estilo {style}.
Considere as contribuições de outros especialistas e forneça insights únicos da sua área.""",
            
            "solution": """Como {role}, proponha uma solução para:

Problema: {prompt}
Restrições: {constraints}

Desenvolva uma proposta {style} que:
1. Aborde o problema central
2. Considere as restrições mencionadas
3. Aproveite sua expertise em {expertise}
4. Seja implementável e prática

Use comunicação {communication}."""
        }
        
        # Criar templates para cada agente
        for agent_id, personality in self.agent_personalities.items():
            self.agent_templates[agent_id] = {}
            
            for task_type, template in base_templates.items():
                optimized_template = self._customize_template_for_agent(
                    template, agent_id, personality
                )
                
                self.agent_templates[agent_id][task_type] = PromptTemplate(
                    agent_id=agent_id,
                    task_type=task_type,
                    template=optimized_template,
                    variables=self._extract_variables(optimized_template),
                    optimization_notes=f"Customizado para {personality['role']}"
                )
    
    def _customize_template_for_agent(self, template: str, agent_id: str, personality: Dict[str, str]) -> str:
        """Customiza template para um agente específico"""
        # Substituir variáveis de personalidade
        customized = template.format(
            role=personality["role"],
            style=personality["style"],
            expertise=personality["expertise"],
            communication=personality["communication"],
            prompt="{prompt}",  # Manter como variável
            context="{context}",  # Manter como variável
            constraints="{constraints}"  # Manter como variável
        )
        
        # Adicionar customizações específicas por agente
        if agent_id == "ana_beatriz_costa":
            customized += "\n\nConsidere também o impacto estratégico e ROI da solução proposta."
        elif agent_id == "carlos_eduardo_santos":
            customized += "\n\nIncluir considerações de arquitetura, escalabilidade e manutenibilidade."
        elif agent_id == "sofia_oliveira":
            customized += "\n\nFocar em implementação prática e integração com sistemas existentes."
        elif agent_id == "gabriel_mendes":
            customized += "\n\nConsiderar performance mobile, UX e compatibilidade entre plataformas."
        elif agent_id == "isabella_santos":
            customized += "\n\nPriorizar experiência do usuário, acessibilidade e design inclusivo."
        elif agent_id == "lucas_pereira":
            customized += "\n\nDefinir estratégia de testes, critérios de qualidade e validação."
        elif agent_id == "mariana_rodrigues":
            customized += "\n\nIncluir aspectos de infraestrutura, deploy, monitoramento e automação."
        elif agent_id == "pedro_henrique_almeida":
            customized += "\n\nConsiderar cronograma, recursos, riscos e metodologia de entrega."
        
        return customized
    
    def _extract_variables(self, template: str) -> List[str]:
        """Extrai variáveis do template"""
        variables = re.findall(r'\{(\w+)\}', template)
        return list(set(variables))
    
    async def optimize_prompt(self, prompt: str, agent_id: str, task_type: str = "analysis") -> str:
        """Otimiza prompt para um agente específico"""
        try:
            # Aplicar regras de otimização
            optimized_prompt = self._apply_optimization_rules(prompt, agent_id)
            
            # Usar template do agente se disponível
            if agent_id in self.agent_templates and task_type in self.agent_templates[agent_id]:
                template = self.agent_templates[agent_id][task_type]
                
                # Substituir variáveis no template
                formatted_prompt = template.template.format(
                    prompt=optimized_prompt,
                    context="",  # Pode ser fornecido separadamente
                    constraints=""  # Pode ser fornecido separadamente
                )
                
                return formatted_prompt
            else:
                # Fallback para prompt básico otimizado
                return self._create_basic_optimized_prompt(optimized_prompt, agent_id)
                
        except Exception as e:
            logger.warning(f"⚠️ Erro na otimização de prompt: {e}")
            return prompt  # Retornar prompt original em caso de erro
    
    def _apply_optimization_rules(self, prompt: str, agent_id: str) -> str:
        """Aplica regras de otimização ao prompt"""
        optimized = prompt
        
        for rule in self.optimization_rules:
            # Verificar se a regra se aplica ao agente
            if "all" in rule.applies_to or agent_id in rule.applies_to:
                optimized = re.sub(rule.pattern, rule.replacement, optimized, flags=re.IGNORECASE)
        
        return optimized
    
    def _create_basic_optimized_prompt(self, prompt: str, agent_id: str) -> str:
        """Cria prompt básico otimizado quando template não está disponível"""
        if agent_id not in self.agent_personalities:
            return prompt
        
        personality = self.agent_personalities[agent_id]
        
        return f"""Como {personality['role']}, considerando sua expertise em {personality['expertise']}:

{prompt}

Forneça uma resposta {personality['style']} com comunicação {personality['communication']}."""
    
    async def get_agent_optimization(self, agent_id: str, task_type: str) -> Dict[str, Any]:
        """Retorna informações de otimização para um agente"""
        if agent_id not in self.agent_personalities:
            return {"error": f"Agente {agent_id} não encontrado"}
        
        personality = self.agent_personalities[agent_id]
        templates = self.agent_templates.get(agent_id, {})
        
        applicable_rules = [
            rule for rule in self.optimization_rules
            if "all" in rule.applies_to or agent_id in rule.applies_to
        ]
        
        return {
            "agent_id": agent_id,
            "personality": personality,
            "available_templates": list(templates.keys()),
            "applicable_rules": [
                {
                    "rule_id": rule.rule_id,
                    "description": rule.description
                }
                for rule in applicable_rules
            ],
            "optimization_tips": self._get_optimization_tips(agent_id)
        }
    
    def _get_optimization_tips(self, agent_id: str) -> List[str]:
        """Retorna dicas de otimização para um agente"""
        tips = [
            "Use linguagem clara e específica",
            "Forneça contexto suficiente",
            "Seja específico sobre o que você espera"
        ]
        
        if agent_id == "ana_beatriz_costa":
            tips.extend([
                "Inclua contexto de negócio e impacto estratégico",
                "Mencione objetivos de longo prazo",
                "Considere aspectos de liderança e visão"
            ])
        elif agent_id == "carlos_eduardo_santos":
            tips.extend([
                "Forneça detalhes técnicos relevantes",
                "Mencione requisitos de escalabilidade",
                "Inclua considerações de arquitetura"
            ])
        elif agent_id == "isabella_santos":
            tips.extend([
                "Descreva o público-alvo",
                "Mencione requisitos de acessibilidade",
                "Inclua contexto de experiência do usuário"
            ])
        elif agent_id == "lucas_pereira":
            tips.extend([
                "Especifique critérios de qualidade",
                "Mencione cenários de teste importantes",
                "Inclua requisitos de performance"
            ])
        
        return tips
    
    async def add_custom_template(
        self,
        agent_id: str,
        task_type: str,
        template: str,
        optimization_notes: str = ""
    ) -> bool:
        """Adiciona template customizado para um agente"""
        try:
            if agent_id not in self.agent_templates:
                self.agent_templates[agent_id] = {}
            
            self.agent_templates[agent_id][task_type] = PromptTemplate(
                agent_id=agent_id,
                task_type=task_type,
                template=template,
                variables=self._extract_variables(template),
                optimization_notes=optimization_notes
            )
            
            logger.info(f"✅ Template customizado adicionado: {agent_id}/{task_type}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao adicionar template: {e}")
            return False
    
    async def get_optimization_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de otimização"""
        total_templates = sum(len(templates) for templates in self.agent_templates.values())
        
        return {
            "total_agents": len(self.agent_personalities),
            "total_templates": total_templates,
            "total_rules": len(self.optimization_rules),
            "templates_per_agent": {
                agent_id: len(templates)
                for agent_id, templates in self.agent_templates.items()
            },
            "available_task_types": list(set(
                task_type
                for templates in self.agent_templates.values()
                for task_type in templates.keys()
            ))
        }
    
    async def validate_prompt(self, prompt: str, agent_id: str) -> Dict[str, Any]:
        """Valida qualidade de um prompt"""
        issues = []
        suggestions = []
        score = 100
        
        # Verificar comprimento
        if len(prompt) < 10:
            issues.append("Prompt muito curto")
            suggestions.append("Forneça mais contexto e detalhes")
            score -= 20
        elif len(prompt) > 2000:
            issues.append("Prompt muito longo")
            suggestions.append("Considere dividir em partes menores")
            score -= 10
        
        # Verificar clareza
        if "?" not in prompt and not any(word in prompt.lower() for word in ["analise", "desenvolva", "crie", "implemente"]):
            issues.append("Objetivo não claro")
            suggestions.append("Use verbos de ação claros (analise, desenvolva, crie)")
            score -= 15
        
        # Verificar contexto
        if agent_id in self.agent_personalities:
            personality = self.agent_personalities[agent_id]
            expertise_keywords = personality["expertise"].lower().split(", ")
            
            if not any(keyword in prompt.lower() for keyword in expertise_keywords):
                suggestions.append(f"Considere mencionar aspectos de {personality['expertise']}")
                score -= 5
        
        return {
            "score": max(score, 0),
            "issues": issues,
            "suggestions": suggestions,
            "quality": "excellent" if score >= 90 else "good" if score >= 70 else "needs_improvement"
        }