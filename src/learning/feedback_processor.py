"""
Processador de Feedback Inteligente
Melhoria #7 - Sistema de Aprendizado Contínuo

Processa e analisa feedback dos usuários para:
- Identificar áreas de melhoria
- Extrair insights acionáveis
- Personalizar experiência
- Otimizar performance dos agentes
- Detectar padrões de satisfação

Criado por: David Simer
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import json
import numpy as np
from collections import defaultdict, Counter
import re
# Importações opcionais para NLP
try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    TextBlob = None

try:
    import nltk
    from nltk.sentiment import SentimentIntensityAnalyzer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    nltk = None
    SentimentIntensityAnalyzer = None


class FeedbackCategory(Enum):
    """Categorias de feedback"""
    RESPONSE_QUALITY = "response_quality"
    COLLABORATION_EFFECTIVENESS = "collaboration_effectiveness"
    COMMUNICATION_CLARITY = "communication_clarity"
    SOLUTION_RELEVANCE = "solution_relevance"
    SPEED_PERFORMANCE = "speed_performance"
    EXPERTISE_ACCURACY = "expertise_accuracy"
    USER_EXPERIENCE = "user_experience"
    TECHNICAL_DEPTH = "technical_depth"


class SentimentLevel(Enum):
    """Níveis de sentimento"""
    VERY_NEGATIVE = -2
    NEGATIVE = -1
    NEUTRAL = 0
    POSITIVE = 1
    VERY_POSITIVE = 2


class FeedbackPriority(Enum):
    """Prioridades de feedback"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class ProcessedFeedback:
    """Feedback processado e analisado"""
    feedback_id: str
    original_feedback: str
    session_id: str
    user_id: Optional[str]
    agent_id: Optional[str]
    
    # Análise de sentimento
    sentiment_score: float
    sentiment_level: SentimentLevel
    confidence: float
    
    # Categorização
    categories: List[FeedbackCategory]
    priority: FeedbackPriority
    
    # Extração de informações
    key_phrases: List[str]
    mentioned_agents: List[str]
    specific_issues: List[str]
    suggestions: List[str]
    
    # Métricas
    rating_inferred: Optional[int]  # 1-5 baseado no sentimento
    urgency_score: float
    actionability_score: float
    
    # Metadados
    processed_at: datetime
    processing_version: str = "1.0"


@dataclass
class FeedbackInsight:
    """Insight extraído do feedback"""
    insight_id: str
    insight_type: str
    description: str
    affected_agents: List[str]
    confidence: float
    supporting_feedback: List[str]
    recommended_actions: List[str]
    created_at: datetime


@dataclass
class FeedbackTrend:
    """Tendência identificada no feedback"""
    trend_id: str
    trend_type: str
    direction: str  # improving, declining, stable
    metric: str
    current_value: float
    change_rate: float
    time_period: int  # dias
    significance: float
    created_at: datetime


class FeedbackProcessor:
    """
    Processador de Feedback Inteligente CWB Hub
    
    Funcionalidades:
    1. Análise de sentimento avançada
    2. Categorização automática
    3. Extração de insights
    4. Detecção de tendências
    5. Priorização inteligente
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Inicializar NLTK (se disponível)
        if NLTK_AVAILABLE:
            try:
                nltk.download('vader_lexicon', quiet=True)
                self.sentiment_analyzer = SentimentIntensityAnalyzer()
                self.nltk_available = True
            except Exception as e:
                self.logger.warning(f"⚠️ NLTK não disponível: {e}")
                self.nltk_available = False
        else:
            self.sentiment_analyzer = None
            self.nltk_available = False
        
        # Configurações
        self.processing_config = {
            "sentiment_threshold_positive": 0.1,
            "sentiment_threshold_negative": -0.1,
            "min_feedback_length": 10,
            "max_key_phrases": 10,
            "confidence_threshold": 0.6,
            "trend_min_samples": 5,
            "urgency_keywords": [
                "urgent", "critical", "broken", "error", "bug", "issue",
                "problem", "wrong", "incorrect", "failed", "not working"
            ],
            "positive_keywords": [
                "excellent", "great", "good", "helpful", "useful",
                "accurate", "fast", "clear", "perfect", "amazing"
            ],
            "negative_keywords": [
                "bad", "poor", "slow", "confusing", "unclear",
                "wrong", "useless", "terrible", "awful", "disappointing"
            ]
        }
        
        # Cache de processamento
        self.processed_feedback: Dict[str, ProcessedFeedback] = {}
        self.feedback_insights: List[FeedbackInsight] = []
        self.feedback_trends: List[FeedbackTrend] = []
        
        # Padrões de regex para extração
        self.patterns = {
            "agent_mentions": re.compile(r'\b(ana|carlos|sofia|gabriel|isabella|lucas|mariana|pedro)\b', re.IGNORECASE),
            "suggestions": re.compile(r'\b(suggest|recommend|should|could|would be better|improve)\b', re.IGNORECASE),
            "issues": re.compile(r'\b(problem|issue|error|bug|wrong|incorrect|failed)\b', re.IGNORECASE),
            "ratings": re.compile(r'\b([1-5])\s*(?:out of|/)\s*5\b|\b([1-5])\s*stars?\b', re.IGNORECASE)
        }
        
        self.logger.info("🔄 Processador de Feedback Inteligente inicializado")
    
    async def process_feedback(
        self,
        feedback_text: str,
        session_id: str,
        user_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        explicit_rating: Optional[int] = None
    ) -> ProcessedFeedback:
        """
        Processa feedback do usuário
        
        Args:
            feedback_text: Texto do feedback
            session_id: ID da sessão
            user_id: ID do usuário (opcional)
            agent_id: ID do agente específico (opcional)
            explicit_rating: Rating explícito (1-5)
            
        Returns:
            Feedback processado
        """
        feedback_id = f"fb_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        self.logger.info(f"🔄 Processando feedback: {feedback_id}")
        
        try:
            # 1. Análise de sentimento
            sentiment_score, sentiment_level, confidence = await self._analyze_sentiment(feedback_text)
            
            # 2. Categorização
            categories = await self._categorize_feedback(feedback_text)
            
            # 3. Priorização
            priority = await self._determine_priority(feedback_text, sentiment_level)
            
            # 4. Extração de informações
            key_phrases = await self._extract_key_phrases(feedback_text)
            mentioned_agents = await self._extract_mentioned_agents(feedback_text)
            specific_issues = await self._extract_issues(feedback_text)
            suggestions = await self._extract_suggestions(feedback_text)
            
            # 5. Inferir rating se não fornecido
            rating_inferred = explicit_rating or await self._infer_rating(sentiment_score, feedback_text)
            
            # 6. Calcular scores
            urgency_score = await self._calculate_urgency_score(feedback_text, sentiment_level)
            actionability_score = await self._calculate_actionability_score(feedback_text, suggestions)
            
            # Criar feedback processado
            processed = ProcessedFeedback(
                feedback_id=feedback_id,
                original_feedback=feedback_text,
                session_id=session_id,
                user_id=user_id,
                agent_id=agent_id,
                sentiment_score=sentiment_score,
                sentiment_level=sentiment_level,
                confidence=confidence,
                categories=categories,
                priority=priority,
                key_phrases=key_phrases,
                mentioned_agents=mentioned_agents,
                specific_issues=specific_issues,
                suggestions=suggestions,
                rating_inferred=rating_inferred,
                urgency_score=urgency_score,
                actionability_score=actionability_score,
                processed_at=datetime.now()
            )
            
            # Cache do feedback processado
            self.processed_feedback[feedback_id] = processed
            
            # Processar insights imediatamente se crítico
            if priority == FeedbackPriority.CRITICAL:
                await self._process_critical_feedback(processed)
            
            self.logger.info(f"✅ Feedback processado: {feedback_id} (sentimento: {sentiment_level.name})")
            return processed
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao processar feedback: {e}")
            raise
    
    async def _analyze_sentiment(self, text: str) -> Tuple[float, SentimentLevel, float]:
        """Analisa sentimento do texto"""
        if not self.nltk_available:
            return await self._analyze_sentiment_fallback(text)
        
        try:
            # Usar VADER para análise de sentimento
            scores = self.sentiment_analyzer.polarity_scores(text)
            compound_score = scores['compound']
            
            # Determinar nível de sentimento
            if compound_score >= 0.5:
                sentiment_level = SentimentLevel.VERY_POSITIVE
            elif compound_score >= 0.1:
                sentiment_level = SentimentLevel.POSITIVE
            elif compound_score <= -0.5:
                sentiment_level = SentimentLevel.VERY_NEGATIVE
            elif compound_score <= -0.1:
                sentiment_level = SentimentLevel.NEGATIVE
            else:
                sentiment_level = SentimentLevel.NEUTRAL
            
            # Calcular confiança baseada na magnitude
            confidence = min(1.0, abs(compound_score) + 0.3)
            
            return compound_score, sentiment_level, confidence
            
        except Exception as e:
            self.logger.warning(f"⚠️ Erro na análise VADER, usando fallback: {e}")
            return await self._analyze_sentiment_fallback(text)
    
    async def _analyze_sentiment_fallback(self, text: str) -> Tuple[float, SentimentLevel, float]:
        """Análise de sentimento de fallback usando palavras-chave"""
        text_lower = text.lower()
        
        positive_count = sum(1 for word in self.processing_config["positive_keywords"] if word in text_lower)
        negative_count = sum(1 for word in self.processing_config["negative_keywords"] if word in text_lower)
        
        # Calcular score simples
        total_words = len(text.split())
        if total_words == 0:
            return 0.0, SentimentLevel.NEUTRAL, 0.5
        
        positive_ratio = positive_count / total_words
        negative_ratio = negative_count / total_words
        
        score = positive_ratio - negative_ratio
        
        # Determinar nível
        if score > 0.05:
            sentiment_level = SentimentLevel.POSITIVE
        elif score < -0.05:
            sentiment_level = SentimentLevel.NEGATIVE
        else:
            sentiment_level = SentimentLevel.NEUTRAL
        
        confidence = min(1.0, abs(score) * 10 + 0.3)
        
        return score, sentiment_level, confidence
    
    async def _categorize_feedback(self, text: str) -> List[FeedbackCategory]:
        """Categoriza o feedback"""
        categories = []
        text_lower = text.lower()
        
        # Mapeamento de palavras-chave para categorias
        category_keywords = {
            FeedbackCategory.RESPONSE_QUALITY: [
                "response", "answer", "quality", "accurate", "correct", "helpful"
            ],
            FeedbackCategory.COLLABORATION_EFFECTIVENESS: [
                "collaboration", "teamwork", "together", "coordination", "synergy"
            ],
            FeedbackCategory.COMMUNICATION_CLARITY: [
                "clear", "understand", "confusing", "explanation", "clarity", "communication"
            ],
            FeedbackCategory.SOLUTION_RELEVANCE: [
                "solution", "relevant", "appropriate", "suitable", "fits", "addresses"
            ],
            FeedbackCategory.SPEED_PERFORMANCE: [
                "fast", "slow", "quick", "speed", "performance", "time", "delay"
            ],
            FeedbackCategory.EXPERTISE_ACCURACY: [
                "expert", "knowledge", "accurate", "technical", "professional", "skilled"
            ],
            FeedbackCategory.USER_EXPERIENCE: [
                "experience", "interface", "usability", "friendly", "intuitive", "easy"
            ],
            FeedbackCategory.TECHNICAL_DEPTH: [
                "technical", "detailed", "depth", "thorough", "comprehensive", "specific"
            ]
        }
        
        # Verificar cada categoria
        for category, keywords in category_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                categories.append(category)
        
        # Se nenhuma categoria específica, usar qualidade da resposta como padrão
        if not categories:
            categories.append(FeedbackCategory.RESPONSE_QUALITY)
        
        return categories
    
    async def _determine_priority(self, text: str, sentiment: SentimentLevel) -> FeedbackPriority:
        """Determina prioridade do feedback"""
        text_lower = text.lower()
        
        # Verificar palavras de urgência
        urgency_words = sum(1 for word in self.processing_config["urgency_keywords"] if word in text_lower)
        
        # Prioridade baseada em sentimento e urgência
        if sentiment == SentimentLevel.VERY_NEGATIVE or urgency_words >= 2:
            return FeedbackPriority.CRITICAL
        elif sentiment == SentimentLevel.NEGATIVE or urgency_words >= 1:
            return FeedbackPriority.HIGH
        elif sentiment == SentimentLevel.VERY_POSITIVE:
            return FeedbackPriority.MEDIUM  # Feedback positivo também é importante
        else:
            return FeedbackPriority.LOW
    
    async def _extract_key_phrases(self, text: str) -> List[str]:
        """Extrai frases-chave do feedback"""
        # Implementação simples - pode ser melhorada com NLP avançado
        sentences = text.split('.')
        key_phrases = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 100:  # Frases de tamanho m��dio
                key_phrases.append(sentence)
        
        return key_phrases[:self.processing_config["max_key_phrases"]]
    
    async def _extract_mentioned_agents(self, text: str) -> List[str]:
        """Extrai menções a agentes específicos"""
        matches = self.patterns["agent_mentions"].findall(text)
        
        # Mapear nomes para IDs de agentes
        name_to_id = {
            "ana": "ana_beatriz_costa",
            "carlos": "carlos_eduardo_santos",
            "sofia": "sofia_oliveira",
            "gabriel": "gabriel_mendes",
            "isabella": "isabella_santos",
            "lucas": "lucas_pereira",
            "mariana": "mariana_rodrigues",
            "pedro": "pedro_henrique_almeida"
        }
        
        agent_ids = []
        for match in matches:
            agent_id = name_to_id.get(match.lower())
            if agent_id and agent_id not in agent_ids:
                agent_ids.append(agent_id)
        
        return agent_ids
    
    async def _extract_issues(self, text: str) -> List[str]:
        """Extrai problemas específicos mencionados"""
        issues = []
        
        # Procurar por padrões de problemas
        sentences = text.split('.')
        for sentence in sentences:
            if self.patterns["issues"].search(sentence):
                issues.append(sentence.strip())
        
        return issues
    
    async def _extract_suggestions(self, text: str) -> List[str]:
        """Extrai sugestões do feedback"""
        suggestions = []
        
        # Procurar por padrões de sugestões
        sentences = text.split('.')
        for sentence in sentences:
            if self.patterns["suggestions"].search(sentence):
                suggestions.append(sentence.strip())
        
        return suggestions
    
    async def _infer_rating(self, sentiment_score: float, text: str) -> int:
        """Infere rating baseado no sentimento e texto"""
        # Primeiro, procurar por ratings explícitos no texto
        rating_matches = self.patterns["ratings"].findall(text)
        if rating_matches:
            for match in rating_matches:
                for rating in match:
                    if rating and rating.isdigit():
                        return int(rating)
        
        # Inferir baseado no sentimento
        if sentiment_score >= 0.5:
            return 5
        elif sentiment_score >= 0.1:
            return 4
        elif sentiment_score >= -0.1:
            return 3
        elif sentiment_score >= -0.5:
            return 2
        else:
            return 1
    
    async def _calculate_urgency_score(self, text: str, sentiment: SentimentLevel) -> float:
        """Calcula score de urgência"""
        text_lower = text.lower()
        
        # Contar palavras de urgência
        urgency_count = sum(1 for word in self.processing_config["urgency_keywords"] if word in text_lower)
        
        # Score base do sentimento
        sentiment_urgency = {
            SentimentLevel.VERY_NEGATIVE: 0.8,
            SentimentLevel.NEGATIVE: 0.6,
            SentimentLevel.NEUTRAL: 0.3,
            SentimentLevel.POSITIVE: 0.2,
            SentimentLevel.VERY_POSITIVE: 0.1
        }
        
        base_score = sentiment_urgency.get(sentiment, 0.3)
        urgency_bonus = min(0.3, urgency_count * 0.1)
        
        return min(1.0, base_score + urgency_bonus)
    
    async def _calculate_actionability_score(self, text: str, suggestions: List[str]) -> float:
        """Calcula score de acionabilidade"""
        # Score baseado na presença de sugestões específicas
        suggestion_score = min(0.5, len(suggestions) * 0.1)
        
        # Score baseado na especificidade do feedback
        specificity_indicators = ["specific", "exactly", "precisely", "should", "could", "would"]
        specificity_count = sum(1 for indicator in specificity_indicators if indicator in text.lower())
        specificity_score = min(0.3, specificity_count * 0.1)
        
        # Score baseado no comprimento (feedbacks mais longos tendem a ser mais acionáveis)
        length_score = min(0.2, len(text.split()) / 100)
        
        return min(1.0, suggestion_score + specificity_score + length_score)
    
    async def _process_critical_feedback(self, feedback: ProcessedFeedback):
        """Processa feedback crítico imediatamente"""
        self.logger.warning(f"🚨 Feedback crítico detectado: {feedback.feedback_id}")
        
        # Criar insight de alta prioridade
        insight = FeedbackInsight(
            insight_id=f"critical_{feedback.feedback_id}",
            insight_type="critical_issue",
            description=f"Feedback crítico detectado: {feedback.original_feedback[:100]}...",
            affected_agents=feedback.mentioned_agents or [],
            confidence=0.9,
            supporting_feedback=[feedback.feedback_id],
            recommended_actions=[
                "Investigar imediatamente",
                "Notificar equipe de desenvolvimento",
                "Implementar correção urgente"
            ],
            created_at=datetime.now()
        )
        
        self.feedback_insights.append(insight)
    
    async def analyze_feedback_trends(
        self,
        time_period_days: int = 30,
        min_samples: int = 5
    ) -> List[FeedbackTrend]:
        """Analisa tendências no feedback"""
        if len(self.processed_feedback) < min_samples:
            return []
        
        cutoff_date = datetime.now() - timedelta(days=time_period_days)
        recent_feedback = [
            fb for fb in self.processed_feedback.values()
            if fb.processed_at >= cutoff_date
        ]
        
        if len(recent_feedback) < min_samples:
            return []
        
        trends = []
        
        # Tendência de sentimento
        sentiment_scores = [fb.sentiment_score for fb in recent_feedback]
        if len(sentiment_scores) >= min_samples:
            # Calcular tendência usando regressão linear simples
            x = np.arange(len(sentiment_scores))
            slope = np.polyfit(x, sentiment_scores, 1)[0]
            
            direction = "improving" if slope > 0.01 else "declining" if slope < -0.01 else "stable"
            
            trend = FeedbackTrend(
                trend_id=f"sentiment_trend_{datetime.now().strftime('%Y%m%d')}",
                trend_type="sentiment",
                direction=direction,
                metric="average_sentiment",
                current_value=np.mean(sentiment_scores),
                change_rate=slope,
                time_period=time_period_days,
                significance=abs(slope) * 10,
                created_at=datetime.now()
            )
            trends.append(trend)
        
        # Tendência de ratings
        ratings = [fb.rating_inferred for fb in recent_feedback if fb.rating_inferred]
        if len(ratings) >= min_samples:
            x = np.arange(len(ratings))
            slope = np.polyfit(x, ratings, 1)[0]
            
            direction = "improving" if slope > 0.05 else "declining" if slope < -0.05 else "stable"
            
            trend = FeedbackTrend(
                trend_id=f"rating_trend_{datetime.now().strftime('%Y%m%d')}",
                trend_type="rating",
                direction=direction,
                metric="average_rating",
                current_value=np.mean(ratings),
                change_rate=slope,
                time_period=time_period_days,
                significance=abs(slope) * 2,
                created_at=datetime.now()
            )
            trends.append(trend)
        
        self.feedback_trends.extend(trends)
        return trends
    
    async def generate_feedback_insights(self) -> List[FeedbackInsight]:
        """Gera insights baseados no feedback processado"""
        insights = []
        
        if len(self.processed_feedback) < 3:
            return insights
        
        # Insight sobre agentes mais mencionados
        agent_mentions = defaultdict(int)
        for fb in self.processed_feedback.values():
            for agent in fb.mentioned_agents:
                agent_mentions[agent] += 1
        
        if agent_mentions:
            most_mentioned = max(agent_mentions.items(), key=lambda x: x[1])
            
            insight = FeedbackInsight(
                insight_id=f"agent_mentions_{datetime.now().strftime('%Y%m%d')}",
                insight_type="agent_attention",
                description=f"Agente {most_mentioned[0]} é o mais mencionado no feedback ({most_mentioned[1]} vezes)",
                affected_agents=[most_mentioned[0]],
                confidence=0.8,
                supporting_feedback=[
                    fb.feedback_id for fb in self.processed_feedback.values()
                    if most_mentioned[0] in fb.mentioned_agents
                ],
                recommended_actions=[
                    "Analisar feedback específico do agente",
                    "Identificar padrões de menção",
                    "Otimizar performance se necessário"
                ],
                created_at=datetime.now()
            )
            insights.append(insight)
        
        # Insight sobre categorias problemáticas
        negative_feedback = [
            fb for fb in self.processed_feedback.values()
            if fb.sentiment_level in [SentimentLevel.NEGATIVE, SentimentLevel.VERY_NEGATIVE]
        ]
        
        if negative_feedback:
            category_issues = defaultdict(int)
            for fb in negative_feedback:
                for category in fb.categories:
                    category_issues[category] += 1
            
            if category_issues:
                problem_category = max(category_issues.items(), key=lambda x: x[1])
                
                insight = FeedbackInsight(
                    insight_id=f"category_issues_{datetime.now().strftime('%Y%m%d')}",
                    insight_type="category_problem",
                    description=f"Categoria {problem_category[0].value} tem mais feedback negativo ({problem_category[1]} ocorrências)",
                    affected_agents=[],
                    confidence=0.7,
                    supporting_feedback=[
                        fb.feedback_id for fb in negative_feedback
                        if problem_category[0] in fb.categories
                    ],
                    recommended_actions=[
                        f"Focar melhorias em {problem_category[0].value}",
                        "Analisar feedback específico da categoria",
                        "Implementar correções direcionadas"
                    ],
                    created_at=datetime.now()
                )
                insights.append(insight)
        
        self.feedback_insights.extend(insights)
        return insights
    
    async def get_feedback_summary(self, time_period_days: int = 7) -> Dict[str, Any]:
        """Obtém resumo do feedback"""
        cutoff_date = datetime.now() - timedelta(days=time_period_days)
        recent_feedback = [
            fb for fb in self.processed_feedback.values()
            if fb.processed_at >= cutoff_date
        ]
        
        if not recent_feedback:
            return {"message": "Nenhum feedback recente encontrado"}
        
        # Estatísticas básicas
        total_feedback = len(recent_feedback)
        avg_sentiment = np.mean([fb.sentiment_score for fb in recent_feedback])
        avg_rating = np.mean([fb.rating_inferred for fb in recent_feedback if fb.rating_inferred])
        
        # Distribuição de sentimento
        sentiment_dist = Counter([fb.sentiment_level.name for fb in recent_feedback])
        
        # Categorias mais comuns
        all_categories = []
        for fb in recent_feedback:
            all_categories.extend([cat.value for cat in fb.categories])
        category_dist = Counter(all_categories)
        
        # Agentes mais mencionados
        all_agents = []
        for fb in recent_feedback:
            all_agents.extend(fb.mentioned_agents)
        agent_mentions = Counter(all_agents)
        
        return {
            "period_days": time_period_days,
            "total_feedback": total_feedback,
            "metrics": {
                "avg_sentiment": round(avg_sentiment, 3),
                "avg_rating": round(avg_rating, 2) if avg_rating else None,
                "positive_ratio": (sentiment_dist.get("POSITIVE", 0) + sentiment_dist.get("VERY_POSITIVE", 0)) / total_feedback
            },
            "distributions": {
                "sentiment": dict(sentiment_dist),
                "categories": dict(category_dist.most_common(5)),
                "agent_mentions": dict(agent_mentions.most_common(5))
            },
            "insights_count": len(self.feedback_insights),
            "trends_count": len(self.feedback_trends)
        }


# Instância global do processador
feedback_processor = FeedbackProcessor()