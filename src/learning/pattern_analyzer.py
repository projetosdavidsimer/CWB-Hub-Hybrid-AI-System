"""
Analisador de Padrões para Sistema de Aprendizado Contínuo
Melhoria #7 - Componente de análise de padrões

Identifica e analisa padrões em:
- Interações bem-sucedidas
- Colaborações efetivas
- Preferências dos usuários
- Contextos de uso
- Evolução temporal

Criado por: David Simer
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
from collections import defaultdict, Counter
import re
# Importações opcionais para ML
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    TfidfVectorizer = None

try:
    import networkx as nx
    NETWORKX_AVAILABLE = True
except ImportError:
    NETWORKX_AVAILABLE = False
    nx = None


class PatternType(Enum):
    """Tipos de padrões identificáveis"""
    SUCCESS_COLLABORATION = "success_collaboration"
    USER_PREFERENCE = "user_preference"
    CONTEXT_USAGE = "context_usage"
    TEMPORAL_TREND = "temporal_trend"
    AGENT_SYNERGY = "agent_synergy"
    PROBLEM_SOLUTION = "problem_solution"
    COMMUNICATION_STYLE = "communication_style"
    EXPERTISE_DEMAND = "expertise_demand"


class PatternConfidence(Enum):
    """Níveis de confiança do padrão"""
    LOW = 0.3
    MEDIUM = 0.6
    HIGH = 0.8
    VERY_HIGH = 0.9


@dataclass
class PatternFeature:
    """Característica de um padrão"""
    feature_name: str
    feature_value: Any
    importance: float
    frequency: int


@dataclass
class IdentifiedPattern:
    """Padrão identificado pelo sistema"""
    pattern_id: str
    pattern_type: PatternType
    confidence: float
    features: List[PatternFeature]
    context: str
    success_rate: float
    usage_count: int
    agents_involved: List[str]
    time_range: Tuple[datetime, datetime]
    created_at: datetime
    last_updated: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PatternAnalysisResult:
    """Resultado da análise de padrões"""
    analysis_id: str
    timestamp: datetime
    patterns_found: List[IdentifiedPattern]
    insights: List[str]
    recommendations: List[str]
    confidence_score: float
    data_quality: float


class PatternAnalyzer:
    """
    Analisador de Padrões CWB Hub
    
    Funcionalidades:
    1. Identificação automática de padrões
    2. Análise de correlações
    3. Detecção de tendências temporais
    4. Análise de redes de colaboração
    5. Extração de insights acionáveis
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Configurações de análise
        self.analysis_config = {
            "min_pattern_frequency": 3,
            "min_confidence_threshold": 0.6,
            "max_patterns_per_analysis": 50,
            "temporal_window_days": 30,
            "similarity_threshold": 0.7,
            "clustering_max_clusters": 10
        }
        
        # Cache de análises
        self.pattern_cache: Dict[str, List[IdentifiedPattern]] = {}
        self.analysis_cache: Dict[str, PatternAnalysisResult] = {}
        
        # Modelos de ML (opcionais)
        if SKLEARN_AVAILABLE:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
        else:
            self.tfidf_vectorizer = None
        
        # Grafo de colaboração (opcional)
        if NETWORKX_AVAILABLE:
            self.collaboration_graph = nx.Graph()
        else:
            self.collaboration_graph = None
        
        self.logger.info("🔍 Analisador de Padrões CWB Hub inicializado")
    
    async def analyze_session_patterns(
        self,
        sessions: List[Any],  # CollaborationSession objects
        analysis_type: str = "comprehensive"
    ) -> PatternAnalysisResult:
        """
        Analisa padrões em um conjunto de sessões
        
        Args:
            sessions: Lista de sessões para análise
            analysis_type: Tipo de análise (comprehensive, quick, focused)
            
        Returns:
            Resultado da análise de padrões
        """
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.logger.info(f"🔍 Iniciando análise de padrões: {analysis_id}")
        
        patterns_found = []
        insights = []
        recommendations = []
        
        try:
            # 1. Análise de colaboração bem-sucedida
            collaboration_patterns = await self._analyze_collaboration_patterns(sessions)
            patterns_found.extend(collaboration_patterns)
            
            # 2. Análise de preferências do usuário
            preference_patterns = await self._analyze_user_preferences(sessions)
            patterns_found.extend(preference_patterns)
            
            # 3. Análise de contexto de uso
            context_patterns = await self._analyze_context_usage(sessions)
            patterns_found.extend(context_patterns)
            
            # 4. Análise temporal
            temporal_patterns = await self._analyze_temporal_trends(sessions)
            patterns_found.extend(temporal_patterns)
            
            # 5. Análise de sinergia entre agentes
            synergy_patterns = await self._analyze_agent_synergy(sessions)
            patterns_found.extend(synergy_patterns)
            
            # Gerar insights
            insights = await self._generate_insights(patterns_found)
            
            # Gerar recomendações
            recommendations = await self._generate_recommendations(patterns_found)
            
            # Calcular scores de qualidade
            confidence_score = np.mean([p.confidence for p in patterns_found]) if patterns_found else 0.0
            data_quality = await self._calculate_data_quality(sessions)
            
            result = PatternAnalysisResult(
                analysis_id=analysis_id,
                timestamp=datetime.now(),
                patterns_found=patterns_found,
                insights=insights,
                recommendations=recommendations,
                confidence_score=confidence_score,
                data_quality=data_quality
            )
            
            # Cache do resultado
            self.analysis_cache[analysis_id] = result
            
            self.logger.info(f"✅ Análise concluída: {len(patterns_found)} padrões encontrados")
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Erro na análise de padrões: {e}")
            raise
    
    async def _analyze_collaboration_patterns(self, sessions: List[Any]) -> List[IdentifiedPattern]:
        """Analisa padrões de colaboração bem-sucedida"""
        patterns = []
        
        # Agrupar sessões por sucesso (baseado em iterações e feedback)
        successful_sessions = [
            s for s in sessions 
            if s.iterations <= 2 and len(s.agent_responses) >= 3
        ]
        
        if len(successful_sessions) < self.analysis_config["min_pattern_frequency"]:
            return patterns
        
        # Analisar combinações de agentes em sessões bem-sucedidas
        agent_combinations = defaultdict(int)
        for session in successful_sessions:
            agents_in_session = list(set([r.agent_id for r in session.agent_responses]))
            
            # Gerar combinações de 2 e 3 agentes
            for i in range(len(agents_in_session)):
                for j in range(i + 1, len(agents_in_session)):
                    combo = tuple(sorted([agents_in_session[i], agents_in_session[j]]))
                    agent_combinations[combo] += 1
        
        # Identificar combinações frequentes
        for combo, frequency in agent_combinations.items():
            if frequency >= self.analysis_config["min_pattern_frequency"]:
                success_rate = frequency / len(successful_sessions)
                
                pattern = IdentifiedPattern(
                    pattern_id=f"collab_{hash(combo)}",
                    pattern_type=PatternType.SUCCESS_COLLABORATION,
                    confidence=min(0.9, success_rate * 1.2),
                    features=[
                        PatternFeature("agent_combination", combo, 1.0, frequency),
                        PatternFeature("success_rate", success_rate, 0.8, frequency)
                    ],
                    context=f"Colaboração entre {' e '.join(combo)}",
                    success_rate=success_rate,
                    usage_count=frequency,
                    agents_involved=list(combo),
                    time_range=(
                        min(s.created_at for s in successful_sessions),
                        max(s.created_at for s in successful_sessions)
                    ),
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                
                patterns.append(pattern)
        
        return patterns
    
    async def _analyze_user_preferences(self, sessions: List[Any]) -> List[IdentifiedPattern]:
        """Analisa padrões de preferências do usuário"""
        patterns = []
        
        # Analisar tipos de requisições mais comuns
        request_types = []
        for session in sessions:
            # Classificar tipo de requisição baseado em palavras-chave
            request_lower = session.user_request.lower()
            
            if any(word in request_lower for word in ['app', 'aplicativo', 'mobile']):
                request_types.append('mobile_development')
            elif any(word in request_lower for word in ['web', 'site', 'frontend']):
                request_types.append('web_development')
            elif any(word in request_lower for word in ['arquitetura', 'design', 'estrutura']):
                request_types.append('architecture')
            elif any(word in request_lower for word in ['dados', 'database', 'banco']):
                request_types.append('data')
            else:
                request_types.append('general')
        
        # Contar frequências
        type_counts = Counter(request_types)
        
        for req_type, count in type_counts.items():
            if count >= self.analysis_config["min_pattern_frequency"]:
                frequency_rate = count / len(sessions)
                
                pattern = IdentifiedPattern(
                    pattern_id=f"pref_{req_type}",
                    pattern_type=PatternType.USER_PREFERENCE,
                    confidence=min(0.8, frequency_rate * 1.5),
                    features=[
                        PatternFeature("request_type", req_type, 1.0, count),
                        PatternFeature("frequency_rate", frequency_rate, 0.9, count)
                    ],
                    context=f"Preferência por {req_type.replace('_', ' ')}",
                    success_rate=0.8,  # Assumindo sucesso baseado na frequência
                    usage_count=count,
                    agents_involved=self._get_relevant_agents_for_type(req_type),
                    time_range=(
                        min(s.created_at for s in sessions),
                        max(s.created_at for s in sessions)
                    ),
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                
                patterns.append(pattern)
        
        return patterns
    
    async def _analyze_context_usage(self, sessions: List[Any]) -> List[IdentifiedPattern]:
        """Analisa padrões de contexto de uso"""
        patterns = []
        
        # Analisar horários de uso
        hour_usage = defaultdict(int)
        for session in sessions:
            hour = session.created_at.hour
            hour_usage[hour] += 1
        
        # Identificar horários de pico
        total_sessions = len(sessions)
        for hour, count in hour_usage.items():
            usage_rate = count / total_sessions
            
            if usage_rate > 0.1:  # Mais de 10% das sessões
                pattern = IdentifiedPattern(
                    pattern_id=f"context_hour_{hour}",
                    pattern_type=PatternType.CONTEXT_USAGE,
                    confidence=min(0.7, usage_rate * 2),
                    features=[
                        PatternFeature("peak_hour", hour, 1.0, count),
                        PatternFeature("usage_rate", usage_rate, 0.8, count)
                    ],
                    context=f"Uso frequente às {hour}:00h",
                    success_rate=0.7,
                    usage_count=count,
                    agents_involved=[],  # Não específico de agentes
                    time_range=(
                        min(s.created_at for s in sessions),
                        max(s.created_at for s in sessions)
                    ),
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                
                patterns.append(pattern)
        
        return patterns
    
    async def _analyze_temporal_trends(self, sessions: List[Any]) -> List[IdentifiedPattern]:
        """Analisa tendências temporais"""
        patterns = []
        
        if len(sessions) < 7:  # Precisa de dados suficientes
            return patterns
        
        # Ordenar sessões por data
        sorted_sessions = sorted(sessions, key=lambda s: s.created_at)
        
        # Analisar tendência de complexidade (baseado em número de iterações)
        complexities = [s.iterations for s in sorted_sessions]
        
        # Calcular tendência usando regressão linear simples
        x = np.arange(len(complexities))
        y = np.array(complexities)
        
        if len(x) > 1:
            slope = np.polyfit(x, y, 1)[0]
            
            if abs(slope) > 0.1:  # Tendência significativa
                trend_type = "increasing" if slope > 0 else "decreasing"
                
                pattern = IdentifiedPattern(
                    pattern_id=f"temporal_complexity_{trend_type}",
                    pattern_type=PatternType.TEMPORAL_TREND,
                    confidence=min(0.8, abs(slope) * 2),
                    features=[
                        PatternFeature("trend_slope", slope, 1.0, len(sessions)),
                        PatternFeature("trend_direction", trend_type, 0.9, len(sessions))
                    ],
                    context=f"Complexidade das consultas está {trend_type}",
                    success_rate=0.7,
                    usage_count=len(sessions),
                    agents_involved=[],
                    time_range=(
                        sorted_sessions[0].created_at,
                        sorted_sessions[-1].created_at
                    ),
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                
                patterns.append(pattern)
        
        return patterns
    
    async def _analyze_agent_synergy(self, sessions: List[Any]) -> List[IdentifiedPattern]:
        """Analisa sinergia entre agentes"""
        patterns = []
        
        # Construir grafo de colaboração (se disponível)
        if not NETWORKX_AVAILABLE or self.collaboration_graph is None:
            return patterns
            
        self.collaboration_graph.clear()
        
        for session in sessions:
            agents_in_session = list(set([r.agent_id for r in session.agent_responses]))
            
            # Adicionar nós
            for agent in agents_in_session:
                if not self.collaboration_graph.has_node(agent):
                    self.collaboration_graph.add_node(agent)
            
            # Adicionar arestas (colaborações)
            for i in range(len(agents_in_session)):
                for j in range(i + 1, len(agents_in_session)):
                    agent1, agent2 = agents_in_session[i], agents_in_session[j]
                    
                    if self.collaboration_graph.has_edge(agent1, agent2):
                        self.collaboration_graph[agent1][agent2]['weight'] += 1
                    else:
                        self.collaboration_graph.add_edge(agent1, agent2, weight=1)
        
        # Analisar centralidade e identificar agentes-chave
        if len(self.collaboration_graph.nodes()) > 2:
            centrality = nx.betweenness_centrality(self.collaboration_graph)
            
            # Identificar agentes com alta centralidade
            high_centrality_agents = [
                agent for agent, cent in centrality.items()
                if cent > 0.3
            ]
            
            if high_centrality_agents:
                pattern = IdentifiedPattern(
                    pattern_id="synergy_central_agents",
                    pattern_type=PatternType.AGENT_SYNERGY,
                    confidence=0.8,
                    features=[
                        PatternFeature("central_agents", high_centrality_agents, 1.0, len(high_centrality_agents)),
                        PatternFeature("avg_centrality", np.mean(list(centrality.values())), 0.8, len(centrality))
                    ],
                    context=f"Agentes centrais na colaboração: {', '.join(high_centrality_agents)}",
                    success_rate=0.8,
                    usage_count=len(sessions),
                    agents_involved=high_centrality_agents,
                    time_range=(
                        min(s.created_at for s in sessions),
                        max(s.created_at for s in sessions)
                    ),
                    created_at=datetime.now(),
                    last_updated=datetime.now()
                )
                
                patterns.append(pattern)
        
        return patterns
    
    async def _generate_insights(self, patterns: List[IdentifiedPattern]) -> List[str]:
        """Gera insights baseados nos padrões identificados"""
        insights = []
        
        # Insights de colaboração
        collab_patterns = [p for p in patterns if p.pattern_type == PatternType.SUCCESS_COLLABORATION]
        if collab_patterns:
            best_collab = max(collab_patterns, key=lambda p: p.success_rate)
            insights.append(
                f"A melhor combinação de agentes é {' + '.join(best_collab.agents_involved)} "
                f"com {best_collab.success_rate:.1%} de taxa de sucesso"
            )
        
        # Insights de preferências
        pref_patterns = [p for p in patterns if p.pattern_type == PatternType.USER_PREFERENCE]
        if pref_patterns:
            top_pref = max(pref_patterns, key=lambda p: p.usage_count)
            insights.append(
                f"Usuários preferem consultas sobre {top_pref.context.lower()} "
                f"({top_pref.usage_count} ocorrências)"
            )
        
        # Insights temporais
        temporal_patterns = [p for p in patterns if p.pattern_type == PatternType.TEMPORAL_TREND]
        if temporal_patterns:
            for pattern in temporal_patterns:
                insights.append(f"Tendência identificada: {pattern.context}")
        
        # Insights de sinergia
        synergy_patterns = [p for p in patterns if p.pattern_type == PatternType.AGENT_SYNERGY]
        if synergy_patterns:
            for pattern in synergy_patterns:
                insights.append(f"Sinergia detectada: {pattern.context}")
        
        return insights
    
    async def _generate_recommendations(self, patterns: List[IdentifiedPattern]) -> List[str]:
        """Gera recomendações baseadas nos padrões"""
        recommendations = []
        
        # Recomendações de colaboração
        collab_patterns = [p for p in patterns if p.pattern_type == PatternType.SUCCESS_COLLABORATION]
        if collab_patterns:
            high_success_patterns = [p for p in collab_patterns if p.success_rate > 0.8]
            if high_success_patterns:
                recommendations.append(
                    "Priorizar combinações de agentes com alta taxa de sucesso identificadas"
                )
        
        # Recomendações de horário
        context_patterns = [p for p in patterns if p.pattern_type == PatternType.CONTEXT_USAGE]
        peak_hours = [p for p in context_patterns if any(f.feature_name == "usage_rate" and f.feature_value > 0.15 for f in p.features)]
        if peak_hours:
            recommendations.append(
                "Otimizar recursos durante horários de pico identificados"
            )
        
        # Recomendações de especialização
        pref_patterns = [p for p in patterns if p.pattern_type == PatternType.USER_PREFERENCE]
        if pref_patterns:
            top_preferences = sorted(pref_patterns, key=lambda p: p.usage_count, reverse=True)[:2]
            recommendations.append(
                f"Focar desenvolvimento em áreas de maior demanda: {', '.join([p.context for p in top_preferences])}"
            )
        
        return recommendations
    
    async def _calculate_data_quality(self, sessions: List[Any]) -> float:
        """Calcula qualidade dos dados para análise"""
        if not sessions:
            return 0.0
        
        quality_factors = []
        
        # Fator 1: Completude dos dados
        complete_sessions = [
            s for s in sessions 
            if s.user_request and s.agent_responses and s.final_solution
        ]
        completeness = len(complete_sessions) / len(sessions)
        quality_factors.append(completeness)
        
        # Fator 2: Diversidade de agentes
        all_agents = set()
        for session in sessions:
            all_agents.update([r.agent_id for r in session.agent_responses])
        diversity = len(all_agents) / 8  # 8 agentes total
        quality_factors.append(diversity)
        
        # Fator 3: Distribuição temporal
        if len(sessions) > 1:
            time_span = (max(s.created_at for s in sessions) - min(s.created_at for s in sessions)).days
            temporal_quality = min(1.0, time_span / 7)  # Melhor se distribuído ao longo de uma semana
            quality_factors.append(temporal_quality)
        
        return np.mean(quality_factors)
    
    def _get_relevant_agents_for_type(self, request_type: str) -> List[str]:
        """Retorna agentes relevantes para um tipo de requisição"""
        agent_mapping = {
            'mobile_development': ['gabriel_mendes', 'sofia_oliveira'],
            'web_development': ['sofia_oliveira', 'isabella_santos'],
            'architecture': ['carlos_eduardo_santos', 'ana_beatriz_costa'],
            'data': ['mariana_rodrigues', 'carlos_eduardo_santos'],
            'general': ['ana_beatriz_costa', 'pedro_henrique_almeida']
        }
        
        return agent_mapping.get(request_type, [])
    
    async def get_pattern_summary(self, pattern_ids: List[str]) -> Dict[str, Any]:
        """Obtém resumo de padrões específicos"""
        patterns = []
        
        for analysis in self.analysis_cache.values():
            patterns.extend([
                p for p in analysis.patterns_found 
                if p.pattern_id in pattern_ids
            ])
        
        if not patterns:
            return {"error": "Padrões não encontrados"}
        
        return {
            "patterns_count": len(patterns),
            "avg_confidence": np.mean([p.confidence for p in patterns]),
            "pattern_types": list(set([p.pattern_type.value for p in patterns])),
            "agents_involved": list(set([agent for p in patterns for agent in p.agents_involved])),
            "time_range": {
                "start": min(p.time_range[0] for p in patterns).isoformat(),
                "end": max(p.time_range[1] for p in patterns).isoformat()
            }
        }
    
    async def export_patterns(self, format_type: str = "json") -> str:
        """Exporta padrões identificados"""
        all_patterns = []
        
        for analysis in self.analysis_cache.values():
            for pattern in analysis.patterns_found:
                pattern_dict = {
                    "pattern_id": pattern.pattern_id,
                    "type": pattern.pattern_type.value,
                    "confidence": pattern.confidence,
                    "context": pattern.context,
                    "success_rate": pattern.success_rate,
                    "usage_count": pattern.usage_count,
                    "agents_involved": pattern.agents_involved,
                    "created_at": pattern.created_at.isoformat(),
                    "features": [
                        {
                            "name": f.feature_name,
                            "value": str(f.feature_value),
                            "importance": f.importance
                        }
                        for f in pattern.features
                    ]
                }
                all_patterns.append(pattern_dict)
        
        if format_type == "json":
            return json.dumps(all_patterns, indent=2)
        else:
            return str(all_patterns)


# Instância global do analisador
pattern_analyzer = PatternAnalyzer()