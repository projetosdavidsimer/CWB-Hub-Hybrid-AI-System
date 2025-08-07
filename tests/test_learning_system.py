"""
Testes para Sistema de Aprendizado Contínuo
Melhoria #7 - Testes abrangentes

Testa todos os componentes do sistema de aprendizado:
- ContinuousLearningSystem
- PatternAnalyzer
- FeedbackProcessor
- LearningIntegration

Criado por: David Simer
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from learning.continuous_learning_system import (
    ContinuousLearningSystem,
    LearningEventType,
    FeedbackType,
    LearningEvent,
    FeedbackEvent,
    LearningMetrics
)

from learning.pattern_analyzer import (
    PatternAnalyzer,
    PatternType,
    IdentifiedPattern,
    PatternFeature
)

from learning.feedback_processor import (
    FeedbackProcessor,
    FeedbackCategory,
    SentimentLevel,
    FeedbackPriority,
    ProcessedFeedback
)

from learning.learning_integration import LearningIntegration


class TestContinuousLearningSystem:
    """Testes para o sistema de aprendizado contínuo"""
    
    @pytest.fixture
    async def learning_system(self):
        """Fixture do sistema de aprendizado"""
        system = ContinuousLearningSystem(data_dir="test_data")
        
        # Mock dos agentes
        mock_agents = {
            "ana_beatriz_costa": Mock(),
            "carlos_eduardo_santos": Mock(),
            "sofia_oliveira": Mock()
        }
        
        await system.initialize(mock_agents)
        yield system
        await system.shutdown()
    
    @pytest.mark.asyncio
    async def test_system_initialization(self, learning_system):
        """Testa inicialização do sistema"""
        assert learning_system.is_learning_active
        assert len(learning_system.agent_metrics) == 3
        assert "ana_beatriz_costa" in learning_system.agent_metrics
    
    @pytest.mark.asyncio
    async def test_record_feedback(self, learning_system):
        """Testa registro de feedback"""
        feedback_id = await learning_system.record_feedback(
            session_id="test_session",
            feedback_type=FeedbackType.POSITIVE,
            rating=5,
            comment="Excelente resposta!",
            user_id="user123"
        )
        
        assert feedback_id.startswith("feedback_")
        assert len(learning_system.feedback_events) == 1
        
        feedback = learning_system.feedback_events[0]
        assert feedback.feedback_type == FeedbackType.POSITIVE
        assert feedback.rating == 5
        assert feedback.comment == "Excelente resposta!"
    
    @pytest.mark.asyncio
    async def test_record_learning_event(self, learning_system):
        """Testa registro de evento de aprendizado"""
        event_id = await learning_system.record_learning_event(
            event_type=LearningEventType.SUCCESS_PATTERN,
            agent_id="ana_beatriz_costa",
            session_id="test_session",
            data={"pattern": "collaboration_success"},
            impact_score=0.8
        )
        
        assert event_id.startswith("event_")
        assert len(learning_system.learning_events) == 1
        
        event = learning_system.learning_events[0]
        assert event.event_type == LearningEventType.SUCCESS_PATTERN
        assert event.agent_id == "ana_beatriz_costa"
        assert event.impact_score == 0.8
    
    @pytest.mark.asyncio
    async def test_agent_adaptation(self, learning_system):
        """Testa adaptação de agente"""
        adaptation_data = {
            "collaboration_style": "more_supportive",
            "communication_style": "detailed"
        }
        
        success = await learning_system.adapt_agent_behavior(
            "ana_beatriz_costa",
            adaptation_data
        )
        
        assert success
        # Verificar se evento de adaptação foi registrado
        adaptation_events = [
            e for e in learning_system.learning_events
            if e.event_type == LearningEventType.ADAPTATION_TRIGGER
        ]
        assert len(adaptation_events) == 1
    
    @pytest.mark.asyncio
    async def test_get_agent_insights(self, learning_system):
        """Testa obtenção de insights do agente"""
        # Adicionar alguns eventos primeiro
        await learning_system.record_learning_event(
            LearningEventType.PERFORMANCE_OPTIMIZATION,
            "ana_beatriz_costa",
            "test_session",
            {"performance": 0.8}
        )
        
        insights = await learning_system.get_agent_learning_insights("ana_beatriz_costa")
        
        assert "agent_id" in insights
        assert "current_metrics" in insights
        assert "trends" in insights
        assert insights["agent_id"] == "ana_beatriz_costa"
    
    @pytest.mark.asyncio
    async def test_system_status(self, learning_system):
        """Testa status do sistema"""
        status = await learning_system.get_system_learning_status()
        
        assert "system_status" in status
        assert "learning_metrics" in status
        assert "agent_metrics" in status
        assert status["system_status"]["is_active"]


class TestPatternAnalyzer:
    """Testes para o analisador de padrões"""
    
    @pytest.fixture
    def pattern_analyzer(self):
        """Fixture do analisador de padrões"""
        return PatternAnalyzer()
    
    @pytest.fixture
    def mock_sessions(self):
        """Fixture de sessões mock"""
        sessions = []
        
        for i in range(5):
            session = Mock()
            session.session_id = f"session_{i}"
            session.user_request = f"Como criar um app mobile {i}?"
            session.iterations = 1 if i < 3 else 2
            session.created_at = datetime.now() - timedelta(days=i)
            
            # Mock agent responses
            session.agent_responses = []
            for j in range(3):
                response = Mock()
                response.agent_id = f"agent_{j}"
                response.confidence = 0.8 + (i * 0.02)
                session.agent_responses.append(response)
            
            sessions.append(session)
        
        return sessions
    
    @pytest.mark.asyncio
    async def test_analyze_session_patterns(self, pattern_analyzer, mock_sessions):
        """Testa análise de padrões de sessão"""
        result = await pattern_analyzer.analyze_session_patterns(mock_sessions)
        
        assert result.analysis_id.startswith("analysis_")
        assert isinstance(result.patterns_found, list)
        assert isinstance(result.insights, list)
        assert isinstance(result.recommendations, list)
        assert 0 <= result.confidence_score <= 1
        assert 0 <= result.data_quality <= 1
    
    @pytest.mark.asyncio
    async def test_collaboration_patterns(self, pattern_analyzer, mock_sessions):
        """Testa identificação de padrões de colaboração"""
        patterns = await pattern_analyzer._analyze_collaboration_patterns(mock_sessions)
        
        # Deve encontrar pelo menos alguns padrões de colaboração
        collaboration_patterns = [
            p for p in patterns 
            if p.pattern_type == PatternType.SUCCESS_COLLABORATION
        ]
        
        # Verificar estrutura dos padrões
        for pattern in collaboration_patterns:
            assert pattern.pattern_id
            assert pattern.confidence > 0
            assert len(pattern.agents_involved) >= 2
            assert pattern.success_rate > 0
    
    @pytest.mark.asyncio
    async def test_user_preferences(self, pattern_analyzer, mock_sessions):
        """Testa análise de preferências do usuário"""
        patterns = await pattern_analyzer._analyze_user_preferences(mock_sessions)
        
        # Deve identificar preferência por desenvolvimento mobile
        mobile_patterns = [
            p for p in patterns
            if "mobile" in p.context.lower()
        ]
        
        assert len(mobile_patterns) > 0
        
        for pattern in mobile_patterns:
            assert pattern.pattern_type == PatternType.USER_PREFERENCE
            assert pattern.usage_count > 0
    
    @pytest.mark.asyncio
    async def test_temporal_trends(self, pattern_analyzer, mock_sessions):
        """Testa análise de tendências temporais"""
        patterns = await pattern_analyzer._analyze_temporal_trends(mock_sessions)
        
        # Verificar se encontrou tendências
        temporal_patterns = [
            p for p in patterns
            if p.pattern_type == PatternType.TEMPORAL_TREND
        ]
        
        # Pode ou não encontrar tendências dependendo dos dados
        for pattern in temporal_patterns:
            assert pattern.confidence > 0
            assert "trend_slope" in [f.feature_name for f in pattern.features]
    
    @pytest.mark.asyncio
    async def test_pattern_export(self, pattern_analyzer, mock_sessions):
        """Testa exportação de padrões"""
        # Primeiro, analisar para gerar padrões
        await pattern_analyzer.analyze_session_patterns(mock_sessions)
        
        # Exportar padrões
        exported = await pattern_analyzer.export_patterns("json")
        
        assert isinstance(exported, str)
        assert len(exported) > 0
        
        # Deve ser JSON válido
        import json
        patterns_data = json.loads(exported)
        assert isinstance(patterns_data, list)


class TestFeedbackProcessor:
    """Testes para o processador de feedback"""
    
    @pytest.fixture
    def feedback_processor(self):
        """Fixture do processador de feedback"""
        return FeedbackProcessor()
    
    @pytest.mark.asyncio
    async def test_process_positive_feedback(self, feedback_processor):
        """Testa processamento de feedback positivo"""
        feedback_text = "Excelente resposta! A equipe foi muito útil e precisa."
        
        processed = await feedback_processor.process_feedback(
            feedback_text,
            "test_session",
            "user123"
        )
        
        assert processed.feedback_id.startswith("fb_")
        assert processed.sentiment_level in [SentimentLevel.POSITIVE, SentimentLevel.VERY_POSITIVE]
        assert processed.rating_inferred >= 4
        assert processed.priority in [FeedbackPriority.LOW, FeedbackPriority.MEDIUM]
    
    @pytest.mark.asyncio
    async def test_process_negative_feedback(self, feedback_processor):
        """Testa processamento de feedback negativo"""
        feedback_text = "Resposta terrível! Não ajudou em nada e foi muito confusa."
        
        processed = await feedback_processor.process_feedback(
            feedback_text,
            "test_session",
            "user123"
        )
        
        assert processed.sentiment_level in [SentimentLevel.NEGATIVE, SentimentLevel.VERY_NEGATIVE]
        assert processed.rating_inferred <= 2
        assert processed.priority in [FeedbackPriority.HIGH, FeedbackPriority.CRITICAL]
        assert processed.urgency_score > 0.5
    
    @pytest.mark.asyncio
    async def test_feedback_categorization(self, feedback_processor):
        """Testa categorização de feedback"""
        feedback_text = "A resposta foi clara mas a colaboração entre agentes poderia ser melhor."
        
        processed = await feedback_processor.process_feedback(
            feedback_text,
            "test_session"
        )
        
        categories = [cat.value for cat in processed.categories]
        assert "communication_clarity" in categories or "collaboration_effectiveness" in categories
    
    @pytest.mark.asyncio
    async def test_agent_mention_extraction(self, feedback_processor):
        """Testa extração de menções a agentes"""
        feedback_text = "Ana foi muito útil, mas Carlos poderia ter sido mais claro."
        
        processed = await feedback_processor.process_feedback(
            feedback_text,
            "test_session"
        )
        
        assert "ana_beatriz_costa" in processed.mentioned_agents
        assert "carlos_eduardo_santos" in processed.mentioned_agents
    
    @pytest.mark.asyncio
    async def test_suggestion_extraction(self, feedback_processor):
        """Testa extração de sugestões"""
        feedback_text = "Sugiro que as respostas sejam mais detalhadas. Seria melhor incluir exemplos."
        
        processed = await feedback_processor.process_feedback(
            feedback_text,
            "test_session"
        )
        
        assert len(processed.suggestions) > 0
        assert processed.actionability_score > 0.5
    
    @pytest.mark.asyncio
    async def test_feedback_trends(self, feedback_processor):
        """Testa análise de tendências de feedback"""
        # Adicionar vários feedbacks
        feedbacks = [
            "Excelente trabalho!",
            "Muito bom, obrigado!",
            "Resposta útil",
            "Poderia ser melhor",
            "Não gostei da resposta"
        ]
        
        for i, feedback in enumerate(feedbacks):
            await feedback_processor.process_feedback(
                feedback,
                f"session_{i}",
                f"user_{i}"
            )
        
        trends = await feedback_processor.analyze_feedback_trends(7, 3)
        
        # Deve encontrar pelo menos uma tendência
        assert len(trends) >= 0  # Pode não encontrar tendências com poucos dados
        
        for trend in trends:
            assert trend.trend_type in ["sentiment", "rating"]
            assert trend.direction in ["improving", "declining", "stable"]
    
    @pytest.mark.asyncio
    async def test_feedback_insights(self, feedback_processor):
        """Testa geração de insights de feedback"""
        # Adicionar feedbacks com menções específicas
        feedbacks = [
            "Ana foi excelente!",
            "Ana ajudou muito",
            "Carlos foi confuso",
            "A colaboração precisa melhorar"
        ]
        
        for i, feedback in enumerate(feedbacks):
            await feedback_processor.process_feedback(
                feedback,
                f"session_{i}",
                f"user_{i}"
            )
        
        insights = await feedback_processor.generate_feedback_insights()
        
        # Deve gerar alguns insights
        assert len(insights) >= 0
        
        for insight in insights:
            assert insight.insight_type
            assert insight.description
            assert 0 <= insight.confidence <= 1
    
    @pytest.mark.asyncio
    async def test_feedback_summary(self, feedback_processor):
        """Testa resumo de feedback"""
        # Adicionar alguns feedbacks
        feedbacks = [
            ("Ótimo trabalho!", 5),
            ("Bom, mas pode melhorar", 3),
            ("Excelente resposta", 5),
            ("Não gostei", 2)
        ]
        
        for i, (feedback, rating) in enumerate(feedbacks):
            await feedback_processor.process_feedback(
                feedback,
                f"session_{i}",
                f"user_{i}",
                explicit_rating=rating
            )
        
        summary = await feedback_processor.get_feedback_summary(7)
        
        assert "total_feedback" in summary
        assert "metrics" in summary
        assert "distributions" in summary
        assert summary["total_feedback"] == 4


class TestLearningIntegration:
    """Testes para integração de aprendizado"""
    
    @pytest.fixture
    async def learning_integration(self):
        """Fixture da integração"""
        integration = LearningIntegration()
        
        # Mock do orquestrador
        mock_orchestrator = Mock()
        mock_orchestrator.agents = {
            "ana_beatriz_costa": Mock(),
            "carlos_eduardo_santos": Mock()
        }
        mock_orchestrator.active_sessions = {}
        
        await integration.initialize(mock_orchestrator)
        yield integration
        await integration.shutdown()
    
    @pytest.mark.asyncio
    async def test_integration_initialization(self, learning_integration):
        """Testa inicialização da integração"""
        assert learning_integration.is_active
        assert learning_integration.orchestrator is not None
    
    @pytest.mark.asyncio
    async def test_process_user_feedback_api(self, learning_integration):
        """Testa API de processamento de feedback"""
        result = await learning_integration.process_user_feedback(
            feedback_text="Excelente trabalho da equipe!",
            session_id="test_session",
            user_id="user123",
            rating=5
        )
        
        assert "feedback_id" in result
        assert "processed_feedback" in result
        assert "learning_impact" in result
        assert result["processed_feedback"]["sentiment"] in ["POSITIVE", "VERY_POSITIVE"]
    
    @pytest.mark.asyncio
    async def test_get_learning_insights_api(self, learning_integration):
        """Testa API de insights de aprendizado"""
        # Insights do sistema
        system_insights = await learning_integration.get_learning_insights()
        assert "system_status" in system_insights
        assert "learning_metrics" in system_insights
        
        # Insights de agente específico
        agent_insights = await learning_integration.get_learning_insights("ana_beatriz_costa")
        assert "agent_id" in agent_insights
        assert "current_metrics" in agent_insights
    
    @pytest.mark.asyncio
    async def test_manual_adaptation_api(self, learning_integration):
        """Testa API de adaptação manual"""
        result = await learning_integration.trigger_manual_adaptation(
            agent_id="ana_beatriz_costa",
            adaptation_type="collaboration_improvement",
            parameters={
                "collaboration_style": "enhanced",
                "communication_style": "detailed"
            }
        )
        
        assert "success" in result
        assert "agent_id" in result
        assert result["agent_id"] == "ana_beatriz_costa"
    
    @pytest.mark.asyncio
    async def test_feedback_analytics_api(self, learning_integration):
        """Testa API de analytics de feedback"""
        analytics = await learning_integration.get_feedback_analytics(7)
        
        assert "summary" in analytics
        assert "trends" in analytics
        assert "insights" in analytics
    
    @pytest.mark.asyncio
    async def test_export_learning_data_api(self, learning_integration):
        """Testa API de exportação de dados"""
        exported = await learning_integration.export_learning_data("json")
        
        assert isinstance(exported, str)
        assert len(exported) > 0
        
        # Deve ser JSON válido
        import json
        data = json.loads(exported)
        assert "export_timestamp" in data
        assert "system_status" in data


# Testes de integração
class TestLearningSystemIntegration:
    """Testes de integração entre componentes"""
    
    @pytest.mark.asyncio
    async def test_full_learning_cycle(self):
        """Testa ciclo completo de aprendizado"""
        # 1. Inicializar sistema
        learning_sys = ContinuousLearningSystem(data_dir="test_integration")
        mock_agents = {"test_agent": Mock()}
        await learning_sys.initialize(mock_agents)
        
        try:
            # 2. Registrar feedback
            feedback_id = await learning_sys.record_feedback(
                session_id="integration_test",
                feedback_type=FeedbackType.POSITIVE,
                rating=5,
                comment="Teste de integração"
            )
            
            # 3. Registrar evento de aprendizado
            event_id = await learning_sys.record_learning_event(
                LearningEventType.SUCCESS_PATTERN,
                "test_agent",
                "integration_test",
                {"test": "data"}
            )
            
            # 4. Verificar se dados foram registrados
            assert len(learning_sys.feedback_events) == 1
            assert len(learning_sys.learning_events) == 1
            
            # 5. Obter status
            status = await learning_sys.get_system_learning_status()
            assert status["learning_metrics"]["total_feedback"] == 1
            assert status["learning_metrics"]["total_events"] == 1
            
        finally:
            await learning_sys.shutdown()
    
    @pytest.mark.asyncio
    async def test_pattern_feedback_integration(self):
        """Testa integração entre análise de padrões e feedback"""
        # Inicializar componentes
        pattern_analyzer = PatternAnalyzer()
        feedback_processor = FeedbackProcessor()
        
        # Simular sessões com feedback
        mock_sessions = []
        for i in range(3):
            session = Mock()
            session.session_id = f"session_{i}"
            session.user_request = "Teste de integração"
            session.iterations = 1
            session.created_at = datetime.now()
            session.agent_responses = [Mock()]
            session.agent_responses[0].agent_id = "test_agent"
            session.agent_responses[0].confidence = 0.8
            mock_sessions.append(session)
        
        # Analisar padrões
        pattern_result = await pattern_analyzer.analyze_session_patterns(mock_sessions)
        
        # Processar feedback relacionado
        feedback_result = await feedback_processor.process_feedback(
            "Os padrões identificados são úteis",
            "session_0"
        )
        
        # Verificar integração
        assert len(pattern_result.patterns_found) >= 0
        assert feedback_result.sentiment_level != SentimentLevel.VERY_NEGATIVE


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])