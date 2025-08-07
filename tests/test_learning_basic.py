"""
Testes Básicos para Sistema de Aprendizado Contínuo
Melhoria #7 - Testes simplificados sem dependências complexas

Testa funcionalidades básicas do sistema de aprendizado:
- Inicialização
- Registro de eventos
- Processamento de feedback
- Métricas básicas

Criado por: David Simer
"""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock
import sys
import os
import tempfile
import shutil

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestLearningSystemBasic:
    """Testes básicos para o sistema de aprendizado"""
    
    def test_learning_enums(self):
        """Testa enums do sistema de aprendizado"""
        from learning.continuous_learning_system import LearningEventType, FeedbackType, LearningStrategy
        
        # Verificar tipos de eventos
        assert LearningEventType.USER_FEEDBACK.value == "user_feedback"
        assert LearningEventType.SUCCESS_PATTERN.value == "success_pattern"
        assert LearningEventType.PERFORMANCE_OPTIMIZATION.value == "performance_optimization"
        
        # Verificar tipos de feedback
        assert FeedbackType.POSITIVE.value == "positive"
        assert FeedbackType.NEGATIVE.value == "negative"
        assert FeedbackType.NEUTRAL.value == "neutral"
        
        # Verificar estratégias
        assert LearningStrategy.REINFORCEMENT.value == "reinforcement"
        assert LearningStrategy.PATTERN_RECOGNITION.value == "pattern_recognition"
    
    def test_learning_dataclasses(self):
        """Testa dataclasses do sistema"""
        from learning.continuous_learning_system import LearningEvent, FeedbackEvent, LearningMetrics
        from learning.continuous_learning_system import LearningEventType, FeedbackType
        
        # Teste LearningEvent
        event = LearningEvent(
            event_id="test_event",
            event_type=LearningEventType.SUCCESS_PATTERN,
            agent_id="test_agent",
            session_id="test_session",
            timestamp=datetime.now(),
            data={"test": "data"},
            impact_score=0.8
        )
        
        assert event.event_id == "test_event"
        assert event.event_type == LearningEventType.SUCCESS_PATTERN
        assert event.impact_score == 0.8
        assert not event.processed  # Default False
        
        # Teste FeedbackEvent
        feedback = FeedbackEvent(
            feedback_id="test_feedback",
            session_id="test_session",
            user_id="test_user",
            feedback_type=FeedbackType.POSITIVE,
            rating=5,
            comment="Excelente!",
            specific_agent="test_agent",
            timestamp=datetime.now()
        )
        
        assert feedback.feedback_id == "test_feedback"
        assert feedback.rating == 5
        assert feedback.comment == "Excelente!"
        
        # Teste LearningMetrics
        metrics = LearningMetrics(
            agent_id="test_agent",
            performance_score=0.8,
            improvement_rate=0.1,
            feedback_score=0.9,
            collaboration_effectiveness=0.7,
            knowledge_growth=0.05,
            adaptation_speed=0.6,
            last_updated=datetime.now()
        )
        
        assert metrics.agent_id == "test_agent"
        assert metrics.performance_score == 0.8
        assert metrics.feedback_score == 0.9
    
    @pytest.mark.asyncio
    async def test_learning_system_initialization(self):
        """Testa inicialização básica do sistema"""
        from learning.continuous_learning_system import ContinuousLearningSystem
        
        # Criar diretório temporário
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Inicializar sistema
            system = ContinuousLearningSystem(data_dir=temp_dir)
            
            # Verificar inicialização
            assert system.is_learning_active
            assert len(system.learning_events) == 0
            assert len(system.feedback_events) == 0
            assert len(system.agent_metrics) == 0
            assert system.data_dir == temp_dir
            
            # Verificar configurações padrão
            assert "feedback_weight" in system.learning_config
            assert "learning_rate" in system.learning_config
            assert system.learning_config["feedback_weight"] == 0.3
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_record_feedback_basic(self):
        """Testa registro básico de feedback"""
        from learning.continuous_learning_system import ContinuousLearningSystem, FeedbackType
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            system = ContinuousLearningSystem(data_dir=temp_dir)
            
            # Registrar feedback
            feedback_id = await system.record_feedback(
                session_id="test_session",
                feedback_type=FeedbackType.POSITIVE,
                rating=5,
                comment="Ótimo trabalho!",
                user_id="test_user"
            )
            
            # Verificar registro
            assert feedback_id.startswith("feedback_")
            assert len(system.feedback_events) == 1
            
            feedback = system.feedback_events[0]
            assert feedback.feedback_type == FeedbackType.POSITIVE
            assert feedback.rating == 5
            assert feedback.comment == "Ótimo trabalho!"
            assert feedback.user_id == "test_user"
            assert not feedback.processed
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_record_learning_event_basic(self):
        """Testa registro básico de evento de aprendizado"""
        from learning.continuous_learning_system import ContinuousLearningSystem, LearningEventType
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            system = ContinuousLearningSystem(data_dir=temp_dir)
            
            # Registrar evento
            event_id = await system.record_learning_event(
                event_type=LearningEventType.SUCCESS_PATTERN,
                agent_id="test_agent",
                session_id="test_session",
                data={"pattern": "collaboration_success"},
                impact_score=0.8
            )
            
            # Verificar registro
            assert event_id.startswith("event_")
            assert len(system.learning_events) == 1
            
            event = system.learning_events[0]
            assert event.event_type == LearningEventType.SUCCESS_PATTERN
            assert event.agent_id == "test_agent"
            assert event.session_id == "test_session"
            assert event.impact_score == 0.8
            assert event.data["pattern"] == "collaboration_success"
            assert not event.processed
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.mark.asyncio
    async def test_system_status_basic(self):
        """Testa status básico do sistema"""
        from learning.continuous_learning_system import ContinuousLearningSystem, LearningEventType, FeedbackType
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            system = ContinuousLearningSystem(data_dir=temp_dir)
            
            # Adicionar alguns dados
            await system.record_feedback(
                session_id="test1",
                feedback_type=FeedbackType.POSITIVE,
                rating=5
            )
            
            await system.record_learning_event(
                event_type=LearningEventType.SUCCESS_PATTERN,
                agent_id="test_agent",
                session_id="test1",
                data={"test": "data"}
            )
            
            # Obter status
            status = await system.get_system_learning_status()
            
            # Verificar status
            assert "system_status" in status
            assert "learning_metrics" in status
            assert "agent_metrics" in status
            assert "learning_config" in status
            
            assert status["system_status"]["is_active"]
            assert status["learning_metrics"]["total_events"] == 1
            assert status["learning_metrics"]["total_feedback"] == 1
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestPatternAnalyzerBasic:
    """Testes básicos para o analisador de padrões"""
    
    def test_pattern_analyzer_initialization(self):
        """Testa inicialização do analisador de padrões"""
        from learning.pattern_analyzer import PatternAnalyzer, PatternType
        
        analyzer = PatternAnalyzer()
        
        # Verificar inicialização
        assert analyzer.analysis_config["min_pattern_frequency"] == 3
        assert analyzer.analysis_config["min_confidence_threshold"] == 0.6
        assert len(analyzer.pattern_cache) == 0
        assert len(analyzer.analysis_cache) == 0
        
        # Verificar enums
        assert PatternType.SUCCESS_COLLABORATION.value == "success_collaboration"
        assert PatternType.USER_PREFERENCE.value == "user_preference"
        assert PatternType.TEMPORAL_TREND.value == "temporal_trend"
    
    def test_pattern_dataclasses(self):
        """Testa dataclasses do analisador"""
        from learning.pattern_analyzer import IdentifiedPattern, PatternFeature, PatternType
        
        # Teste PatternFeature
        feature = PatternFeature(
            feature_name="test_feature",
            feature_value="test_value",
            importance=0.8,
            frequency=5
        )
        
        assert feature.feature_name == "test_feature"
        assert feature.importance == 0.8
        assert feature.frequency == 5
        
        # Teste IdentifiedPattern
        pattern = IdentifiedPattern(
            pattern_id="test_pattern",
            pattern_type=PatternType.SUCCESS_COLLABORATION,
            confidence=0.9,
            features=[feature],
            context="Test context",
            success_rate=0.85,
            usage_count=10,
            agents_involved=["agent1", "agent2"],
            time_range=(datetime.now(), datetime.now()),
            created_at=datetime.now(),
            last_updated=datetime.now()
        )
        
        assert pattern.pattern_id == "test_pattern"
        assert pattern.confidence == 0.9
        assert pattern.success_rate == 0.85
        assert len(pattern.features) == 1
        assert len(pattern.agents_involved) == 2


class TestFeedbackProcessorBasic:
    """Testes básicos para o processador de feedback"""
    
    def test_feedback_processor_initialization(self):
        """Testa inicialização do processador de feedback"""
        from learning.feedback_processor import FeedbackProcessor, FeedbackCategory, SentimentLevel
        
        processor = FeedbackProcessor()
        
        # Verificar inicialização
        assert processor.processing_config["min_feedback_length"] == 10
        assert processor.processing_config["max_key_phrases"] == 10
        assert len(processor.processed_feedback) == 0
        
        # Verificar enums
        assert FeedbackCategory.RESPONSE_QUALITY.value == "response_quality"
        assert FeedbackCategory.COLLABORATION_EFFECTIVENESS.value == "collaboration_effectiveness"
        
        assert SentimentLevel.POSITIVE.value == 1
        assert SentimentLevel.NEGATIVE.value == -1
        assert SentimentLevel.NEUTRAL.value == 0
    
    @pytest.mark.asyncio
    async def test_basic_sentiment_analysis(self):
        """Testa análise básica de sentimento"""
        from learning.feedback_processor import FeedbackProcessor, SentimentLevel
        
        processor = FeedbackProcessor()
        
        # Teste com texto positivo
        positive_text = "Excelente trabalho! Muito útil e preciso."
        sentiment_score, sentiment_level, confidence = await processor._analyze_sentiment_fallback(positive_text)
        
        assert sentiment_level in [SentimentLevel.POSITIVE, SentimentLevel.NEUTRAL]
        assert 0 <= confidence <= 1
        
        # Teste com texto negativo
        negative_text = "Terrível resposta! Muito confusa e inútil."
        sentiment_score, sentiment_level, confidence = await processor._analyze_sentiment_fallback(negative_text)
        
        assert sentiment_level in [SentimentLevel.NEGATIVE, SentimentLevel.NEUTRAL]
        assert 0 <= confidence <= 1
    
    @pytest.mark.asyncio
    async def test_feedback_categorization(self):
        """Testa categorização básica de feedback"""
        from learning.feedback_processor import FeedbackProcessor, FeedbackCategory
        
        processor = FeedbackProcessor()
        
        # Teste com feedback sobre qualidade
        quality_text = "A resposta foi muito precisa e útil"
        categories = await processor._categorize_feedback(quality_text)
        
        assert len(categories) > 0
        assert FeedbackCategory.RESPONSE_QUALITY in categories
        
        # Teste com feedback sobre colaboração
        collab_text = "A colaboração entre os agentes foi excelente"
        categories = await processor._categorize_feedback(collab_text)
        
        assert len(categories) > 0
        # Pode ou não detectar colaboração dependendo das palavras-chave


class TestLearningIntegrationBasic:
    """Testes básicos para integração de aprendizado"""
    
    def test_learning_integration_initialization(self):
        """Testa inicialização da integração"""
        from learning.learning_integration import LearningIntegration
        
        integration = LearningIntegration()
        
        # Verificar inicialização
        assert not integration.is_active  # Não ativo até initialize()
        assert integration.orchestrator is None
        assert integration.integration_config["auto_capture_events"]
        assert integration.integration_config["real_time_adaptation"]
        assert integration.adaptations_this_hour == 0


class TestLearningSystemIntegrationBasic:
    """Testes básicos de integração entre componentes"""
    
    @pytest.mark.asyncio
    async def test_basic_learning_flow(self):
        """Testa fluxo básico de aprendizado"""
        from learning.continuous_learning_system import ContinuousLearningSystem, FeedbackType, LearningEventType
        from learning.feedback_processor import FeedbackProcessor
        
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Inicializar componentes
            learning_sys = ContinuousLearningSystem(data_dir=temp_dir)
            feedback_proc = FeedbackProcessor()
            
            # 1. Registrar feedback
            feedback_id = await learning_sys.record_feedback(
                session_id="integration_test",
                feedback_type=FeedbackType.POSITIVE,
                rating=5,
                comment="Teste de integração básica"
            )
            
            # 2. Processar feedback
            processed = await feedback_proc.process_feedback(
                "Teste de integração básica",
                "integration_test",
                "test_user"
            )
            
            # 3. Registrar evento de aprendizado
            event_id = await learning_sys.record_learning_event(
                LearningEventType.SUCCESS_PATTERN,
                "test_agent",
                "integration_test",
                {"integration": "test"}
            )
            
            # Verificar integração
            assert len(learning_sys.feedback_events) == 1
            assert len(learning_sys.learning_events) == 1
            assert processed.feedback_id.startswith("fb_")
            
            # Verificar status
            status = await learning_sys.get_system_learning_status()
            assert status["learning_metrics"]["total_feedback"] == 1
            assert status["learning_metrics"]["total_events"] == 1
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])