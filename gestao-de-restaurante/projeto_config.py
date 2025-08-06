"""
Configuração específica do projeto Gestão de Restaurante
Criado por: David Simer
"""

# Configurações do projeto
PROJECT_CONFIG = {
    "name": "Sistema de Gestão de Restaurante",
    "version": "1.0.0",
    "creator": "David Simer",
    "description": "Sistema completo para gestão de restaurantes",
    
    # Configurações da equipe CWB Hub
    "cwb_hub": {
        "agents_priority": [
            "ana_beatriz_costa",      # CTO - Estratégia
            "carlos_eduardo_santos",  # Arquiteto - Arquitetura
            "sofia_oliveira",         # Full Stack - Desenvolvimento
            "pedro_henrique_almeida", # PM - Gestão
            "isabella_santos",        # UX/UI - Interface
            "lucas_pereira",          # QA - Testes
            "mariana_rodrigues",      # DevOps - Infraestrutura
            "gabriel_mendes"          # Mobile - App móvel
        ],
        
        "focus_areas": [
            "Gestão de pedidos",
            "Controle de estoque", 
            "Interface de usuário",
            "Relatórios financeiros",
            "App mobile para garçons",
            "Sistema de delivery",
            "Integração de pagamentos"
        ]
    },
    
    # Templates de solicitação
    "templates": {
        "business_plan": """
        PROJETO: {project_name}
        CRIADO POR: David Simer
        
        PLANO DE NEGÓCIO:
        {business_plan}
        
        SOLICITAÇÃO PARA EQUIPE CWB HUB:
        Analisem este plano e forneçam:
        1. Análise técnica completa
        2. Arquitetura recomendada
        3. Tecnologias sugeridas
        4. Plano de desenvolvimento
        5. Cronograma detalhado
        """,
        
        "feature_request": """
        PROJETO: {project_name}
        FUNCIONALIDADE: {feature_name}
        
        DESCRIÇÃO:
        {feature_description}
        
        SOLICITAÇÃO:
        Implementem esta funcionalidade considerando:
        - Integração com sistema existente
        - Melhor experiência do usuário
        - Performance e escalabilidade
        - Testes necessários
        """,
        
        "iteration_feedback": """
        PROJETO: {project_name}
        FEEDBACK DO CLIENTE:
        {feedback}
        
        SOLICITAÇÃO:
        Refinem a solução considerando este feedback e mantenham
        a qualidade técnica e usabilidade.
        """
    }
}

# Função para obter configuração
def get_config():
    return PROJECT_CONFIG

# Função para obter template
def get_template(template_name, **kwargs):
    template = PROJECT_CONFIG["templates"].get(template_name, "")
    return template.format(**kwargs)