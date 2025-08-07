"""
Sistema de Aprendizado Contínuo CWB Hub
Melhoria #7 - IA que aprende e evolui

Módulo completo de aprendizado contínuo que permite aos agentes CWB Hub
evoluírem através de feedback, padrões de sucesso e adaptação inteligente.

Componentes principais:
- ContinuousLearningSystem: Sistema principal de aprendizado
- PatternAnalyzer: Análise de padrões e tendências
- FeedbackProcessor: Processamento inteligente de feedback
- LearningIntegration: Integração com sistema principal

Criado por: David Simer
"""

from .continuous_learning_system import (
    ContinuousLearningSystem,
    LearningEventType,
    FeedbackType,
    LearningStrategy,
    learning_system
)

from .pattern_analyzer import (
    PatternAnalyzer,
    PatternType,
    PatternConfidence,
    IdentifiedPattern,
    pattern_analyzer
)

from .feedback_processor import (
    FeedbackProcessor,
    FeedbackCategory,
    SentimentLevel,
    FeedbackPriority,
    ProcessedFeedback,
    feedback_processor
)

from .learning_integration import (
    LearningIntegration,
    learning_integration
)

__all__ = [
    # Classes principais
    'ContinuousLearningSystem',
    'PatternAnalyzer', 
    'FeedbackProcessor',
    'LearningIntegration',
    
    # Enums
    'LearningEventType',
    'FeedbackType',
    'LearningStrategy',
    'PatternType',
    'PatternConfidence',
    'FeedbackCategory',
    'SentimentLevel',
    'FeedbackPriority',
    
    # Dataclasses
    'IdentifiedPattern',
    'ProcessedFeedback',
    
    # Instâncias globais
    'learning_system',
    'pattern_analyzer',
    'feedback_processor',
    'learning_integration'
]

# Versão do módulo
__version__ = "1.0.0"

# Informações do módulo
__author__ = "David Simer"
__description__ = "Sistema de Aprendizado Contínuo CWB Hub"
__status__ = "Production"