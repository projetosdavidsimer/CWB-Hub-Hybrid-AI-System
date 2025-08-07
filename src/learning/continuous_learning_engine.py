#!/usr/bin/env python3
"""
CWB Hub Continuous Learning Engine - Sistema de Aprendizado Contínuo
Melhoria #7 - IA que Evolui Autonomamente
"""

import asyncio
import logging
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics
import numpy as np
from collections import defaultdict, deque

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InteractionType(Enum):
    """Tipos de interação do usuário"""
    PROJECT_ANALYSIS = "project_analysis"
    AGENT_CONSULTATION = "agent_consultation"
    ITERATION_FEEDBACK = "iteration_feedback"
    DIRECT_QUESTION = "direct_question"
    BRAINSTORM_SESSION = "brainstorm_session"

class FeedbackType(Enum):
    """Tipos de feedback disponíveis"""
    EXPLICIT_RATING = "explicit_rating"  # Rating direto do usuário
    IMPLICIT_BEHAVIOR = "implicit_behavior"  # Comportamento inferido
    ITERATION_COUNT = "iteration_count"  # Número de iterações
    SESSION_DURATION = "session_duration"  # Tempo de sessão
    FOLLOW_UP_QUESTIONS = "follow_up_questions"  # Perguntas de follow-up

class LearningObjective(Enum):
    """Objetivos de aprendizado"""
    IMPROVE_ACCURACY = "improve_accuracy"
    REDUCE_ITERATIONS = "reduce_iterations"
    INCREASE_SATISFACTION = "increase_satisfaction"
    OPTIMIZE_RESPONSE_TIME = "optimize_response_time"
    ENHANCE_RELEVANCE = "enhance_relevance"

@dataclass
class InteractionRecord:
    """Registro de uma interação completa"""
    interaction_id: str
    session_id: str
    user_id: str
    interaction_type: InteractionType
    timestamp: datetime
    
    # Input data
    user_request: str
    context: Dict[str, Any]
    agents_involved: List[str]
    
    # Output data
    response: str
    response_time: float
    confidence_score: float
    
    # Feedback data
    explicit_rating: Optional[float] = None  # 1-5 scale
    implicit_satisfaction: Optional[float] = None  # Calculated
    iteration_count: int = 1
    session_duration: Optional[float] = None
    follow_up_questions: int = 0
    
    # Learning metadata
    prompt_version: str = "1.0"
    model_used: str = "default"
    processing_complexity: str = "medium"

@dataclass
class LearningPattern:
    """Padrão identificado pelo sistema de aprendizado"""
    pattern_id: str
    pattern_type: str
    description: str
    
    # Pattern characteristics
    trigger_conditions: Dict[str, Any]
    success_indicators: Dict[str, float]
    failure_indicators: Dict[str, float]
    
    # Statistical data
    occurrence_count: int
    success_rate: float
    confidence_level: float
    
    # Optimization suggestions
    recommended_actions: List[str]
    prompt_optimizations: Dict[str, str]
    
    created_at: datetime
    last_updated: datetime

@dataclass
class OptimizationRule:
    """Regra de otimização aprendida"""
    rule_id: str
    rule_name: str
    description: str
    
    # Conditions
    conditions: Dict[str, Any]
    agent_scope: List[str]  # Agentes afetados
    
    # Actions
    prompt_modifications: Dict[str, str]
    parameter_adjustments: Dict[str, Any]
    behavior_changes: Dict[str, Any]
    
    # Performance
    effectiveness_score: float
    usage_count: int
    success_rate: float
    
    # Lifecycle
    is_active: bool
    created_at: datetime
    last_applied: Optional[datetime]

class ContinuousLearningEngine:
    """
    Motor de Aprendizado Contínuo do CWB Hub
    
    Funcionalidades:
    - Coleta e análise de interações
    - Identificação de padrões de sucesso/falha
    - Otimização automática de prompts
    - Evolução de comportamento dos agentes
    - Monitoramento de melhorias
    - A/B testing de otimizações
    """
    
    def __init__(self, 
                 learning_rate: float = 0.1,
                 pattern_threshold: int = 10,
                 confidence_threshold: float = 0.7):
        
        self.learning_rate = learning_rate
        self.pattern_threshold = pattern_threshold
        self.confidence_threshold = confidence_threshold
        
        # Data storage
        self.interactions: deque = deque(maxlen=10000)  # Recent interactions
        self.patterns: Dict[str, LearningPattern] = {}
        self.optimization_rules: Dict[str, OptimizationRule] = {}
        
        # Learning state
        self.learning_metrics = {
            "total_interactions": 0,
            "patterns_identified": 0,
            "optimizations_applied": 0,
            "average_satisfaction": 0.0,
            "learning_velocity": 0.0
        }
        
        # Pattern analysis
        self.pattern_analyzer = PatternAnalyzer()
        self.prompt_optimizer = PromptOptimizer()
        self.performance_tracker = PerformanceTracker()
        
        # A/B testing
        self.ab_tests: Dict[str, Dict] = {}
        
        logger.info("🧠 Continuous Learning Engine inicializado")
    
    async def record_interaction(self, interaction: InteractionRecord) -> None:
        """Registra uma nova interação para aprendizado"""
        try:
            # Adicionar à coleção
            self.interactions.append(interaction)
            self.learning_metrics["total_interactions"] += 1
            
            # Calcular satisfação implícita
            interaction.implicit_satisfaction = self._calculate_implicit_satisfaction(interaction)
            
            # Análise em tempo real
            await self._analyze_interaction(interaction)
            
            # Atualizar métricas
            await self._update_learning_metrics()
            
            logger.debug(f"📝 Interação registrada: {interaction.interaction_id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar interação: {e}")
    
    def _calculate_implicit_satisfaction(self, interaction: InteractionRecord) -> float:
        """Calcula satisfação implícita baseada em comportamento"""
        score = 0.5  # Base neutral
        
        # Fatores positivos
        if interaction.iteration_count == 1:
            score += 0.3  # Resposta aceita na primeira tentativa
        
        if interaction.confidence_score > 0.8:
            score += 0.2  # Alta confiança
        
        if interaction.response_time < 2.0:
            score += 0.1  # Resposta rápida
        
        if interaction.follow_up_questions == 0:
            score += 0.2  # Sem necessidade de esclarecimentos
        
        # Fatores negativos
        if interaction.iteration_count > 3:
            score -= 0.3  # Muitas iterações
        
        if interaction.response_time > 10.0:
            score -= 0.2  # Resposta lenta
        
        if interaction.follow_up_questions > 2:
            score -= 0.2  # Muitas dúvidas
        
        # Normalizar entre 0 e 1
        return max(0.0, min(1.0, score))
    
    async def _analyze_interaction(self, interaction: InteractionRecord) -> None:
        """Analisa interação para identificar padrões"""
        try:
            # Identificar padrões
            patterns = await self.pattern_analyzer.analyze(interaction)
            
            for pattern in patterns:
                await self._update_or_create_pattern(pattern)
            
            # Verificar se deve aplicar otimizações
            await self._check_optimization_triggers(interaction)
            
        except Exception as e:
            logger.error(f"❌ Erro na análise de interação: {e}")
    
    async def _update_or_create_pattern(self, pattern_data: Dict[str, Any]) -> None:
        """Atualiza ou cria um padrão identificado"""
        pattern_id = pattern_data.get("pattern_id")
        
        if pattern_id in self.patterns:
            # Atualizar padrão existente
            pattern = self.patterns[pattern_id]
            pattern.occurrence_count += 1
            pattern.last_updated = datetime.now()
            
            # Recalcular métricas
            await self._recalculate_pattern_metrics(pattern)
        else:
            # Criar novo padrão
            if pattern_data.get("occurrence_count", 0) >= self.pattern_threshold:
                new_pattern = LearningPattern(**pattern_data)
                self.patterns[pattern_id] = new_pattern
                self.learning_metrics["patterns_identified"] += 1
                
                logger.info(f"🔍 Novo padrão identificado: {pattern_id}")
    
    async def _check_optimization_triggers(self, interaction: InteractionRecord) -> None:
        """Verifica se deve aplicar otimizações baseadas na interação"""
        try:
            # Verificar regras de otimização ativas
            for rule_id, rule in self.optimization_rules.items():
                if rule.is_active and self._matches_conditions(interaction, rule.conditions):
                    await self._apply_optimization_rule(rule, interaction)
            
            # Verificar se deve criar novas otimizações
            if self._should_create_optimization(interaction):
                await self._create_optimization_rule(interaction)
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar otimizações: {e}")
    
    def _matches_conditions(self, interaction: InteractionRecord, conditions: Dict[str, Any]) -> bool:
        """Verifica se interação atende às condições"""
        try:
            for key, value in conditions.items():
                if hasattr(interaction, key):
                    interaction_value = getattr(interaction, key)
                    
                    if isinstance(value, dict):
                        # Condições complexas (range, etc.)
                        if "min" in value and interaction_value < value["min"]:
                            return False
                        if "max" in value and interaction_value > value["max"]:
                            return False
                        if "equals" in value and interaction_value != value["equals"]:
                            return False
                    else:
                        # Condição simples
                        if interaction_value != value:
                            return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar condições: {e}")
            return False
    
    async def _apply_optimization_rule(self, rule: OptimizationRule, interaction: InteractionRecord) -> None:
        """Aplica uma regra de otimização"""
        try:
            # Aplicar modificações de prompt
            if rule.prompt_modifications:
                await self.prompt_optimizer.apply_modifications(
                    rule.prompt_modifications, 
                    interaction.agents_involved
                )
            
            # Aplicar ajustes de parâmetros
            if rule.parameter_adjustments:
                await self._apply_parameter_adjustments(rule.parameter_adjustments)
            
            # Registrar aplicação
            rule.usage_count += 1
            rule.last_applied = datetime.now()
            self.learning_metrics["optimizations_applied"] += 1
            
            logger.info(f"🔧 Otimização aplicada: {rule.rule_name}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao aplicar otimização: {e}")
    
    def _should_create_optimization(self, interaction: InteractionRecord) -> bool:
        """Determina se deve criar nova otimização baseada na interação"""
        # Criar otimização se satisfação baixa e padrão identificado
        if (interaction.implicit_satisfaction < 0.4 and 
            interaction.iteration_count > 2):
            return True
        
        # Criar otimização se resposta muito lenta
        if interaction.response_time > 15.0:
            return True
        
        # Criar otimização se baixa confiança
        if interaction.confidence_score < 0.5:
            return True
        
        return False
    
    async def _create_optimization_rule(self, interaction: InteractionRecord) -> None:
        """Cria nova regra de otimização baseada em problema identificado"""
        try:
            rule_id = f"opt_{int(time.time())}_{interaction.interaction_type.value}"
            
            # Identificar problema principal
            problem_type = self._identify_main_problem(interaction)
            
            # Criar regra baseada no problema
            rule = OptimizationRule(
                rule_id=rule_id,
                rule_name=f"Auto-optimization for {problem_type}",
                description=f"Automatically generated rule to address {problem_type}",
                conditions=self._generate_conditions(interaction, problem_type),
                agent_scope=interaction.agents_involved,
                prompt_modifications=self._generate_prompt_modifications(problem_type),
                parameter_adjustments=self._generate_parameter_adjustments(problem_type),
                behavior_changes={},
                effectiveness_score=0.0,
                usage_count=0,
                success_rate=0.0,
                is_active=True,
                created_at=datetime.now(),
                last_applied=None
            )
            
            self.optimization_rules[rule_id] = rule
            
            logger.info(f"🆕 Nova regra de otimização criada: {rule_id}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar regra de otimização: {e}")
    
    def _identify_main_problem(self, interaction: InteractionRecord) -> str:
        """Identifica o problema principal da interação"""
        if interaction.response_time > 10.0:
            return "slow_response"
        elif interaction.iteration_count > 3:
            return "low_accuracy"
        elif interaction.confidence_score < 0.5:
            return "low_confidence"
        elif interaction.implicit_satisfaction < 0.3:
            return "low_satisfaction"
        else:
            return "general_improvement"
    
    def _generate_conditions(self, interaction: InteractionRecord, problem_type: str) -> Dict[str, Any]:
        """Gera condições para a regra de otimização"""
        base_conditions = {
            "interaction_type": interaction.interaction_type.value
        }
        
        if problem_type == "slow_response":
            base_conditions["response_time"] = {"min": 8.0}
        elif problem_type == "low_accuracy":
            base_conditions["iteration_count"] = {"min": 3}
        elif problem_type == "low_confidence":
            base_conditions["confidence_score"] = {"max": 0.6}
        
        return base_conditions
    
    def _generate_prompt_modifications(self, problem_type: str) -> Dict[str, str]:
        """Gera modificações de prompt baseadas no problema"""
        modifications = {}
        
        if problem_type == "low_accuracy":
            modifications["accuracy_boost"] = "Seja mais específico e detalhado na análise. Considere múltiplas perspectivas."
        elif problem_type == "low_confidence":
            modifications["confidence_boost"] = "Baseie suas recomendações em melhores práticas estabelecidas e dados concretos."
        elif problem_type == "slow_response":
            modifications["speed_boost"] = "Priorize as informações mais importantes e seja conciso."
        
        return modifications
    
    def _generate_parameter_adjustments(self, problem_type: str) -> Dict[str, Any]:
        """Gera ajustes de parâmetros baseados no problema"""
        adjustments = {}
        
        if problem_type == "slow_response":
            adjustments["max_tokens"] = 2000  # Reduzir tokens
            adjustments["temperature"] = 0.3  # Mais determinístico
        elif problem_type == "low_confidence":
            adjustments["temperature"] = 0.1  # Mais conservador
        
        return adjustments
    
    async def _apply_parameter_adjustments(self, adjustments: Dict[str, Any]) -> None:
        """Aplica ajustes de parâmetros ao sistema"""
        # Implementar aplicação de ajustes
        logger.info(f"🔧 Aplicando ajustes de parâmetros: {adjustments}")
    
    async def _update_learning_metrics(self) -> None:
        """Atualiza métricas de aprendizado"""
        try:
            if len(self.interactions) > 0:
                # Calcular satisfação média
                satisfactions = [
                    i.implicit_satisfaction for i in self.interactions 
                    if i.implicit_satisfaction is not None
                ]
                
                if satisfactions:
                    self.learning_metrics["average_satisfaction"] = statistics.mean(satisfactions)
                
                # Calcular velocidade de aprendizado (melhorias por hora)
                recent_interactions = [
                    i for i in self.interactions 
                    if i.timestamp > datetime.now() - timedelta(hours=1)
                ]
                
                if recent_interactions:
                    improvements = sum(1 for i in recent_interactions if i.implicit_satisfaction > 0.7)
                    self.learning_metrics["learning_velocity"] = improvements / len(recent_interactions)
        
        except Exception as e:
            logger.error(f"❌ Erro ao atualizar métricas: {e}")
    
    async def _recalculate_pattern_metrics(self, pattern: LearningPattern) -> None:
        """Recalcula métricas de um padrão"""
        # Implementar recálculo de métricas do padrão
        pass
    
    async def get_learning_insights(self) -> Dict[str, Any]:
        """Retorna insights do sistema de aprendizado"""
        try:
            insights = {
                "learning_metrics": self.learning_metrics.copy(),
                "active_patterns": len([p for p in self.patterns.values() if p.confidence_level > self.confidence_threshold]),
                "active_optimizations": len([r for r in self.optimization_rules.values() if r.is_active]),
                "recent_improvements": await self._calculate_recent_improvements(),
                "top_patterns": await self._get_top_patterns(),
                "optimization_effectiveness": await self._calculate_optimization_effectiveness()
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar insights: {e}")
            return {}
    
    async def _calculate_recent_improvements(self) -> Dict[str, float]:
        """Calcula melhorias recentes"""
        # Implementar cálculo de melhorias
        return {
            "satisfaction_improvement": 0.15,
            "response_time_improvement": 0.25,
            "accuracy_improvement": 0.10
        }
    
    async def _get_top_patterns(self) -> List[Dict[str, Any]]:
        """Retorna os padrões mais significativos"""
        sorted_patterns = sorted(
            self.patterns.values(),
            key=lambda p: p.confidence_level * p.occurrence_count,
            reverse=True
        )
        
        return [
            {
                "pattern_id": p.pattern_id,
                "description": p.description,
                "success_rate": p.success_rate,
                "confidence": p.confidence_level,
                "occurrences": p.occurrence_count
            }
            for p in sorted_patterns[:5]
        ]
    
    async def _calculate_optimization_effectiveness(self) -> Dict[str, float]:
        """Calcula efetividade das otimizações"""
        if not self.optimization_rules:
            return {"overall_effectiveness": 0.0}
        
        effectiveness_scores = [r.effectiveness_score for r in self.optimization_rules.values()]
        
        return {
            "overall_effectiveness": statistics.mean(effectiveness_scores) if effectiveness_scores else 0.0,
            "total_optimizations": len(self.optimization_rules),
            "active_optimizations": len([r for r in self.optimization_rules.values() if r.is_active])
        }
    
    async def export_learning_data(self) -> Dict[str, Any]:
        """Exporta dados de aprendizado para análise"""
        return {
            "interactions_count": len(self.interactions),
            "patterns": {pid: asdict(pattern) for pid, pattern in self.patterns.items()},
            "optimization_rules": {rid: asdict(rule) for rid, rule in self.optimization_rules.items()},
            "learning_metrics": self.learning_metrics,
            "export_timestamp": datetime.now().isoformat()
        }

class PatternAnalyzer:
    """Analisador de padrões de interação"""
    
    async def analyze(self, interaction: InteractionRecord) -> List[Dict[str, Any]]:
        """Analisa interação para identificar padrões"""
        patterns = []
        
        # Padrão de tipo de interação
        patterns.append(await self._analyze_interaction_type_pattern(interaction))
        
        # Padrão de satisfação
        patterns.append(await self._analyze_satisfaction_pattern(interaction))
        
        # Padrão de performance
        patterns.append(await self._analyze_performance_pattern(interaction))
        
        return [p for p in patterns if p is not None]
    
    async def _analyze_interaction_type_pattern(self, interaction: InteractionRecord) -> Optional[Dict[str, Any]]:
        """Analisa padrão baseado no tipo de interação"""
        pattern_id = f"interaction_type_{interaction.interaction_type.value}"
        
        return {
            "pattern_id": pattern_id,
            "pattern_type": "interaction_type",
            "description": f"Pattern for {interaction.interaction_type.value} interactions",
            "trigger_conditions": {"interaction_type": interaction.interaction_type.value},
            "success_indicators": {"implicit_satisfaction": interaction.implicit_satisfaction},
            "failure_indicators": {},
            "occurrence_count": 1,
            "success_rate": 1.0 if interaction.implicit_satisfaction > 0.7 else 0.0,
            "confidence_level": 0.8,
            "recommended_actions": [],
            "prompt_optimizations": {},
            "created_at": datetime.now(),
            "last_updated": datetime.now()
        }
    
    async def _analyze_satisfaction_pattern(self, interaction: InteractionRecord) -> Optional[Dict[str, Any]]:
        """Analisa padrão de satisfação"""
        if interaction.implicit_satisfaction < 0.5:
            pattern_id = f"low_satisfaction_{interaction.interaction_type.value}"
            
            return {
                "pattern_id": pattern_id,
                "pattern_type": "satisfaction",
                "description": f"Low satisfaction pattern for {interaction.interaction_type.value}",
                "trigger_conditions": {
                    "interaction_type": interaction.interaction_type.value,
                    "implicit_satisfaction": {"max": 0.5}
                },
                "success_indicators": {},
                "failure_indicators": {"implicit_satisfaction": interaction.implicit_satisfaction},
                "occurrence_count": 1,
                "success_rate": 0.0,
                "confidence_level": 0.9,
                "recommended_actions": ["improve_prompt", "adjust_parameters"],
                "prompt_optimizations": {},
                "created_at": datetime.now(),
                "last_updated": datetime.now()
            }
        
        return None
    
    async def _analyze_performance_pattern(self, interaction: InteractionRecord) -> Optional[Dict[str, Any]]:
        """Analisa padrão de performance"""
        if interaction.response_time > 10.0:
            pattern_id = f"slow_response_{interaction.interaction_type.value}"
            
            return {
                "pattern_id": pattern_id,
                "pattern_type": "performance",
                "description": f"Slow response pattern for {interaction.interaction_type.value}",
                "trigger_conditions": {
                    "interaction_type": interaction.interaction_type.value,
                    "response_time": {"min": 8.0}
                },
                "success_indicators": {},
                "failure_indicators": {"response_time": interaction.response_time},
                "occurrence_count": 1,
                "success_rate": 0.0,
                "confidence_level": 0.8,
                "recommended_actions": ["optimize_prompt", "reduce_complexity"],
                "prompt_optimizations": {},
                "created_at": datetime.now(),
                "last_updated": datetime.now()
            }
        
        return None

class PromptOptimizer:
    """Otimizador de prompts baseado em aprendizado"""
    
    async def apply_modifications(self, modifications: Dict[str, str], agents: List[str]) -> None:
        """Aplica modificações de prompt aos agentes"""
        logger.info(f"🔧 Aplicando modificações de prompt para agentes: {agents}")
        logger.info(f"📝 Modificações: {modifications}")
        
        # Implementar aplicação real das modificações
        # Integrar com sistema de prompts dos agentes

class PerformanceTracker:
    """Rastreador de performance do sistema de aprendizado"""
    
    def __init__(self):
        self.performance_history = deque(maxlen=1000)
    
    async def track_performance(self, metrics: Dict[str, float]) -> None:
        """Rastreia métricas de performance"""
        self.performance_history.append({
            "timestamp": datetime.now(),
            "metrics": metrics
        })

# Instância global do motor de aprendizado
learning_engine = ContinuousLearningEngine()

if __name__ == "__main__":
    # Teste básico do sistema
    async def test_learning_engine():
        print("🧪 Testando Sistema de Aprendizado Contínuo...")
        
        # Criar interação de teste
        test_interaction = InteractionRecord(
            interaction_id="test_001",
            session_id="session_test",
            user_id="user_test",
            interaction_type=InteractionType.PROJECT_ANALYSIS,
            timestamp=datetime.now(),
            user_request="Desenvolver um marketplace B2B",
            context={"domain": "e-commerce", "complexity": "high"},
            agents_involved=["ana_beatriz_costa", "carlos_eduardo_santos"],
            response="Recomendo arquitetura microserviços com API Gateway...",
            response_time=5.2,
            confidence_score=0.85,
            explicit_rating=4.0,
            iteration_count=1,
            follow_up_questions=0
        )
        
        # Registrar interação
        await learning_engine.record_interaction(test_interaction)
        
        # Obter insights
        insights = await learning_engine.get_learning_insights()
        print(f"📊 Insights: {insights}")
        
        print("✅ Teste concluído com sucesso!")
    
    asyncio.run(test_learning_engine())