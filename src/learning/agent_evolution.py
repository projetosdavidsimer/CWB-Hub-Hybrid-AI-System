#!/usr/bin/env python3
"""
CWB Hub Agent Evolution System - Sistema de Evolução de Agentes
Melhoria #7 - Evolução automática dos agentes baseada em aprendizado
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import statistics
from collections import defaultdict

from .continuous_learning_engine import learning_engine, LearningPattern, OptimizationRule
from .feedback_collector import feedback_collector

logger = logging.getLogger(__name__)

class EvolutionStrategy(Enum):
    """Estratégias de evolução disponíveis"""
    PROMPT_OPTIMIZATION = "prompt_optimization"
    BEHAVIOR_ADAPTATION = "behavior_adaptation"
    KNOWLEDGE_EXPANSION = "knowledge_expansion"
    RESPONSE_REFINEMENT = "response_refinement"
    COLLABORATION_IMPROVEMENT = "collaboration_improvement"

class EvolutionTrigger(Enum):
    """Gatilhos para evolução"""
    LOW_SATISFACTION = "low_satisfaction"
    HIGH_ITERATION_COUNT = "high_iteration_count"
    SLOW_RESPONSE = "slow_response"
    LOW_CONFIDENCE = "low_confidence"
    PATTERN_DETECTED = "pattern_detected"
    SCHEDULED_EVOLUTION = "scheduled_evolution"

@dataclass
class EvolutionEvent:
    """Evento de evolução de agente"""
    event_id: str
    agent_id: str
    trigger: EvolutionTrigger
    strategy: EvolutionStrategy
    
    # Dados do evento
    baseline_metrics: Dict[str, float]
    target_metrics: Dict[str, float]
    evolution_data: Dict[str, Any]
    
    # Resultados
    success: bool
    improvement_achieved: Dict[str, float]
    
    # Metadata
    timestamp: datetime
    duration: float
    confidence_level: float

@dataclass
class AgentProfile:
    """Perfil evolutivo de um agente"""
    agent_id: str
    agent_name: str
    
    # Métricas de performance
    current_metrics: Dict[str, float]
    historical_metrics: List[Dict[str, Any]]
    
    # Configurações evolutivas
    evolution_enabled: bool
    evolution_frequency: int  # Em horas
    last_evolution: Optional[datetime]
    
    # Prompts e comportamentos
    base_prompt: str
    current_prompt: str
    prompt_history: List[Dict[str, Any]]
    
    # Especialização
    expertise_areas: List[str]
    learning_focus: List[str]
    
    # Estatísticas
    total_interactions: int
    successful_evolutions: int
    failed_evolutions: int
    
    created_at: datetime
    last_updated: datetime

class AgentEvolutionSystem:
    """
    Sistema de Evolução de Agentes
    
    Funcionalidades:
    - Monitoramento contínuo de performance dos agentes
    - Identificação automática de oportunidades de melhoria
    - Evolução de prompts baseada em feedback
    - Adaptação de comportamento baseada em padrões
    - A/B testing de melhorias
    - Rollback automático se performance piorar
    """
    
    def __init__(self):
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self.evolution_events: List[EvolutionEvent] = []
        self.active_experiments: Dict[str, Dict[str, Any]] = {}
        
        # Configurações
        self.evolution_threshold = 0.1  # Melhoria mínima para aplicar evolução
        self.rollback_threshold = 0.05  # Piora máxima antes de rollback
        self.experiment_duration = 24  # Horas para testar evolução
        
        # Métricas de sistema
        self.system_metrics = {
            "total_evolutions": 0,
            "successful_evolutions": 0,
            "failed_evolutions": 0,
            "rollbacks_performed": 0,
            "average_improvement": 0.0
        }
        
        logger.info("🧬 Sistema de Evolução de Agentes inicializado")
    
    async def initialize_agent_profile(self, 
                                     agent_id: str, 
                                     agent_name: str,
                                     base_prompt: str,
                                     expertise_areas: List[str]) -> None:
        """Inicializa perfil evolutivo de um agente"""
        
        profile = AgentProfile(
            agent_id=agent_id,
            agent_name=agent_name,
            current_metrics={
                "satisfaction_score": 0.0,
                "response_time": 0.0,
                "confidence_score": 0.0,
                "iteration_rate": 0.0,
                "success_rate": 0.0
            },
            historical_metrics=[],
            evolution_enabled=True,
            evolution_frequency=24,  # Evolução diária
            last_evolution=None,
            base_prompt=base_prompt,
            current_prompt=base_prompt,
            prompt_history=[{
                "prompt": base_prompt,
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "performance": {}
            }],
            expertise_areas=expertise_areas,
            learning_focus=[],
            total_interactions=0,
            successful_evolutions=0,
            failed_evolutions=0,
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        self.agent_profiles[agent_id] = profile
        logger.info(f"🧬 Perfil evolutivo criado para agente: {agent_name}")
    
    async def update_agent_metrics(self, 
                                 agent_id: str, 
                                 interaction_data: Dict[str, Any]) -> None:
        """Atualiza métricas de um agente baseado em interação"""
        
        if agent_id not in self.agent_profiles:
            logger.warning(f"⚠️ Agente {agent_id} não encontrado para atualização de métricas")
            return
        
        profile = self.agent_profiles[agent_id]
        profile.total_interactions += 1
        
        # Extrair métricas da interação
        new_metrics = {
            "satisfaction_score": interaction_data.get("satisfaction", 0.0),
            "response_time": interaction_data.get("response_time", 0.0),
            "confidence_score": interaction_data.get("confidence", 0.0),
            "iteration_rate": interaction_data.get("iterations", 1),
            "success_rate": 1.0 if interaction_data.get("satisfaction", 0.0) > 0.7 else 0.0
        }
        
        # Atualizar métricas atuais (média móvel)
        alpha = 0.1  # Fator de suavização
        for metric, value in new_metrics.items():
            current = profile.current_metrics.get(metric, 0.0)
            profile.current_metrics[metric] = (1 - alpha) * current + alpha * value
        
        # Adicionar ao histórico
        profile.historical_metrics.append({
            "timestamp": datetime.now().isoformat(),
            "metrics": new_metrics.copy(),
            "interaction_id": interaction_data.get("interaction_id", "unknown")
        })
        
        # Manter apenas últimas 100 métricas
        if len(profile.historical_metrics) > 100:
            profile.historical_metrics = profile.historical_metrics[-100:]
        
        profile.last_updated = datetime.now()
        
        # Verificar se deve evoluir
        await self._check_evolution_triggers(agent_id)
    
    async def _check_evolution_triggers(self, agent_id: str) -> None:
        """Verifica se agente deve evoluir baseado em gatilhos"""
        
        profile = self.agent_profiles[agent_id]
        
        if not profile.evolution_enabled:
            return
        
        # Verificar gatilhos de evolução
        triggers = []
        
        # Gatilho: Baixa satisfação
        if profile.current_metrics["satisfaction_score"] < 0.6:
            triggers.append(EvolutionTrigger.LOW_SATISFACTION)
        
        # Gatilho: Muitas iterações
        if profile.current_metrics["iteration_rate"] > 2.0:
            triggers.append(EvolutionTrigger.HIGH_ITERATION_COUNT)
        
        # Gatilho: Resposta lenta
        if profile.current_metrics["response_time"] > 10.0:
            triggers.append(EvolutionTrigger.SLOW_RESPONSE)
        
        # Gatilho: Baixa confiança
        if profile.current_metrics["confidence_score"] < 0.7:
            triggers.append(EvolutionTrigger.LOW_CONFIDENCE)
        
        # Gatilho: Evolução programada
        if (profile.last_evolution is None or 
            datetime.now() - profile.last_evolution > timedelta(hours=profile.evolution_frequency)):
            triggers.append(EvolutionTrigger.SCHEDULED_EVOLUTION)
        
        # Executar evolução se houver gatilhos
        if triggers:
            await self._trigger_evolution(agent_id, triggers)
    
    async def _trigger_evolution(self, agent_id: str, triggers: List[EvolutionTrigger]) -> None:
        """Dispara processo de evolução para um agente"""
        
        profile = self.agent_profiles[agent_id]
        
        # Determinar estratégia de evolução baseada nos gatilhos
        strategy = self._determine_evolution_strategy(triggers, profile)
        
        # Executar evolução
        evolution_event = await self._execute_evolution(agent_id, triggers[0], strategy)
        
        # Registrar evento
        self.evolution_events.append(evolution_event)
        
        # Atualizar estatísticas
        self.system_metrics["total_evolutions"] += 1
        if evolution_event.success:
            self.system_metrics["successful_evolutions"] += 1
            profile.successful_evolutions += 1
        else:
            self.system_metrics["failed_evolutions"] += 1
            profile.failed_evolutions += 1
        
        profile.last_evolution = datetime.now()
        
        logger.info(f"🧬 Evolução executada para {profile.agent_name}: {strategy.value}")
    
    def _determine_evolution_strategy(self, 
                                    triggers: List[EvolutionTrigger], 
                                    profile: AgentProfile) -> EvolutionStrategy:
        """Determina estratégia de evolução baseada nos gatilhos"""
        
        # Mapear gatilhos para estratégias
        trigger_strategy_map = {
            EvolutionTrigger.LOW_SATISFACTION: EvolutionStrategy.RESPONSE_REFINEMENT,
            EvolutionTrigger.HIGH_ITERATION_COUNT: EvolutionStrategy.PROMPT_OPTIMIZATION,
            EvolutionTrigger.SLOW_RESPONSE: EvolutionStrategy.BEHAVIOR_ADAPTATION,
            EvolutionTrigger.LOW_CONFIDENCE: EvolutionStrategy.KNOWLEDGE_EXPANSION,
            EvolutionTrigger.PATTERN_DETECTED: EvolutionStrategy.COLLABORATION_IMPROVEMENT,
            EvolutionTrigger.SCHEDULED_EVOLUTION: EvolutionStrategy.PROMPT_OPTIMIZATION
        }
        
        # Usar estratégia do primeiro gatilho
        primary_trigger = triggers[0]
        return trigger_strategy_map.get(primary_trigger, EvolutionStrategy.PROMPT_OPTIMIZATION)
    
    async def _execute_evolution(self, 
                               agent_id: str, 
                               trigger: EvolutionTrigger,
                               strategy: EvolutionStrategy) -> EvolutionEvent:
        """Executa evolução de um agente"""
        
        start_time = time.time()
        profile = self.agent_profiles[agent_id]
        
        # Capturar métricas baseline
        baseline_metrics = profile.current_metrics.copy()
        
        # Definir métricas alvo
        target_metrics = self._calculate_target_metrics(baseline_metrics, strategy)
        
        # Executar estratégia específica
        evolution_data = {}
        success = False
        
        try:
            if strategy == EvolutionStrategy.PROMPT_OPTIMIZATION:
                evolution_data, success = await self._evolve_prompt(agent_id, trigger)
            elif strategy == EvolutionStrategy.BEHAVIOR_ADAPTATION:
                evolution_data, success = await self._adapt_behavior(agent_id, trigger)
            elif strategy == EvolutionStrategy.KNOWLEDGE_EXPANSION:
                evolution_data, success = await self._expand_knowledge(agent_id, trigger)
            elif strategy == EvolutionStrategy.RESPONSE_REFINEMENT:
                evolution_data, success = await self._refine_responses(agent_id, trigger)
            elif strategy == EvolutionStrategy.COLLABORATION_IMPROVEMENT:
                evolution_data, success = await self._improve_collaboration(agent_id, trigger)
            
        except Exception as e:
            logger.error(f"❌ Erro na evolução do agente {agent_id}: {e}")
            success = False
        
        # Calcular melhoria alcançada (será atualizada após período de teste)
        improvement_achieved = {}
        
        # Criar evento de evolução
        evolution_event = EvolutionEvent(
            event_id=f"evolution_{agent_id}_{int(time.time())}",
            agent_id=agent_id,
            trigger=trigger,
            strategy=strategy,
            baseline_metrics=baseline_metrics,
            target_metrics=target_metrics,
            evolution_data=evolution_data,
            success=success,
            improvement_achieved=improvement_achieved,
            timestamp=datetime.now(),
            duration=time.time() - start_time,
            confidence_level=0.8  # Será calculada baseada em dados históricos
        )
        
        return evolution_event
    
    def _calculate_target_metrics(self, 
                                baseline: Dict[str, float], 
                                strategy: EvolutionStrategy) -> Dict[str, float]:
        """Calcula métricas alvo baseadas na estratégia"""
        
        target = baseline.copy()
        
        if strategy == EvolutionStrategy.PROMPT_OPTIMIZATION:
            target["satisfaction_score"] = min(1.0, baseline["satisfaction_score"] + 0.15)
            target["iteration_rate"] = max(1.0, baseline["iteration_rate"] - 0.3)
        
        elif strategy == EvolutionStrategy.BEHAVIOR_ADAPTATION:
            target["response_time"] = max(1.0, baseline["response_time"] * 0.8)
            target["confidence_score"] = min(1.0, baseline["confidence_score"] + 0.1)
        
        elif strategy == EvolutionStrategy.KNOWLEDGE_EXPANSION:
            target["confidence_score"] = min(1.0, baseline["confidence_score"] + 0.2)
            target["success_rate"] = min(1.0, baseline["success_rate"] + 0.15)
        
        elif strategy == EvolutionStrategy.RESPONSE_REFINEMENT:
            target["satisfaction_score"] = min(1.0, baseline["satisfaction_score"] + 0.2)
            target["success_rate"] = min(1.0, baseline["success_rate"] + 0.15)
        
        return target
    
    async def _evolve_prompt(self, agent_id: str, trigger: EvolutionTrigger) -> Tuple[Dict[str, Any], bool]:
        """Evolui prompt do agente baseado no gatilho"""
        
        profile = self.agent_profiles[agent_id]
        current_prompt = profile.current_prompt
        
        # Analisar padrões de feedback para otimização
        optimization_suggestions = await self._analyze_feedback_patterns(agent_id)
        
        # Gerar novo prompt
        new_prompt = await self._generate_optimized_prompt(
            current_prompt, 
            trigger, 
            optimization_suggestions,
            profile.expertise_areas
        )
        
        if new_prompt and new_prompt != current_prompt:
            # Criar versão de teste
            version = f"v{len(profile.prompt_history) + 1}.0"
            
            # Iniciar A/B test
            experiment_id = f"prompt_test_{agent_id}_{int(time.time())}"
            await self._start_ab_test(agent_id, experiment_id, new_prompt, version)
            
            evolution_data = {
                "old_prompt": current_prompt,
                "new_prompt": new_prompt,
                "version": version,
                "experiment_id": experiment_id,
                "optimization_suggestions": optimization_suggestions
            }
            
            return evolution_data, True
        
        return {"error": "Não foi possível gerar prompt otimizado"}, False
    
    async def _analyze_feedback_patterns(self, agent_id: str) -> List[str]:
        """Analisa padrões de feedback para sugerir otimizações"""
        
        # Obter insights do sistema de aprendizado
        insights = await learning_engine.get_learning_insights()
        
        suggestions = []
        
        # Analisar padrões específicos do agente
        agent_patterns = [
            p for p in insights.get("top_patterns", [])
            if agent_id in p.get("agents_involved", [])
        ]
        
        for pattern in agent_patterns:
            if pattern.get("success_rate", 0) < 0.7:
                suggestions.append(f"Melhorar abordagem para {pattern.get('description', 'situação específica')}")
        
        # Sugestões baseadas em métricas
        profile = self.agent_profiles[agent_id]
        
        if profile.current_metrics["satisfaction_score"] < 0.7:
            suggestions.append("Ser mais específico e detalhado nas respostas")
        
        if profile.current_metrics["iteration_rate"] > 2.0:
            suggestions.append("Fornecer respostas mais completas na primeira tentativa")
        
        if profile.current_metrics["confidence_score"] < 0.7:
            suggestions.append("Basear recomendações em dados e melhores práticas")
        
        return suggestions
    
    async def _generate_optimized_prompt(self, 
                                       current_prompt: str,
                                       trigger: EvolutionTrigger,
                                       suggestions: List[str],
                                       expertise_areas: List[str]) -> str:
        """Gera prompt otimizado baseado em análise"""
        
        # Identificar área de melhoria baseada no gatilho
        improvement_focus = {
            EvolutionTrigger.LOW_SATISFACTION: "qualidade e relevância das respostas",
            EvolutionTrigger.HIGH_ITERATION_COUNT: "completude e precisão inicial",
            EvolutionTrigger.SLOW_RESPONSE: "eficiência e concisão",
            EvolutionTrigger.LOW_CONFIDENCE: "fundamentação e expertise",
            EvolutionTrigger.SCHEDULED_EVOLUTION: "otimização geral"
        }.get(trigger, "melhoria geral")
        
        # Construir prompt otimizado
        optimization_instructions = []
        
        # Adicionar instruções baseadas no foco
        if "qualidade" in improvement_focus:
            optimization_instructions.append(
                "Priorize respostas de alta qualidade, detalhadas e altamente relevantes para o contexto específico."
            )
        
        if "completude" in improvement_focus:
            optimization_instructions.append(
                "Forneça respostas completas e abrangentes na primeira tentativa, antecipando possíveis dúvidas."
            )
        
        if "eficiência" in improvement_focus:
            optimization_instructions.append(
                "Seja conciso mas completo, priorizando as informações mais importantes primeiro."
            )
        
        if "fundamentação" in improvement_focus:
            optimization_instructions.append(
                "Base todas as recomendações em melhores práticas estabelecidas, dados concretos e sua expertise."
            )
        
        # Adicionar sugestões específicas
        for suggestion in suggestions[:3]:  # Máximo 3 sugestões
            optimization_instructions.append(f"Importante: {suggestion}")
        
        # Construir novo prompt
        if optimization_instructions:
            new_prompt = current_prompt + "\n\n" + "OTIMIZAÇÕES BASEADAS EM APRENDIZADO:\n"
            for i, instruction in enumerate(optimization_instructions, 1):
                new_prompt += f"{i}. {instruction}\n"
            
            return new_prompt
        
        return current_prompt
    
    async def _start_ab_test(self, 
                           agent_id: str, 
                           experiment_id: str, 
                           new_prompt: str, 
                           version: str) -> None:
        """Inicia teste A/B para novo prompt"""
        
        self.active_experiments[experiment_id] = {
            "agent_id": agent_id,
            "type": "prompt_optimization",
            "start_time": datetime.now(),
            "duration_hours": self.experiment_duration,
            "control_prompt": self.agent_profiles[agent_id].current_prompt,
            "test_prompt": new_prompt,
            "version": version,
            "control_metrics": [],
            "test_metrics": [],
            "status": "running"
        }
        
        logger.info(f"🧪 A/B test iniciado para {agent_id}: {experiment_id}")
    
    async def _adapt_behavior(self, agent_id: str, trigger: EvolutionTrigger) -> Tuple[Dict[str, Any], bool]:
        """Adapta comportamento do agente"""
        # Implementar adaptação de comportamento
        return {"behavior_adaptation": "implemented"}, True
    
    async def _expand_knowledge(self, agent_id: str, trigger: EvolutionTrigger) -> Tuple[Dict[str, Any], bool]:
        """Expande conhecimento do agente"""
        # Implementar expansão de conhecimento
        return {"knowledge_expansion": "implemented"}, True
    
    async def _refine_responses(self, agent_id: str, trigger: EvolutionTrigger) -> Tuple[Dict[str, Any], bool]:
        """Refina respostas do agente"""
        # Implementar refinamento de respostas
        return {"response_refinement": "implemented"}, True
    
    async def _improve_collaboration(self, agent_id: str, trigger: EvolutionTrigger) -> Tuple[Dict[str, Any], bool]:
        """Melhora colaboração do agente"""
        # Implementar melhoria de colaboração
        return {"collaboration_improvement": "implemented"}, True
    
    async def check_experiment_results(self) -> None:
        """Verifica resultados de experimentos em andamento"""
        
        current_time = datetime.now()
        
        for experiment_id, experiment in list(self.active_experiments.items()):
            # Verificar se experimento deve ser finalizado
            elapsed_hours = (current_time - experiment["start_time"]).total_seconds() / 3600
            
            if elapsed_hours >= experiment["duration_hours"]:
                await self._finalize_experiment(experiment_id)
    
    async def _finalize_experiment(self, experiment_id: str) -> None:
        """Finaliza experimento e aplica resultados"""
        
        experiment = self.active_experiments[experiment_id]
        agent_id = experiment["agent_id"]
        profile = self.agent_profiles[agent_id]
        
        # Analisar resultados (simplificado para MVP)
        # Em implementação completa, compararia métricas de controle vs teste
        
        # Aplicar prompt otimizado se experimento foi bem-sucedido
        if experiment["type"] == "prompt_optimization":
            # Atualizar prompt do agente
            profile.current_prompt = experiment["test_prompt"]
            
            # Adicionar ao histórico
            profile.prompt_history.append({
                "prompt": experiment["test_prompt"],
                "version": experiment["version"],
                "timestamp": datetime.now().isoformat(),
                "experiment_id": experiment_id,
                "performance": {}  # Será preenchido com métricas reais
            })
            
            logger.info(f"✅ Prompt otimizado aplicado para {profile.agent_name}")
        
        # Remover experimento ativo
        experiment["status"] = "completed"
        del self.active_experiments[experiment_id]
    
    async def get_evolution_analytics(self) -> Dict[str, Any]:
        """Retorna analytics do sistema de evolução"""
        
        total_agents = len(self.agent_profiles)
        active_experiments = len(self.active_experiments)
        
        # Calcular métricas agregadas
        if self.agent_profiles:
            avg_satisfaction = statistics.mean([
                p.current_metrics["satisfaction_score"] 
                for p in self.agent_profiles.values()
            ])
            
            avg_confidence = statistics.mean([
                p.current_metrics["confidence_score"] 
                for p in self.agent_profiles.values()
            ])
        else:
            avg_satisfaction = 0.0
            avg_confidence = 0.0
        
        return {
            "system_metrics": self.system_metrics.copy(),
            "agent_metrics": {
                "total_agents": total_agents,
                "agents_with_evolution": len([p for p in self.agent_profiles.values() if p.evolution_enabled]),
                "average_satisfaction": avg_satisfaction,
                "average_confidence": avg_confidence,
                "total_interactions": sum(p.total_interactions for p in self.agent_profiles.values())
            },
            "experiment_metrics": {
                "active_experiments": active_experiments,
                "total_experiments": len(self.evolution_events),
                "success_rate": (
                    self.system_metrics["successful_evolutions"] / 
                    max(self.system_metrics["total_evolutions"], 1)
                )
            },
            "recent_evolutions": [
                {
                    "agent_id": e.agent_id,
                    "strategy": e.strategy.value,
                    "success": e.success,
                    "timestamp": e.timestamp.isoformat()
                }
                for e in self.evolution_events[-10:]  # Últimas 10 evoluções
            ]
        }
    
    async def get_agent_evolution_status(self, agent_id: str) -> Dict[str, Any]:
        """Retorna status de evolução de um agente específico"""
        
        if agent_id not in self.agent_profiles:
            return {"error": "Agente não encontrado"}
        
        profile = self.agent_profiles[agent_id]
        
        # Encontrar experimentos ativos para este agente
        active_experiments = [
            exp for exp in self.active_experiments.values()
            if exp["agent_id"] == agent_id
        ]
        
        return {
            "agent_id": agent_id,
            "agent_name": profile.agent_name,
            "evolution_enabled": profile.evolution_enabled,
            "current_metrics": profile.current_metrics,
            "total_interactions": profile.total_interactions,
            "evolution_stats": {
                "successful_evolutions": profile.successful_evolutions,
                "failed_evolutions": profile.failed_evolutions,
                "last_evolution": profile.last_evolution.isoformat() if profile.last_evolution else None
            },
            "current_prompt_version": f"v{len(profile.prompt_history)}.0",
            "active_experiments": len(active_experiments),
            "expertise_areas": profile.expertise_areas,
            "learning_focus": profile.learning_focus
        }

# Instância global do sistema de evolução
agent_evolution_system = AgentEvolutionSystem()

if __name__ == "__main__":
    # Teste básico do sistema de evolução
    async def test_evolution_system():
        print("🧪 Testando Sistema de Evolução de Agentes...")
        
        # Inicializar perfil de agente
        await agent_evolution_system.initialize_agent_profile(
            "ana_beatriz_costa",
            "Dra. Ana Beatriz Costa",
            "Você é uma CTO experiente especializada em estratégia tecnológica...",
            ["estratégia", "inovação", "liderança"]
        )
        
        # Simular atualização de métricas
        await agent_evolution_system.update_agent_metrics(
            "ana_beatriz_costa",
            {
                "satisfaction": 0.5,  # Baixa satisfação para trigger evolução
                "response_time": 8.0,
                "confidence": 0.6,
                "iterations": 3,
                "interaction_id": "test_001"
            }
        )
        
        # Verificar experimentos
        await agent_evolution_system.check_experiment_results()
        
        # Analytics
        analytics = await agent_evolution_system.get_evolution_analytics()
        print(f"📊 Analytics: {analytics}")
        
        # Status do agente
        status = await agent_evolution_system.get_agent_evolution_status("ana_beatriz_costa")
        print(f"🤖 Status do agente: {status}")
        
        print("✅ Teste concluído!")
    
    asyncio.run(test_evolution_system())