#!/usr/bin/env python3
"""
CWB Hub Persistence System - JWT Authentication Handler
Sistema de autenticação JWT com refresh tokens
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from passlib.context import CryptContext
from passlib.hash import bcrypt
import os
import secrets
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações JWT
JWT_CONFIG = {
    "secret_key": os.getenv("JWT_SECRET_KEY", secrets.token_urlsafe(32)),
    "algorithm": "HS256",
    "access_token_expire_minutes": int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")),
    "refresh_token_expire_days": int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")),
}

# Context para hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class JWTHandler:
    """Manipulador de tokens JWT"""
    
    def __init__(self):
        self.secret_key = JWT_CONFIG["secret_key"]
        self.algorithm = JWT_CONFIG["algorithm"]
        self.access_token_expire_minutes = JWT_CONFIG["access_token_expire_minutes"]
        self.refresh_token_expire_days = JWT_CONFIG["refresh_token_expire_days"]
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Cria um token de acesso"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({
            "exp": expire,
            "type": "access",
            "iat": datetime.utcnow()
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Token de acesso criado para usuário: {data.get('sub', 'unknown')}")
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Cria um token de refresh"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({
            "exp": expire,
            "type": "refresh",
            "iat": datetime.utcnow()
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Token de refresh criado para usuário: {data.get('sub', 'unknown')}")
        return encoded_jwt
    
    def create_token_pair(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Cria um par de tokens (access + refresh)"""
        access_token = self.create_access_token(user_data)
        refresh_token = self.create_refresh_token(user_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica e decodifica um token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verificar se o token não expirou
            exp = payload.get("exp")
            if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
                logger.warning("Token expirado")
                return None
            
            return payload
        
        except jwt.ExpiredSignatureError:
            logger.warning("Token expirado")
            return None
        except jwt.JWTError as e:
            logger.error(f"Erro ao verificar token: {e}")
            return None
    
    def verify_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica especificamente um token de acesso"""
        payload = self.verify_token(token)
        if payload and payload.get("type") == "access":
            return payload
        return None
    
    def verify_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verifica especificamente um token de refresh"""
        payload = self.verify_token(token)
        if payload and payload.get("type") == "refresh":
            return payload
        return None
    
    def refresh_access_token(self, refresh_token: str) -> Optional[Dict[str, str]]:
        """Gera um novo token de acesso usando o refresh token"""
        payload = self.verify_refresh_token(refresh_token)
        if not payload:
            return None
        
        # Criar novo token de acesso com os mesmos dados do usuário
        user_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "company": payload.get("company")
        }
        
        new_access_token = self.create_access_token(user_data)
        
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": self.access_token_expire_minutes * 60
        }
    
    def get_token_info(self, token: str) -> Optional[Dict[str, Any]]:
        """Obtém informações sobre um token sem verificar expiração"""
        try:
            # Decodificar sem verificar expiração
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options={"verify_exp": False})
            
            exp = payload.get("exp")
            iat = payload.get("iat")
            
            return {
                "user_id": payload.get("sub"),
                "email": payload.get("email"),
                "role": payload.get("role"),
                "company": payload.get("company"),
                "token_type": payload.get("type"),
                "issued_at": datetime.fromtimestamp(iat) if iat else None,
                "expires_at": datetime.fromtimestamp(exp) if exp else None,
                "is_expired": datetime.utcnow() > datetime.fromtimestamp(exp) if exp else False
            }
        except jwt.JWTError as e:
            logger.error(f"Erro ao obter informações do token: {e}")
            return None


class PasswordHandler:
    """Manipulador de senhas"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Gera hash da senha"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha está correta"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def generate_password(length: int = 12) -> str:
        """Gera uma senha aleatória"""
        return secrets.token_urlsafe(length)


# Instâncias globais
jwt_handler = JWTHandler()
password_handler = PasswordHandler()


# Funções de conveniência
def create_user_tokens(user_id: int, email: str, role: str, company: str) -> Dict[str, str]:
    """Cria tokens para um usuário"""
    user_data = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "company": company
    }
    return jwt_handler.create_token_pair(user_data)


def verify_user_token(token: str) -> Optional[Dict[str, Any]]:
    """Verifica token de usuário"""
    return jwt_handler.verify_access_token(token)


def refresh_user_token(refresh_token: str) -> Optional[Dict[str, str]]:
    """Atualiza token de usuário"""
    return jwt_handler.refresh_access_token(refresh_token)


def hash_user_password(password: str) -> str:
    """Hash da senha do usuário"""
    return password_handler.hash_password(password)


def verify_user_password(password: str, hashed: str) -> bool:
    """Verifica senha do usuário"""
    return password_handler.verify_password(password, hashed)


# Middleware de autenticação para FastAPI
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Dependency para obter usuário atual autenticado"""
    token = credentials.credentials
    payload = verify_user_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {
        "user_id": int(payload["sub"]),
        "email": payload["email"],
        "role": payload["role"],
        "company": payload["company"]
    }


def require_role(required_role: str):
    """Decorator para exigir role específica"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
        if current_user["role"] != required_role and current_user["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Role necessária: {required_role}"
            )
        return current_user
    return role_checker


def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Dependency para exigir role de admin"""
    if current_user["role"] != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores."
        )
    return current_user


if __name__ == "__main__":
    # Teste do sistema de autenticação
    print("🔐 Testando sistema de autenticação JWT...")
    
    # Criar tokens de teste
    test_user_data = {
        "sub": "123",
        "email": "test@cwbhub.com",
        "role": "user",
        "company": "CWB Hub Test"
    }
    
    # Criar par de tokens
    tokens = jwt_handler.create_token_pair(test_user_data)
    print(f"✅ Tokens criados:")
    print(f"   Access Token: {tokens['access_token'][:50]}...")
    print(f"   Refresh Token: {tokens['refresh_token'][:50]}...")
    
    # Verificar token de acesso
    access_payload = jwt_handler.verify_access_token(tokens["access_token"])
    if access_payload:
        print(f"✅ Token de acesso válido para usuário: {access_payload['email']}")
    
    # Testar refresh
    new_tokens = jwt_handler.refresh_access_token(tokens["refresh_token"])
    if new_tokens:
        print(f"✅ Token renovado com sucesso")
    
    # Testar senhas
    password = "minha_senha_secreta"
    hashed = password_handler.hash_password(password)
    print(f"✅ Senha hasheada: {hashed[:50]}...")
    
    if password_handler.verify_password(password, hashed):
        print("✅ Verificação de senha funcionando!")
    
    print("🎉 Sistema de autenticação testado com sucesso!")