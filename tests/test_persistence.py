#!/usr/bin/env python3
"""
Testes para o Sistema de Persistência CWB Hub
Melhoria #5 - Testes Automatizados Completos
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório persistence ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'persistence'))

from database.models import (
    Base, User, Project, Session, Agent, Collaboration, 
    Feedback, AuditLog, SystemMetric, create_tables, populate_initial_data
)
from database.connection import (
    test_connection, test_async_connection, health_check,
    get_connection_info, get_db_session, get_async_db_session
)


class TestDatabaseModels:
    """Testes para os modelos do banco de dados"""
    
    @pytest.fixture
    def engine(self):
        """Fixture para engine de teste em memória"""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        return engine
    
    @pytest.fixture
    def session(self, engine):
        """Fixture para sessão de teste"""
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_user_model_creation(self, session):
        """Testa criação de modelo User"""
        user = User(
            email="test@example.com",
            company_name="Test Company",
            full_name="Test User",
            hashed_password="hashed_password_123",
            role="user"
        )
        
        session.add(user)
        session.commit()
        
        assert user.id is not None
        assert user.uuid is not None
        assert user.email == "test@example.com"
        assert user.company_name == "Test Company"
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_project_model_creation(self, session):
        """Testa criação de modelo Project"""
        # Primeiro criar um usuário
        user = User(
            email="owner@example.com",
            company_name="Owner Company",
            full_name="Project Owner",
            hashed_password="hashed_password_123"
        )
        session.add(user)
        session.commit()
        
        # Criar projeto
        project = Project(
            title="Test Project",
            description="Test project description",
            requirements=["Requirement 1", "Requirement 2"],
            constraints=["Constraint 1"],
            urgency="high",
            owner_id=user.id
        )
        
        session.add(project)
        session.commit()
        
        assert project.id is not None
        assert project.uuid is not None
        assert project.title == "Test Project"
        assert project.urgency == "high"
        assert project.owner_id == user.id
        assert project.status == "active"
        assert project.created_at is not None
    
    def test_agent_model_creation(self, session):
        """Testa criação de modelo Agent"""
        agent = Agent(
            agent_id="test_agent",
            name="Test Agent",
            role="Test Role",
            description="Test agent description",
            skills=["Skill 1", "Skill 2"],
            expertise_areas=["Area 1", "Area 2"],
            avatar="🤖"
        )
        
        session.add(agent)
        session.commit()
        
        assert agent.id is not None
        assert agent.agent_id == "test_agent"
        assert agent.name == "Test Agent"
        assert agent.role == "Test Role"
        assert agent.skills == ["Skill 1", "Skill 2"]
        assert agent.expertise_areas == ["Area 1", "Area 2"]
        assert agent.is_active is True
        assert agent.created_at is not None
    
    def test_session_model_creation(self, session):
        """Testa criação de modelo Session"""
        # Criar usuário e projeto primeiro
        user = User(
            email="session_user@example.com",
            company_name="Session Company",
            full_name="Session User",
            hashed_password="hashed_password_123"
        )
        session.add(user)
        session.commit()
        
        project = Project(
            title="Session Project",
            description="Session project description",
            requirements=["Requirement"],
            owner_id=user.id
        )
        session.add(project)
        session.commit()
        
        # Criar sessão
        cwb_session = Session(
            session_id="test_session_123",
            request_text="Test request",
            response_text="Test response",
            confidence_score=85,
            user_id=user.id,
            project_id=project.id
        )
        
        session.add(cwb_session)
        session.commit()
        
        assert cwb_session.id is not None
        assert cwb_session.session_id == "test_session_123"
        assert cwb_session.confidence_score == 85
        assert cwb_session.status == "processing"
        assert cwb_session.created_at is not None
    
    def test_collaboration_model_creation(self, session):
        """Testa criação de modelo Collaboration"""
        # Criar dependências
        user = User(
            email="collab_user@example.com",
            company_name="Collab Company",
            full_name="Collab User",
            hashed_password="hashed_password_123"
        )
        session.add(user)
        session.commit()
        
        project = Project(
            title="Collab Project",
            description="Collab project description",
            requirements=["Requirement"],
            owner_id=user.id
        )
        session.add(project)
        session.commit()
        
        cwb_session = Session(
            session_id="collab_session_123",
            request_text="Collab request",
            user_id=user.id,
            project_id=project.id
        )
        session.add(cwb_session)
        session.commit()
        
        agent = Agent(
            agent_id="collab_agent",
            name="Collab Agent",
            role="Collab Role"
        )
        session.add(agent)
        session.commit()
        
        # Criar colaboração
        collaboration = Collaboration(
            collaboration_type="peer_review",
            context="Test collaboration context",
            response="Test collaboration response",
            confidence_score=90,
            session_id=cwb_session.id,
            agent_id=agent.id
        )
        
        session.add(collaboration)
        session.commit()
        
        assert collaboration.id is not None
        assert collaboration.collaboration_type == "peer_review"
        assert collaboration.confidence_score == 90
        assert collaboration.session_id == cwb_session.id
        assert collaboration.agent_id == agent.id
        assert collaboration.created_at is not None
    
    def test_audit_log_model_creation(self, session):
        """Testa criação de modelo AuditLog"""
        user = User(
            email="audit_user@example.com",
            company_name="Audit Company",
            full_name="Audit User",
            hashed_password="hashed_password_123"
        )
        session.add(user)
        session.commit()
        
        audit_log = AuditLog(
            action="create",
            resource_type="project",
            resource_id="123",
            user_id=user.id,
            details={"field": "value"},
            ip_address="192.168.1.1"
        )
        
        session.add(audit_log)
        session.commit()
        
        assert audit_log.id is not None
        assert audit_log.action == "create"
        assert audit_log.resource_type == "project"
        assert audit_log.details == {"field": "value"}
        assert audit_log.created_at is not None
    
    def test_system_metric_model_creation(self, session):
        """Testa criação de modelo SystemMetric"""
        metric = SystemMetric(
            metric_name="response_time",
            metric_value="150ms",
            metric_type="gauge",
            tags={"service": "api", "endpoint": "/analyze"}
        )
        
        session.add(metric)
        session.commit()
        
        assert metric.id is not None
        assert metric.metric_name == "response_time"
        assert metric.metric_value == "150ms"
        assert metric.metric_type == "gauge"
        assert metric.tags == {"service": "api", "endpoint": "/analyze"}
        assert metric.created_at is not None


class TestDatabaseConnection:
    """Testes para conexão com banco de dados"""
    
    def test_get_connection_info(self):
        """Testa obtenção de informações de conexão"""
        info = get_connection_info()
        
        assert isinstance(info, dict)
        assert "host" in info
        assert "port" in info
        assert "database" in info
        assert "username" in info
        assert "pool_size" in info
        assert "max_overflow" in info
        assert "engine_url" in info
        assert "async_engine_url" in info
    
    def test_connection_info_security(self):
        """Testa se informações sensíveis estão mascaradas"""
        info = get_connection_info()
        
        # Senha deve estar mascarada
        assert "***" in info["engine_url"]
        assert "***" in info["async_engine_url"]
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Testa conexão com banco de dados"""
        # Este teste só funciona se o PostgreSQL estiver rodando
        try:
            result = test_connection()
            assert isinstance(result, bool)
            
            if result:  # Se conexão funcionou
                async_result = await test_async_connection()
                assert isinstance(async_result, bool)
        except Exception:
            # Se não conseguir conectar, pular teste
            pytest.skip("PostgreSQL não disponível para teste")
    
    def test_health_check_structure(self):
        """Testa estrutura do health check"""
        try:
            health = health_check()
            
            assert isinstance(health, dict)
            assert "status" in health
            
            if health["status"] == "healthy":
                assert "database_version" in health
                assert "current_database" in health
                assert "current_user" in health
                assert "pool_statistics" in health
                assert "connection_info" in health
            else:
                assert "error" in health
                
        except Exception:
            # Se não conseguir conectar, pular teste
            pytest.skip("PostgreSQL não disponível para teste")


class TestDatabaseOperations:
    """Testes para operações do banco de dados"""
    
    @pytest.fixture
    def engine(self):
        """Fixture para engine de teste"""
        engine = create_engine("sqlite:///:memory:", echo=False)
        create_tables(engine)
        return engine
    
    def test_create_tables(self, engine):
        """Testa criação de tabelas"""
        # Verificar se tabelas foram criadas
        inspector = engine.dialect.get_table_names(engine.connect())
        
        expected_tables = [
            "users", "projects", "sessions", "agents", 
            "collaborations", "feedbacks", "audit_logs", "system_metrics"
        ]
        
        for table in expected_tables:
            assert table in inspector or table.lower() in inspector
    
    def test_populate_initial_data(self, engine):
        """Testa população de dados iniciais"""
        # Executar população de dados
        populate_initial_data(engine)
        
        # Verificar se agentes foram criados
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            agents = session.query(Agent).all()
            assert len(agents) == 8  # 8 agentes especialistas
            
            # Verificar alguns agentes específicos
            agent_ids = [agent.agent_id for agent in agents]
            assert "ana_beatriz_costa" in agent_ids
            assert "carlos_eduardo_santos" in agent_ids
            assert "sofia_oliveira" in agent_ids
            assert "gabriel_mendes" in agent_ids
            
        finally:
            session.close()
    
    def test_populate_initial_data_idempotent(self, engine):
        """Testa se população de dados é idempotente"""
        # Executar duas vezes
        populate_initial_data(engine)
        populate_initial_data(engine)
        
        # Verificar se ainda há apenas 8 agentes
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            agents = session.query(Agent).all()
            assert len(agents) == 8  # Não deve duplicar
            
        finally:
            session.close()


class TestDatabaseRelationships:
    """Testes para relacionamentos entre modelos"""
    
    @pytest.fixture
    def engine(self):
        """Fixture para engine de teste"""
        engine = create_engine("sqlite:///:memory:", echo=False)
        create_tables(engine)
        return engine
    
    @pytest.fixture
    def session(self, engine):
        """Fixture para sessão de teste"""
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_user_project_relationship(self, session):
        """Testa relacionamento User -> Project"""
        user = User(
            email="rel_user@example.com",
            company_name="Rel Company",
            full_name="Rel User",
            hashed_password="hashed_password_123"
        )
        session.add(user)
        session.commit()
        
        project1 = Project(
            title="Project 1",
            description="Description 1",
            requirements=["Req 1"],
            owner_id=user.id
        )
        
        project2 = Project(
            title="Project 2",
            description="Description 2",
            requirements=["Req 2"],
            owner_id=user.id
        )
        
        session.add_all([project1, project2])
        session.commit()
        
        # Testar relacionamento
        assert len(user.projects) == 2
        assert project1 in user.projects
        assert project2 in user.projects
        assert project1.owner == user
        assert project2.owner == user
    
    def test_session_collaboration_relationship(self, session):
        """Testa relacionamento Session -> Collaboration"""
        # Criar dependências
        user = User(
            email="session_rel@example.com",
            company_name="Session Company",
            full_name="Session User",
            hashed_password="hashed_password_123"
        )
        session.add(user)
        session.commit()
        
        project = Project(
            title="Session Project",
            description="Session description",
            requirements=["Req"],
            owner_id=user.id
        )
        session.add(project)
        session.commit()
        
        cwb_session = Session(
            session_id="rel_session_123",
            request_text="Rel request",
            user_id=user.id,
            project_id=project.id
        )
        session.add(cwb_session)
        session.commit()
        
        agent = Agent(
            agent_id="rel_agent",
            name="Rel Agent",
            role="Rel Role"
        )
        session.add(agent)
        session.commit()
        
        # Criar colaborações
        collab1 = Collaboration(
            collaboration_type="peer_review",
            context="Context 1",
            response="Response 1",
            session_id=cwb_session.id,
            agent_id=agent.id
        )
        
        collab2 = Collaboration(
            collaboration_type="expertise_sharing",
            context="Context 2",
            response="Response 2",
            session_id=cwb_session.id,
            agent_id=agent.id
        )
        
        session.add_all([collab1, collab2])
        session.commit()
        
        # Testar relacionamentos
        assert len(cwb_session.collaborations) == 2
        assert collab1 in cwb_session.collaborations
        assert collab2 in cwb_session.collaborations
        assert collab1.session == cwb_session
        assert collab2.session == cwb_session


class TestDatabasePerformance:
    """Testes de performance do banco de dados"""
    
    @pytest.fixture
    def engine(self):
        """Fixture para engine de teste"""
        engine = create_engine("sqlite:///:memory:", echo=False)
        create_tables(engine)
        return engine
    
    def test_bulk_insert_performance(self, engine):
        """Testa performance de inserção em lote"""
        import time
        
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            start_time = time.time()
            
            # Inserir 100 métricas de sistema
            metrics = []
            for i in range(100):
                metric = SystemMetric(
                    metric_name=f"test_metric_{i}",
                    metric_value=f"value_{i}",
                    metric_type="counter"
                )
                metrics.append(metric)
            
            session.add_all(metrics)
            session.commit()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Deve inserir 100 registros em menos de 1 segundo
            assert duration < 1.0
            
            # Verificar se todos foram inseridos
            count = session.query(SystemMetric).count()
            assert count == 100
            
        finally:
            session.close()
    
    def test_query_performance(self, engine):
        """Testa performance de consultas"""
        import time
        
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        try:
            # Criar dados de teste
            user = User(
                email="perf_user@example.com",
                company_name="Perf Company",
                full_name="Perf User",
                hashed_password="hashed_password_123"
            )
            session.add(user)
            session.commit()
            
            # Criar 50 projetos
            projects = []
            for i in range(50):
                project = Project(
                    title=f"Project {i}",
                    description=f"Description {i}",
                    requirements=[f"Req {i}"],
                    owner_id=user.id
                )
                projects.append(project)
            
            session.add_all(projects)
            session.commit()
            
            # Testar performance de consulta
            start_time = time.time()
            
            # Consulta com join
            results = session.query(Project).join(User).filter(
                User.email == "perf_user@example.com"
            ).all()
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Consulta deve ser rápida (menos de 0.1 segundos)
            assert duration < 0.1
            assert len(results) == 50
            
        finally:
            session.close()


if __name__ == "__main__":
    # Executar testes
    pytest.main([__file__, "-v", "--tb=short"])