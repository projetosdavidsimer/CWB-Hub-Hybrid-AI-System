"""
CWB Hub Hybrid AI System
Sistema de IA híbrida que incorpora 8 profissionais sênior
"""

from .core.hybrid_ai_orchestrator import HybridAIOrchestrator
from .agents.base_agent import BaseAgent, AgentProfile
from .communication.collaboration_framework import CollaborationFramework
from .utils.requirement_analyzer import RequirementAnalyzer
from .utils.response_synthesizer import ResponseSynthesizer

__version__ = "1.0.0"
__author__ = "CWB Hub Team"

__all__ = [
    "HybridAIOrchestrator",
    "BaseAgent",
    "AgentProfile",
    "CollaborationFramework",
    "RequirementAnalyzer",
    "ResponseSynthesizer"
]