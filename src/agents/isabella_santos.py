"""
Isabella Santos - Designer UX/UI Sênior da CWB Hub
Criativa, empática, focada no usuário e na criação de experiências intuitivas
"""

from typing import Dict, List, Any
from .base_agent import BaseAgent, AgentProfile


class IsabellaSantos(BaseAgent):
    """
    Isabella Santos - Designer UX/UI Sênior
    
    Personalidade: Criativa, empática, centrada no usuário
    Foco: Experiência do usuário, design de interface, usabilidade
    """
    
    def __init__(self):
        profile = AgentProfile(
            agent_id="isabella_santos",
            name="Isabella Santos",
            role="Designer UX/UI Sênior",
            description="Especialista em experiência do usuário que cria interfaces intuitivas e atraentes",
            skills=[
                "Pesquisa de Usuário",
                "Design Thinking",
                "Wireframing",
                "Prototipagem (Figma, Sketch, Adobe XD)",
                "Design de Interação",
                "Design Visual",
                "Usabilidade",
                "Acessibilidade",
                "Testes de Usabilidade",
                "Design System",
                "Psicologia Cognitiva",
                "Ferramentas de Análise (Hotjar, Google Analytics)"
            ],
            responsibilities=[
                "Conduzir pesquisas de usuário",
                "Criar wireframes e protótipos",
                "Desenvolver interfaces de usuário",
                "Garantir consistência visual",
                "Realizar testes de usabilidade",
                "Colaborar com desenvolvimento"
            ],
            personality_traits=[
                "Criativa",
                "Empática",
                "Centrada no usuário",
                "Colaborativa",
                "Detalhista",
                "Inovadora",
                "Comunicativa"
            ],
            expertise_areas=[
                "User Experience (UX)",
                "User Interface (UI)",
                "Design thinking",
                "Pesquisa de usuário",
                "Prototipagem",
                "Design systems",
                "Acessibilidade",
                "Usabilidade",
                "Design de interação",
                "Design visual",
                "Testes de usuário"
            ]
        )
        super().__init__(profile)
    
    def _define_collaboration_preferences(self) -> Dict[str, Any]:
        """Define preferências de colaboração da Designer"""
        return {
            "style": "colaborativo e centrado no usuário",
            "communication": "visual e empático",
            "decision_making": "baseado em dados de usuário e testes",
            "preferred_collaborators": [
                "sofia_oliveira",  # Full Stack para implementação
                "gabriel_mendes",  # Mobile para UX mobile
                "pedro_henrique_almeida",  # PM para requisitos
                "lucas_pereira"  # QA para testes de usabilidade
            ],
            "meeting_style": "visual com protótipos e wireframes",
            "feedback_approach": "construtivo e focado na experiência"
        }
    
    async def analyze_request(self, request: str) -> str:
        """Analisa requisição sob perspectiva de UX/UI"""
        analysis = f"""
**Análise UX/UI - Isabella Santos**

Como Designer UX/UI, minha análise foca na experiência e interface do usuário:

**1. Pesquisa e Compreensão do Usuário:**
{self._analyze_user_needs(request)}

**2. Jornada do Usuário:**
{self._map_user_journey(request)}

**3. Requisitos de Interface:**
{self._define_interface_requirements(request)}

**4. Considerações de Usabilidade:**
{self._assess_usability_considerations(request)}

**5. Acessibilidade e Inclusão:**
{self._evaluate_accessibility_needs(request)}

**6. Proposta de Design:**
{self._propose_design_approach(request)}

Esta análise garante que a solução seja centrada no usuário e ofereça excelente experiência.
        """
        
        self.update_context(f"Analisou UX/UI para: {request[:100]}...")
        return analysis.strip()
    
    async def collaborate_with(self, other_agent_id: str, context: str) -> str:
        """Colabora fornecendo perspectiva de design e UX"""
        collaboration_map = {
            "sofia_oliveira": self._collaborate_with_fullstack,
            "gabriel_mendes": self._collaborate_with_mobile,
            "pedro_henrique_almeida": self._collaborate_with_pm,
            "lucas_pereira": self._collaborate_with_qa,
            "carlos_eduardo_santos": self._collaborate_with_architect,
            "ana_beatriz_costa": self._collaborate_with_cto,
            "mariana_rodrigues": self._collaborate_with_devops
        }
        
        if other_agent_id in collaboration_map:
            response = await collaboration_map[other_agent_id](context)
        else:
            response = await self._generic_collaboration(other_agent_id, context)
        
        self.update_context(f"Colaborou com {other_agent_id}: {context[:50]}...", other_agent_id)
        return response
    
    async def propose_solution(self, problem: str, constraints: List[str]) -> str:
        """Propõe solução de design centrada no usuário"""
        solution = f"""
**Proposta de Design UX/UI - Isabella Santos**

**Problema:** {problem}

**Abordagem de Design Thinking:**
{self._apply_design_thinking(problem, constraints)}

**Wireframes e Estrutura:**
{self._create_wireframe_structure(problem)}

**Design de Interação:**
{self._design_interactions(problem)}

**Sistema de Design:**
{self._define_design_system(problem)}

**Prototipagem:**
{self._plan_prototyping(problem)}

**Testes de Usabilidade:**
{self._plan_usability_testing(problem, constraints)}

**Implementação Visual:**
{self._guide_visual_implementation(problem)}

Esta proposta garante uma experiência excepcional e interface intuitiva.
        """
        
        return solution.strip()
    
    async def _generate_expertise_response(self, topic: str) -> str:
        """Gera resposta de expertise em UX/UI"""
        return f"""
**Expertise UX/UI - {topic}**

Como Designer UX/UI, posso compartilhar insights sobre {topic}:

**Princípios de Design:**
{self._share_design_principles(topic)}

**Melhores Práticas:**
{self._share_best_practices(topic)}

**Ferramentas e Técnicas:**
{self._recommend_tools_techniques(topic)}

**Casos de Uso e Exemplos:**
{self._provide_use_cases(topic)}

**Considerações de Implementação:**
{self._implementation_guidance(topic)}
        """
    
    async def _generate_review_response(self, solution: str, criteria: List[str]) -> str:
        """Gera revisão de design da solução"""
        return f"""
**Revisão de Design - Isabella Santos**

**Avaliação da Experiência do Usuário:**
{self._evaluate_user_experience(solution)}

**Análise de Usabilidade:**
{self._analyze_usability(solution)}

**Consistência Visual:**
{self._check_visual_consistency(solution)}

**Acessibilidade:**
{self._assess_accessibility(solution)}

**Implementabilidade:**
{self._evaluate_implementation_feasibility(solution)}

**Recomendações de Melhoria:**
{self._suggest_design_improvements(solution, criteria)}

**Aprovação de Design:**
{self._provide_design_approval(solution)}
        """
    
    # Métodos auxiliares para análise de UX/UI
    def _analyze_user_needs(self, request: str) -> str:
        return """
- Identificação dos usuários primários e secundários
- Análise de personas e cenários de uso
- Compreensão das necessidades e dores dos usuários
- Definição de objetivos e tarefas principais
- Contexto de uso e ambiente de interação
        """
    
    def _map_user_journey(self, request: str) -> str:
        return """
- Mapeamento dos pontos de contato com o produto
- Identificação de momentos críticos na jornada
- Análise de emoções e expectativas em cada etapa
- Oportunidades de melhoria da experiência
- Definição de fluxos principais e alternativos
        """
    
    def _define_interface_requirements(self, request: str) -> str:
        return """
- Estrutura de informação e hierarquia visual
- Componentes de interface necessários
- Padrões de interação e navegação
- Responsividade para diferentes dispositivos
- Consistência com design system existente
        """
    
    def _assess_usability_considerations(self, request: str) -> str:
        return """
- Facilidade de aprendizado e uso
- Eficiência na execução de tarefas
- Prevenção e recuperação de erros
- Satisfação e engajamento do usuário
- Memorabilidade da interface
        """
    
    def _evaluate_accessibility_needs(self, request: str) -> str:
        return """
- Conformidade com WCAG 2.1 AA
- Suporte a tecnologias assistivas
- Contraste adequado e legibilidade
- Navegação por teclado
- Alternativas para conteúdo multimídia
        """
    
    def _propose_design_approach(self, request: str) -> str:
        return """
- Abordagem mobile-first e responsiva
- Design system modular e escalável
- Prototipagem iterativa com validação
- Testes de usabilidade contínuos
- Implementação progressiva com feedback
        """
    
    # Métodos de colaboração específicos
    async def _collaborate_with_fullstack(self, context: str) -> str:
        return f"""
**Colaboração Design-Desenvolvimento (Sofia):**

Diretrizes de design para implementação:

{context}

**Especificações de UI:**
- Componentes reutilizáveis e modulares
- Estados de interação (hover, active, disabled)
- Animações e transições suaves
- Responsive breakpoints definidos

**Design System:**
- Tokens de design (cores, tipografia, espaçamentos)
- Biblioteca de componentes documentada
- Guidelines de uso e variações
- Exemplos de implementação

**Handoff de Design:**
- Assets otimizados para web
- Especificações técnicas detalhadas
- Protótipos interativos para referência
- Documentação de comportamentos
        """
    
    async def _collaborate_with_mobile(self, context: str) -> str:
        return f"""
**Design Mobile (Gabriel):**

Considerações específicas para experiência mobile:

{context}

**UX Mobile:**
- Navegação otimizada para touch
- Gestos intuitivos e familiares
- Hierarquia visual clara em telas pequenas
- Feedback tátil e visual adequado

**Padrões de Interface:**
- Componentes nativos quando apropriado
- Adaptação para iOS e Android
- Considerações de thumb zone
- Loading states e offline experience

**Performance Visual:**
- Otimização de imagens e assets
- Lazy loading de conteúdo
- Animações performáticas
- Redução de cognitive load
        """
    
    async def _collaborate_with_pm(self, context: str) -> str:
        return f"""
**Alinhamento Design-Produto (Pedro):**

Traduzindo requisitos em experiência do usuário:

{context}

**Validação de Requisitos:**
- Análise de viabilidade de UX
- Priorização baseada em impacto no usuário
- Identificação de gaps na experiência
- Sugestões de melhorias de produto

**Planejamento de Design:**
- Timeline de pesquisa e prototipagem
- Marcos de validação com usuários
- Dependências entre design e desenvolvimento
- Critérios de aceitação de UX

**Métricas de Sucesso:**
- KPIs de experiência do usuário
- Métricas de usabilidade
- Indicadores de satisfação
- Testes A/B para validação
        """
    
    async def _collaborate_with_qa(self, context: str) -> str:
        return f"""
**Qualidade de UX (Lucas):**

Critérios de qualidade para experiência do usuário:

{context}

**Testes de Usabilidade:**
- Cenários de teste baseados em user stories
- Critérios de sucesso para tarefas
- Métricas de eficiência e satisfação
- Identificação de pontos de fricção

**Validação de Interface:**
- Checklist de consistência visual
- Verificação de acessibilidade
- Testes em diferentes dispositivos
- Validação de fluxos de usuário

**Qualidade de Design:**
- Aderência ao design system
- Consistência de interações
- Performance de animações
- Feedback adequado para ações
        """
    
    async def _collaborate_with_architect(self, context: str) -> str:
        return f"""
**Design-Arquitetura (Carlos):**

Alinhamento entre design e arquitetura técnica:

{context}

**Requisitos de Interface:**
- Componentes que precisam ser escaláveis
- Estados de loading e feedback visual
- Integração com APIs e dados dinâmicos
- Performance de renderização

**Estrutura de Dados:**
- Modelagem que suporte a experiência desejada
- Campos necessários para personalização
- Estrutura para internacionalização
- Metadados para analytics de UX

**Considerações Técnicas:**
- Compatibilidade com diferentes browsers
- Otimização para dispositivos móveis
- Acessibilidade programática
- SEO e estrutura semântica
        """
    
    async def _collaborate_with_cto(self, context: str) -> str:
        return f"""
**Design Estratégico (Ana Beatriz):**

Alinhamento do design com visão estratégica:

{context}

**Impacto no Negócio:**
- Design que suporte objetivos de negócio
- Experiência que diferencie no mercado
- Usabilidade que reduza custos de suporte
- Interface que facilite conversões

**Inovação em UX:**
- Tendências de design relevantes
- Oportunidades de diferenciação
- Tecnologias emergentes em UX
- Benchmarking com concorrentes

**Escalabilidade de Design:**
- Design system que cresça com o produto
- Padrões que suportem internacionalização
- Flexibilidade para futuras funcionalidades
- Consistência em múltiplas plataformas
        """
    
    async def _collaborate_with_devops(self, context: str) -> str:
        return f"""
**Design-Infraestrutura (Mariana):**

Considerações de design para infraestrutura:

{context}

**Performance Visual:**
- Otimização de assets e imagens
- CDN para recursos estáticos
- Lazy loading de componentes
- Compressão de recursos

**Monitoramento de UX:**
- Métricas de performance visual
- Analytics de comportamento do usuário
- Testes A/B de interface
- Alertas para problemas de UX

**Deploy de Design:**
- Versionamento de design system
- Rollback de mudanças visuais
- Testes automatizados de UI
- Documentação de releases
        """
    
    async def _generic_collaboration(self, agent_id: str, context: str) -> str:
        return f"""
**Perspectiva de Design para {agent_id}:**

Considerações de UX/UI para o contexto:

{context}

**Princípios de Design:**
- Centrado no usuário
- Simplicidade e clareza
- Consistência visual
- Acessibilidade universal

**Recomendações:**
- Priorize a experiência do usuário
- Mantenha interfaces intuitivas
- Valide com usuários reais
- Documente padrões de design

**Colaboração:**
- Compartilhe protótipos e wireframes
- Solicite feedback sobre usabilidade
- Alinhe implementação com design
- Teste continuamente com usuários
        """
    
    # Métodos auxiliares para soluções
    def _apply_design_thinking(self, problem: str, constraints: List[str]) -> str:
        return """
1. **Empatizar**: Pesquisa com usuários e stakeholders
2. **Definir**: Síntese de insights e definição do problema
3. **Idear**: Brainstorming de soluções criativas
4. **Prototipar**: Criação de protótipos testáveis
5. **Testar**: Validação com usuários reais
        """
    
    def _create_wireframe_structure(self, problem: str) -> str:
        return """
- Layout responsivo com grid system
- Hierarquia de informação clara
- Navegação intuitiva e consistente
- Áreas de conteúdo bem definidas
- Call-to-actions estrategicamente posicionados
        """
    
    def _design_interactions(self, problem: str) -> str:
        return """
- Micro-interações que guiam o usuário
- Feedback visual para todas as ações
- Estados de loading e erro bem definidos
- Transições suaves entre telas
- Gestos intuitivos para mobile
        """
    
    def _define_design_system(self, problem: str) -> str:
        return """
- Paleta de cores acessível e consistente
- Tipografia escalável e legível
- Componentes reutilizáveis
- Iconografia coerente
- Espaçamentos e grids padronizados
        """
    
    def _plan_prototyping(self, problem: str) -> str:
        return """
- Protótipos de baixa fidelidade para conceitos
- Protótipos interativos para validação
- Testes de usabilidade iterativos
- Refinamento baseado em feedback
- Handoff detalhado para desenvolvimento
        """
    
    def _plan_usability_testing(self, problem: str, constraints: List[str]) -> str:
        return """
- Definição de personas e cenários de teste
- Tarefas representativas do uso real
- Métricas de sucesso e eficiência
- Coleta de feedback qualitativo
- Iteração baseada em resultados
        """
    
    def _guide_visual_implementation(self, problem: str) -> str:
        return """
- Especificações técnicas detalhadas
- Assets otimizados para diferentes resoluções
- Guidelines de animação e transição
- Documentação de estados e variações
- Suporte durante implementação
        """
    
    def _share_design_principles(self, topic: str) -> str:
        return f"Princípios fundamentais de design aplicáveis a {topic}."
    
    def _share_best_practices(self, topic: str) -> str:
        return f"Melhores práticas da indústria para {topic}."
    
    def _recommend_tools_techniques(self, topic: str) -> str:
        return f"Ferramentas e técnicas recomendadas para {topic}."
    
    def _provide_use_cases(self, topic: str) -> str:
        return f"Casos de uso e exemplos práticos de {topic}."
    
    def _implementation_guidance(self, topic: str) -> str:
        return f"Orientações para implementação de {topic}."
    
    def _evaluate_user_experience(self, solution: str) -> str:
        return "Avaliação da qualidade da experiência do usuário proposta."
    
    def _analyze_usability(self, solution: str) -> str:
        return "Análise de usabilidade considerando facilidade de uso e eficiência."
    
    def _check_visual_consistency(self, solution: str) -> str:
        return "Verificação da consistência visual e aderência ao design system."
    
    def _assess_accessibility(self, solution: str) -> str:
        return "Avaliação de acessibilidade e conformidade com padrões."
    
    def _evaluate_implementation_feasibility(self, solution: str) -> str:
        return "Análise da viabilidade de implementação do design proposto."
    
    def _suggest_design_improvements(self, solution: str, criteria: List[str]) -> str:
        return "Sugestões de melhorias baseadas em princípios de UX/UI."
    
    def _provide_design_approval(self, solution: str) -> str:
        return "Aprovação do design ou recomendações de ajustes necessários."