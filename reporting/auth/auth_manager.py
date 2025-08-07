"""
Authentication and Authorization Manager - Sistema de Autenticação e Autorização
Criado pela Equipe Híbrida CWB Hub

Mariana Rodrigues (DevOps): "Sistema de segurança robusto com múltiplas 
camadas de proteção e controle granular de acesso."

Carlos Eduardo Santos (Arquiteto): "Arquitetura de segurança escalável 
com JWT, RBAC e auditoria completa."
"""

import logging
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set
from enum import Enum
from dataclasses import dataclass, asdict
import json
from pathlib import Path
import asyncio

from ..core.error_handler import error_handler, ErrorSeverity, ErrorCategory, handle_errors

logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    """Roles de usuário no sistema"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"
    GUEST = "guest"


class Permission(str, Enum):
    """Permissões específicas do sistema"""
    # Relatórios
    VIEW_REPORTS = "view_reports"
    GENERATE_REPORTS = "generate_reports"
    SCHEDULE_REPORTS = "schedule_reports"
    DELETE_REPORTS = "delete_reports"
    EXPORT_REPORTS = "export_reports"
    
    # Dashboard
    VIEW_DASHBOARD = "view_dashboard"
    CUSTOMIZE_DASHBOARD = "customize_dashboard"
    
    # Configurações
    MANAGE_USERS = "manage_users"
    MANAGE_SYSTEM_CONFIG = "manage_system_config"
    MANAGE_TEMPLATES = "manage_templates"
    
    # Dados
    VIEW_RAW_DATA = "view_raw_data"
    EXPORT_DATA = "export_data"
    
    # Sistema
    VIEW_LOGS = "view_logs"
    MANAGE_ALERTS = "manage_alerts"
    SYSTEM_ADMIN = "system_admin"


@dataclass
class User:
    """Modelo de usuário"""
    id: str
    username: str
    email: str
    full_name: str
    role: UserRole
    permissions: Set[Permission]
    is_active: bool = True
    created_at: datetime = None
    last_login: Optional[datetime] = None
    password_hash: Optional[str] = None
    company: Optional[str] = None
    department: Optional[str] = None
    preferences: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.preferences is None:
            self.preferences = {}


@dataclass
class Session:
    """Sessão de usuário"""
    session_id: str
    user_id: str
    created_at: datetime
    expires_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    is_active: bool = True


class AuthenticationManager:
    """
    Gerenciador de autenticação e autorização
    
    Responsabilidades:
    - Autenticação de usuários (login/logout)
    - Autorização baseada em roles e permissões
    - Gestão de sessões e tokens JWT
    - Auditoria de acesso
    - Controle de segurança
    """
    
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or self._generate_secret_key()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Armazenamento em memória (em produção seria banco de dados)
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self.failed_attempts: Dict[str, List[datetime]] = {}
        
        # Configurações de segurança
        self.security_config = {
            "max_failed_attempts": 5,
            "lockout_duration_minutes": 30,
            "session_timeout_hours": 8,
            "jwt_expiry_hours": 24,
            "password_min_length": 8,
            "require_password_complexity": True
        }
        
        # Mapeamento de roles para permissões
        self.role_permissions = self._get_role_permissions()
        
        # Criar usuários padrão
        self._create_default_users()
        
        # Auditoria
        self.audit_log: List[Dict[str, Any]] = []
        
        self.logger.info("Authentication Manager inicializado")
    
    def _generate_secret_key(self) -> str:
        """Gera chave secreta para JWT"""
        return secrets.token_urlsafe(32)
    
    def _get_role_permissions(self) -> Dict[UserRole, Set[Permission]]:
        """Define permissões por role"""
        return {
            UserRole.SUPER_ADMIN: set(Permission),  # Todas as permissões
            
            UserRole.ADMIN: {
                Permission.VIEW_REPORTS, Permission.GENERATE_REPORTS,
                Permission.SCHEDULE_REPORTS, Permission.DELETE_REPORTS,
                Permission.EXPORT_REPORTS, Permission.VIEW_DASHBOARD,
                Permission.CUSTOMIZE_DASHBOARD, Permission.MANAGE_USERS,
                Permission.MANAGE_SYSTEM_CONFIG, Permission.MANAGE_TEMPLATES,
                Permission.VIEW_RAW_DATA, Permission.EXPORT_DATA,
                Permission.VIEW_LOGS, Permission.MANAGE_ALERTS
            },
            
            UserRole.MANAGER: {
                Permission.VIEW_REPORTS, Permission.GENERATE_REPORTS,
                Permission.SCHEDULE_REPORTS, Permission.EXPORT_REPORTS,
                Permission.VIEW_DASHBOARD, Permission.CUSTOMIZE_DASHBOARD,
                Permission.VIEW_RAW_DATA, Permission.EXPORT_DATA
            },
            
            UserRole.ANALYST: {
                Permission.VIEW_REPORTS, Permission.GENERATE_REPORTS,
                Permission.VIEW_DASHBOARD, Permission.VIEW_RAW_DATA,
                Permission.EXPORT_DATA
            },
            
            UserRole.VIEWER: {
                Permission.VIEW_REPORTS, Permission.VIEW_DASHBOARD
            },
            
            UserRole.GUEST: {
                Permission.VIEW_DASHBOARD
            }
        }
    
    def _create_default_users(self):
        """Cria usuários padrão do sistema"""
        default_users = [
            {
                "id": "admin",
                "username": "admin",
                "email": "admin@cwbhub.com",
                "full_name": "Administrador do Sistema",
                "role": UserRole.SUPER_ADMIN,
                "password": "admin123",
                "company": "CWB Hub",
                "department": "TI"
            },
            {
                "id": "ana_beatriz",
                "username": "ana.beatriz",
                "email": "ana.beatriz@cwbhub.com",
                "full_name": "Ana Beatriz Costa",
                "role": UserRole.ADMIN,
                "password": "cto123",
                "company": "CWB Hub",
                "department": "Estratégia"
            },
            {
                "id": "carlos_eduardo",
                "username": "carlos.eduardo",
                "email": "carlos.eduardo@cwbhub.com",
                "full_name": "Carlos Eduardo Santos",
                "role": UserRole.ADMIN,
                "password": "arch123",
                "company": "CWB Hub",
                "department": "Arquitetura"
            },
            {
                "id": "manager_demo",
                "username": "manager",
                "email": "manager@cwbhub.com",
                "full_name": "Gerente de Demonstração",
                "role": UserRole.MANAGER,
                "password": "manager123",
                "company": "CWB Hub",
                "department": "Gestão"
            },
            {
                "id": "analyst_demo",
                "username": "analyst",
                "email": "analyst@cwbhub.com",
                "full_name": "Analista de Demonstração",
                "role": UserRole.ANALYST,
                "password": "analyst123",
                "company": "CWB Hub",
                "department": "Análise"
            }
        ]
        
        for user_data in default_users:
            password = user_data.pop("password")
            user = User(
                permissions=self.role_permissions[user_data["role"]],
                **user_data
            )
            user.password_hash = self._hash_password(password)
            self.users[user.id] = user
        
        self.logger.info(f"Criados {len(default_users)} usuários padrão")
    
    @handle_errors(severity=ErrorSeverity.HIGH, category=ErrorCategory.AUTHENTICATION)
    async def authenticate(
        self, 
        username: str, 
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Autentica usuário e cria sessão
        
        Args:
            username: Nome de usuário ou email
            password: Senha
            ip_address: IP do cliente
            user_agent: User agent do cliente
            
        Returns:
            Dados da sessão se autenticado, None caso contrário
        """
        
        # Verificar tentativas de login falhadas
        if self._is_account_locked(username):
            self._log_audit("login_blocked", username, {"reason": "account_locked"})
            raise ValueError("Conta temporariamente bloqueada devido a múltiplas tentativas falhadas")
        
        # Encontrar usuário
        user = self._find_user(username)
        if not user:
            self._record_failed_attempt(username)
            self._log_audit("login_failed", username, {"reason": "user_not_found"})
            return None
        
        # Verificar se usuário está ativo
        if not user.is_active:
            self._log_audit("login_failed", username, {"reason": "user_inactive"})
            return None
        
        # Verificar senha
        if not self._verify_password(password, user.password_hash):
            self._record_failed_attempt(username)
            self._log_audit("login_failed", username, {"reason": "invalid_password"})
            return None
        
        # Limpar tentativas falhadas
        if username in self.failed_attempts:
            del self.failed_attempts[username]
        
        # Criar sessão
        session = await self._create_session(user, ip_address, user_agent)
        
        # Atualizar último login
        user.last_login = datetime.utcnow()
        
        # Gerar token JWT
        token = self._generate_jwt_token(user, session)
        
        # Log de auditoria
        self._log_audit("login_success", username, {
            "session_id": session.session_id,
            "ip_address": ip_address
        })
        
        self.logger.info(f"Usuário {username} autenticado com sucesso")
        
        return {
            "user": self._user_to_dict(user),
            "session": asdict(session),
            "token": token,
            "permissions": list(user.permissions)
        }
    
    async def logout(self, session_id: str) -> bool:
        """
        Realiza logout do usuário
        
        Args:
            session_id: ID da sessão
            
        Returns:
            True se logout realizado com sucesso
        """
        
        session = self.sessions.get(session_id)
        if not session:
            return False
        
        # Desativar sessão
        session.is_active = False
        
        # Log de auditoria
        self._log_audit("logout", session.user_id, {"session_id": session_id})
        
        self.logger.info(f"Logout realizado para sessão {session_id}")
        return True
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verifica e decodifica token JWT
        
        Args:
            token: Token JWT
            
        Returns:
            Dados do token se válido, None caso contrário
        """
        
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            
            # Verificar se sessão ainda é válida
            session_id = payload.get("session_id")
            session = self.sessions.get(session_id)
            
            if not session or not session.is_active:
                return None
            
            # Verificar se sessão não expirou
            if datetime.utcnow() > session.expires_at:
                session.is_active = False
                return None
            
            # Atualizar última atividade
            session.last_activity = datetime.utcnow()
            
            return payload
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Token JWT expirado")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Token JWT inválido")
            return None
    
    def check_permission(self, user_id: str, permission: Permission) -> bool:
        """
        Verifica se usuário tem permissão específica
        
        Args:
            user_id: ID do usuário
            permission: Permissão a verificar
            
        Returns:
            True se usuário tem a permissão
        """
        
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return False
        
        return permission in user.permissions
    
    def check_role(self, user_id: str, required_role: UserRole) -> bool:
        """
        Verifica se usuário tem role específico ou superior
        
        Args:
            user_id: ID do usuário
            required_role: Role mínimo requerido
            
        Returns:
            True se usuário tem o role ou superior
        """
        
        user = self.users.get(user_id)
        if not user or not user.is_active:
            return False
        
        # Hierarquia de roles
        role_hierarchy = {
            UserRole.GUEST: 0,
            UserRole.VIEWER: 1,
            UserRole.ANALYST: 2,
            UserRole.MANAGER: 3,
            UserRole.ADMIN: 4,
            UserRole.SUPER_ADMIN: 5
        }
        
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    async def create_user(
        self,
        username: str,
        email: str,
        full_name: str,
        role: UserRole,
        password: str,
        company: Optional[str] = None,
        department: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> User:
        """
        Cria novo usuário
        
        Args:
            username: Nome de usuário único
            email: Email único
            full_name: Nome completo
            role: Role do usuário
            password: Senha
            company: Empresa
            department: Departamento
            created_by: ID do usuário que criou
            
        Returns:
            Usuário criado
        """
        
        # Validar se username e email são únicos
        if self._find_user(username) or self._find_user(email):
            raise ValueError("Username ou email já existem")
        
        # Validar senha
        if not self._validate_password(password):
            raise ValueError("Senha não atende aos critérios de segurança")
        
        # Criar usuário
        user_id = f"user_{len(self.users) + 1}"
        user = User(
            id=user_id,
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            permissions=self.role_permissions[role],
            company=company,
            department=department
        )
        
        user.password_hash = self._hash_password(password)
        self.users[user_id] = user
        
        # Log de auditoria
        self._log_audit("user_created", created_by or "system", {
            "new_user_id": user_id,
            "username": username,
            "role": role.value
        })
        
        self.logger.info(f"Usuário {username} criado com sucesso")
        return user
    
    async def update_user(
        self,
        user_id: str,
        updates: Dict[str, Any],
        updated_by: str
    ) -> bool:
        """
        Atualiza dados do usuário
        
        Args:
            user_id: ID do usuário
            updates: Campos a atualizar
            updated_by: ID do usuário que fez a atualização
            
        Returns:
            True se atualizado com sucesso
        """
        
        user = self.users.get(user_id)
        if not user:
            return False
        
        # Campos permitidos para atualização
        allowed_fields = {
            "full_name", "email", "role", "is_active", 
            "company", "department", "preferences"
        }
        
        changes = {}
        for field, value in updates.items():
            if field in allowed_fields:
                old_value = getattr(user, field)
                setattr(user, field, value)
                changes[field] = {"old": old_value, "new": value}
                
                # Atualizar permissões se role mudou
                if field == "role":
                    user.permissions = self.role_permissions[value]
        
        # Log de auditoria
        if changes:
            self._log_audit("user_updated", updated_by, {
                "user_id": user_id,
                "changes": changes
            })
        
        return True
    
    async def change_password(
        self,
        user_id: str,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Altera senha do usuário
        
        Args:
            user_id: ID do usuário
            old_password: Senha atual
            new_password: Nova senha
            
        Returns:
            True se senha alterada com sucesso
        """
        
        user = self.users.get(user_id)
        if not user:
            return False
        
        # Verificar senha atual
        if not self._verify_password(old_password, user.password_hash):
            return False
        
        # Validar nova senha
        if not self._validate_password(new_password):
            raise ValueError("Nova senha não atende aos critérios de segurança")
        
        # Atualizar senha
        user.password_hash = self._hash_password(new_password)
        
        # Log de auditoria
        self._log_audit("password_changed", user_id, {})
        
        self.logger.info(f"Senha alterada para usuário {user_id}")
        return True
    
    def get_user_sessions(self, user_id: str) -> List[Session]:
        """Retorna sessões ativas do usuário"""
        return [
            session for session in self.sessions.values()
            if session.user_id == user_id and session.is_active
        ]
    
    async def cleanup_expired_sessions(self):
        """Remove sessões expiradas"""
        now = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if now > session.expires_at or not session.is_active:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            self.logger.info(f"Removidas {len(expired_sessions)} sessões expiradas")
    
    def _find_user(self, identifier: str) -> Optional[User]:
        """Encontra usuário por username ou email"""
        for user in self.users.values():
            if user.username == identifier or user.email == identifier:
                return user
        return None
    
    def _hash_password(self, password: str) -> str:
        """Gera hash da senha"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """Verifica senha contra hash"""
        try:
            salt, hash_hex = password_hash.split(':')
            password_check = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
            return password_check.hex() == hash_hex
        except Exception:
            return False
    
    def _validate_password(self, password: str) -> bool:
        """Valida critérios de segurança da senha"""
        if len(password) < self.security_config["password_min_length"]:
            return False
        
        if self.security_config["require_password_complexity"]:
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
            
            return has_upper and has_lower and has_digit and has_special
        
        return True
    
    def _is_account_locked(self, username: str) -> bool:
        """Verifica se conta está bloqueada por tentativas falhadas"""
        if username not in self.failed_attempts:
            return False
        
        attempts = self.failed_attempts[username]
        max_attempts = self.security_config["max_failed_attempts"]
        lockout_duration = timedelta(minutes=self.security_config["lockout_duration_minutes"])
        
        # Remover tentativas antigas
        cutoff_time = datetime.utcnow() - lockout_duration
        attempts = [attempt for attempt in attempts if attempt > cutoff_time]
        self.failed_attempts[username] = attempts
        
        return len(attempts) >= max_attempts
    
    def _record_failed_attempt(self, username: str):
        """Registra tentativa de login falhada"""
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
        
        self.failed_attempts[username].append(datetime.utcnow())
    
    async def _create_session(
        self,
        user: User,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> Session:
        """Cria nova sessão para usuário"""
        
        session_id = secrets.token_urlsafe(32)
        now = datetime.utcnow()
        expires_at = now + timedelta(hours=self.security_config["session_timeout_hours"])
        
        session = Session(
            session_id=session_id,
            user_id=user.id,
            created_at=now,
            expires_at=expires_at,
            last_activity=now,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.sessions[session_id] = session
        return session
    
    def _generate_jwt_token(self, user: User, session: Session) -> str:
        """Gera token JWT para usuário"""
        
        payload = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value,
            "session_id": session.session_id,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=self.security_config["jwt_expiry_hours"])
        }
        
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def _user_to_dict(self, user: User) -> Dict[str, Any]:
        """Converte usuário para dicionário (sem dados sensíveis)"""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat() if user.last_login else None,
            "company": user.company,
            "department": user.department,
            "preferences": user.preferences
        }
    
    def _log_audit(self, action: str, user_id: str, details: Dict[str, Any]):
        """Registra evento de auditoria"""
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "user_id": user_id,
            "details": details
        }
        
        self.audit_log.append(audit_entry)
        
        # Manter apenas últimos 1000 eventos
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-1000:]
    
    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retorna log de auditoria filtrado"""
        
        filtered_log = self.audit_log
        
        if user_id:
            filtered_log = [entry for entry in filtered_log if entry["user_id"] == user_id]
        
        if action:
            filtered_log = [entry for entry in filtered_log if entry["action"] == action]
        
        return filtered_log[-limit:]
    
    def get_security_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas de segurança"""
        
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        
        # Contar eventos das últimas 24h
        recent_logins = len([
            entry for entry in self.audit_log
            if entry["action"] == "login_success" and 
            datetime.fromisoformat(entry["timestamp"]) > last_24h
        ])
        
        failed_logins = len([
            entry for entry in self.audit_log
            if entry["action"] == "login_failed" and 
            datetime.fromisoformat(entry["timestamp"]) > last_24h
        ])
        
        return {
            "total_users": len(self.users),
            "active_users": len([u for u in self.users.values() if u.is_active]),
            "active_sessions": len([s for s in self.sessions.values() if s.is_active]),
            "recent_logins_24h": recent_logins,
            "failed_logins_24h": failed_logins,
            "locked_accounts": len(self.failed_attempts),
            "audit_events_total": len(self.audit_log)
        }
    
    def export_users(self) -> List[Dict[str, Any]]:
        """Exporta lista de usuários (sem dados sensíveis)"""
        return [self._user_to_dict(user) for user in self.users.values()]
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retorna dados do usuário por ID"""
        user = self.users.get(user_id)
        return self._user_to_dict(user) if user else None


# Instância global do gerenciador de autenticação
auth_manager = AuthenticationManager()


# Decorador para verificar autenticação
def require_auth(permission: Optional[Permission] = None, role: Optional[UserRole] = None):
    """
    Decorador para verificar autenticação e autorização
    
    Args:
        permission: Permissão específica requerida
        role: Role mínimo requerido
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extrair token do contexto (seria implementado conforme framework web)
            token = kwargs.get("auth_token")
            if not token:
                raise ValueError("Token de autenticação requerido")
            
            # Verificar token
            payload = auth_manager.verify_token(token)
            if not payload:
                raise ValueError("Token inválido ou expirado")
            
            user_id = payload["user_id"]
            
            # Verificar permissão específica
            if permission and not auth_manager.check_permission(user_id, permission):
                raise ValueError(f"Permissão '{permission.value}' requerida")
            
            # Verificar role mínimo
            if role and not auth_manager.check_role(user_id, role):
                raise ValueError(f"Role '{role.value}' ou superior requerido")
            
            # Adicionar dados do usuário ao contexto
            kwargs["current_user"] = auth_manager.get_user_by_id(user_id)
            kwargs["user_permissions"] = list(auth_manager.users[user_id].permissions)
            
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator