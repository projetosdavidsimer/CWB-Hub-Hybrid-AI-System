"""
Authentication and Authorization Module
Sistema de Autenticação e Autorização CWB Hub

Criado pela Equipe Híbrida CWB Hub
"""

from .auth_manager import (
    AuthenticationManager,
    User,
    Session,
    UserRole,
    Permission,
    auth_manager,
    require_auth
)

__all__ = [
    "AuthenticationManager",
    "User", 
    "Session",
    "UserRole",
    "Permission",
    "auth_manager",
    "require_auth"
]