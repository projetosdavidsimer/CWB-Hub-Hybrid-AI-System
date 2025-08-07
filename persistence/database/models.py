#!/usr/bin/env python3
"""
CWB Hub Persistence System - Database Models
SQLAlchemy models para o sistema de persistência
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """Modelo de usuário/empresa"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    company_name = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")  # admin, user, viewer
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True))
    
    # Configurações
    settings = Column(JSON, default={})
    subscription_plan = Column(String(50), default="free")  # free, pro, enterprise
    
    # Relacionamentos
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index('idx_user_email_active', 'email', 'is_active'),
        Index('idx_user_company', 'company_name'),
        Index('idx_user_created', 'created_at'),
    )


class Project(Base):
    """Modelo de projeto"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(JSON, nullable=False)  # Lista de requisitos
    constraints = Column(JSON, default=[])  # Lista de restrições
    urgency = Column(String(20), default="medium")  # low, medium, high, critical
    budget = Column(String(100))
    status = Column(String(20), default="active")  # active, completed, archived
    
    # Metadados
    tags = Column(JSON, default=[])
    category = Column(String(100))
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relacionamentos
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="projects")
    sessions = relationship("Session", back_populates="project", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index('idx_project_owner_status', 'owner_id', 'status'),
        Index('idx_project_created', 'created_at'),
        Index('idx_project_urgency', 'urgency'),
        Index('idx_project_category', 'category'),
    )


class Session(Base):
    """Modelo de sessão de colaboração"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    
    # Dados da sessão
    request_text = Column(Text, nullable=False)
    response_text = Column(Text)
    confidence_score = Column(Integer, default=0)  # 0-100
    status = Column(String(20), default="processing")  # processing, completed, failed
    
    # Métricas
    agents_count = Column(Integer, default=0)
    collaborations_count = Column(Integer, default=0)
    iterations_count = Column(Integer, default=0)
    processing_time_ms = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relacionamentos
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user = relationship("User", back_populates="sessions")
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    project = relationship("Project", back_populates="sessions")
    
    collaborations = relationship("Collaboration", back_populates="session", cascade="all, delete-orphan")
    feedbacks = relationship("Feedback", back_populates="session", cascade="all, delete-orphan")
    
    # Índices
    __table_args__ = (
        Index('idx_session_user_project', 'user_id', 'project_id'),
        Index('idx_session_status', 'status'),
        Index('idx_session_created', 'created_at'),
        Index('idx_session_confidence', 'confidence_score'),
    )


class Agent(Base):
    """Modelo de agente especialista"""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(255), nullable=False)
    description = Column(Text)
    skills = Column(JSON, default=[])
    expertise_areas = Column(JSON, default=[])
    avatar = Column(String(10))
    
    # Estatísticas
    total_sessions = Column(Integer, default=0)
    total_collaborations = Column(Integer, default=0)
    average_confidence = Column(Integer, default=0)
    
    # Configurações
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relacionamentos
    collaborations = relationship("Collaboration", back_populates="agent", foreign_keys="[Collaboration.agent_id]")
    
    # Índices
    __table_args__ = (
        Index('idx_agent_active', 'is_active'),
        Index('idx_agent_role', 'role'),
    )


class Collaboration(Base):
    """Modelo de colaboração entre agentes"""
    __tablename__ = "collaborations"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Dados da colaboração
    collaboration_type = Column(String(50), nullable=False)  # peer_review, expertise_sharing, etc.
    context = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    confidence_score = Column(Integer, default=0)
    
    # Relacionamentos
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    session = relationship("Session", back_populates="collaborations")
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    agent = relationship("Agent", back_populates="collaborations", foreign_keys=[agent_id])
    
    # Colaboração com outro agente (opcional)
    collaborator_agent_id = Column(Integer, ForeignKey("agents.id"))
    collaborator_agent = relationship("Agent", foreign_keys=[collaborator_agent_id])
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Índices
    __table_args__ = (
        Index('idx_collaboration_session', 'session_id'),
        Index('idx_collaboration_agent', 'agent_id'),
        Index('idx_collaboration_type', 'collaboration_type'),
        Index('idx_collaboration_created', 'created_at'),
    )


class Feedback(Base):
    """Modelo de feedback/iteração"""
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Dados do feedback
    feedback_text = Column(Text, nullable=False)
    response_text = Column(Text)
    iteration_number = Column(Integer, default=1)
    confidence_improvement = Column(Integer, default=0)  # Melhoria na confiança
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True))
    
    # Relacionamentos
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    session = relationship("Session", back_populates="feedbacks")
    
    # Índices
    __table_args__ = (
        Index('idx_feedback_session', 'session_id'),
        Index('idx_feedback_iteration', 'iteration_number'),
        Index('idx_feedback_created', 'created_at'),
    )


class AuditLog(Base):
    """Modelo de log de auditoria"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Dados da ação
    action = Column(String(100), nullable=False)  # create, update, delete, login, etc.
    resource_type = Column(String(50), nullable=False)  # user, project, session, etc.
    resource_id = Column(String(100))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Detalhes
    details = Column(JSON, default={})
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relacionamentos
    user = relationship("User")
    
    # Índices
    __table_args__ = (
        Index('idx_audit_user_action', 'user_id', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
        Index('idx_audit_created', 'created_at'),
    )


class SystemMetric(Base):
    """Modelo de métricas do sistema"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(String(255), nullable=False)
    metric_type = Column(String(50), nullable=False)  # counter, gauge, histogram
    tags = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Índices
    __table_args__ = (
        Index('idx_metric_name_created', 'metric_name', 'created_at'),
        Index('idx_metric_type', 'metric_type'),
    )


# Função para criar todas as tabelas
def create_tables(engine):
    """Cria todas as tabelas no banco de dados"""
    Base.metadata.create_all(bind=engine)


# Função para popular dados iniciais
def populate_initial_data(engine):
    """Popula dados iniciais (agentes)"""
    from sqlalchemy.orm import sessionmaker
    
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    try:
        _populate_agents(session)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def _populate_agents(session):
    """Função auxiliar para popular agentes"""
    
    agents_data = [
        {
            "agent_id": "ana_beatriz_costa",
            "name": "Dra. Ana Beatriz Costa",
            "role": "Chief Technology Officer (CTO)",
            "description": "Visionária tecnológica que define estratégias e lidera inovação na CWB Hub",
            "skills": ["Liderança estratégica", "Arquitetura de Software", "Gestão de Pessoas", "Inovação Tecnológica"],
            "expertise_areas": ["Estratégia tecnológica", "Arquitetura empresarial", "Inovação e tendências"],
            "avatar": "👩‍💼"
        },
        {
            "agent_id": "carlos_eduardo_santos",
            "name": "Dr. Carlos Eduardo Santos",
            "role": "Arquiteto de Software Sênior",
            "description": "Especialista em arquitetura de sistemas que garante qualidade e escalabilidade técnica",
            "skills": ["Arquitetura de Sistemas", "Microsserviços", "Design Patterns", "Escalabilidade"],
            "expertise_areas": ["Arquitetura de software", "Sistemas distribuídos", "Microserviços"],
            "avatar": "👨‍💻"
        },
        {
            "agent_id": "sofia_oliveira",
            "name": "Sofia Oliveira",
            "role": "Engenheira Full Stack",
            "description": "Especialista em desenvolvimento completo que conecta frontend e backend",
            "skills": ["React/Vue.js", "Node.js/Python", "APIs REST", "Bancos de Dados"],
            "expertise_areas": ["Desenvolvimento web", "APIs", "Integração de sistemas"],
            "avatar": "👩‍💻"
        },
        {
            "agent_id": "gabriel_mendes",
            "name": "Gabriel Mendes",
            "role": "Engenheiro Mobile",
            "description": "Especialista em desenvolvimento mobile que cria experiências nativas excepcionais",
            "skills": ["iOS (Swift)", "Android (Kotlin)", "React Native", "Flutter"],
            "expertise_areas": ["Desenvolvimento mobile", "UX mobile", "Performance"],
            "avatar": "👨‍📱"
        },
        {
            "agent_id": "isabella_santos",
            "name": "Isabella Santos",
            "role": "Designer UX/UI Sênior",
            "description": "Especialista em experiência do usuário que cria interfaces intuitivas e atraentes",
            "skills": ["Pesquisa de Usuário", "Design Thinking", "Prototipagem", "Design de Interação"],
            "expertise_areas": ["User Experience", "User Interface", "Design thinking"],
            "avatar": "👩‍🎨"
        },
        {
            "agent_id": "lucas_pereira",
            "name": "Lucas Pereira",
            "role": "Engenheiro de QA",
            "description": "Especialista em qualidade que garante excelência através de testes e validações",
            "skills": ["Testes Automatizados", "Selenium", "Jest", "Cypress"],
            "expertise_areas": ["Qualidade de software", "Testes automatizados", "QA"],
            "avatar": "👨‍🔬"
        },
        {
            "agent_id": "mariana_rodrigues",
            "name": "Mariana Rodrigues",
            "role": "Engenheira DevOps",
            "description": "Especialista em infraestrutura que garante operações confiáveis e escaláveis",
            "skills": ["Docker", "Kubernetes", "AWS/Azure", "CI/CD"],
            "expertise_areas": ["DevOps", "Infraestrutura", "Cloud computing"],
            "avatar": "👩‍🔧"
        },
        {
            "agent_id": "pedro_henrique_almeida",
            "name": "Pedro Henrique Almeida",
            "role": "Agile Project Manager",
            "description": "Especialista em metodologias ágeis que coordena equipes e garante entregas de valor",
            "skills": ["Scrum", "Kanban", "Jira", "Confluence"],
            "expertise_areas": ["Metodologias ágeis", "Gestão de projetos", "Coordenação"],
            "avatar": "👨‍📊"
        }
    ]
    
    # Verificar se agentes já existem
    existing_agents = session.query(Agent).count()
    if existing_agents == 0:
        for agent_data in agents_data:
            agent = Agent(**agent_data)
            session.add(agent)
        
        session.commit()
        print(f"✅ {len(agents_data)} agentes criados com sucesso!")
    else:
        print(f"ℹ️  {existing_agents} agentes já existem no banco de dados")