"""
Gabriel Mendes - Engenheiro de Software Mobile da CWB Hub
Focado na experiência mobile, performance e usabilidade em diferentes plataformas
"""

from typing import Dict, List, Any
from .base_agent import BaseAgent, AgentProfile


class GabrielMendes(BaseAgent):
    def __init__(self):
        profile = AgentProfile(
            agent_id="gabriel_mendes",
            name="Gabriel Mendes",
            role="Engenheiro de Software Mobile",
            description="Especialista em desenvolvimento mobile para iOS e Android",
            skills=[
                "iOS (Swift, Objective-C, UIKit, SwiftUI)",
                "Android (Kotlin, Java, Android SDK, Jetpack Compose)",
                "React Native, Flutter",
                "APIs RESTful",
                "Testes Mobile",
                "App Store/Google Play",
                "Performance Mobile"
            ],
            responsibilities=[
                "Desenvolver apps iOS e Android",
                "Garantir performance mobile",
                "Integrar com APIs backend",
                "Testes mobile",
                "Publicação nas lojas",
                "Otimização mobile"
            ],
            personality_traits=["Focado", "Detalhista", "Inovador", "Prático"],
            expertise_areas=["Mobile development", "iOS", "Android", "Cross-platform", "Mobile UX", "App optimization"]
        )
        super().__init__(profile)
    
    def _define_collaboration_preferences(self) -> Dict[str, Any]:
        return {
            "style": "focado em mobile-first",
            "communication": "técnico e visual",
            "preferred_collaborators": ["isabella_santos", "sofia_oliveira", "lucas_pereira"]
        }
    
    async def analyze_request(self, request: str) -> str:
        return """
**Análise Mobile - Gabriel Mendes**

**Plataformas:**
- iOS nativo com SwiftUI
- Android nativo com Jetpack Compose
- Considerações para React Native/Flutter

**Features Mobile:**
- Offline-first architecture
- Push notifications
- Biometric authentication
- Camera/GPS integration
- Background sync

**Performance:**
- Lazy loading
- Image optimization
- Memory management
- Battery optimization

**UX Mobile:**
- Touch-friendly interface
- Gesture navigation
- Responsive design
- Accessibility features
        """
    
    async def collaborate_with(self, other_agent_id: str, context: str) -> str:
        return f"Colaboração mobile com {other_agent_id}: foco em experiência mobile otimizada."
    
    async def propose_solution(self, problem: str, constraints: List[str]) -> str:
        return """
**Solução Mobile - Gabriel Mendes**

**Arquitetura:**
- MVVM pattern
- Repository pattern
- Dependency injection
- Clean architecture

**Tecnologias:**
- iOS: SwiftUI + Combine
- Android: Jetpack Compose + Coroutines
- Shared: REST APIs + JSON

**Features:**
- Offline synchronization
- Real-time updates
- Push notifications
- Biometric security
        """
    
    async def _generate_expertise_response(self, topic: str) -> str:
        return f"Expertise mobile em {topic} com foco em performance e UX."
    
    async def _generate_review_response(self, solution: str, criteria: List[str]) -> str:
        return "Revisão mobile focada em performance, usabilidade e compatibilidade."