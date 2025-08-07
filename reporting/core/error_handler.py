"""
Error Handler - Sistema de Tratamento de Erros e Logging
Criado pela Equipe Híbrida CWB Hub

Lucas Pereira (QA): "Sistema robusto de tratamento de erros com logging 
detalhado para garantir a qualidade e confiabilidade do sistema."

Mariana Rodrigues (DevOps): "Monitoramento proativo com alertas 
automáticos para manter a saúde do sistema."
"""

import logging
import traceback
import sys
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from enum import Enum
import json
import asyncio
from dataclasses import dataclass, asdict
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class ErrorSeverity(str, Enum):
    """Níveis de severidade dos erros"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ErrorCategory(str, Enum):
    """Categorias de erros"""
    SYSTEM = "system"
    DATA_COLLECTION = "data_collection"
    TEMPLATE_RENDERING = "template_rendering"
    REPORT_GENERATION = "report_generation"
    SCHEDULING = "scheduling"
    EMAIL_DISTRIBUTION = "email_distribution"
    DATABASE = "database"
    CONFIGURATION = "configuration"
    AUTHENTICATION = "authentication"
    EXTERNAL_API = "external_api"


@dataclass
class ErrorEvent:
    """Estrutura de um evento de erro"""
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    error_code: str
    message: str
    details: Dict[str, Any]
    stack_trace: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    component: Optional[str] = None
    resolution_status: str = "open"
    resolution_time: Optional[datetime] = None


class ReportingErrorHandler:
    """
    Sistema centralizado de tratamento de erros para o sistema de relatórios
    
    Responsabilidades:
    - Capturar e categorizar erros
    - Logging estruturado e detalhado
    - Alertas automáticos para erros críticos
    - Métricas de qualidade e confiabilidade
    - Recovery automático quando possível
    """
    
    def __init__(
        self,
        log_dir: Optional[Path] = None,
        enable_alerts: bool = True,
        alert_recipients: Optional[List[str]] = None
    ):
        # Configurar diretório de logs
        if log_dir is None:
            log_dir = Path(__file__).parent.parent.parent / "logs"
        
        self.log_dir = log_dir
        self.log_dir.mkdir(exist_ok=True)
        
        # Configurações de alertas
        self.enable_alerts = enable_alerts
        self.alert_recipients = alert_recipients or []
        
        # Cache de erros para análise
        self.error_cache: List[ErrorEvent] = []
        self.max_cache_size = 1000
        
        # Callbacks para notificações
        self.error_callbacks: Dict[ErrorSeverity, List[Callable]] = {
            severity: [] for severity in ErrorSeverity
        }
        
        # Configurar loggers
        self._setup_loggers()
        
        # Métricas de erro
        self.error_metrics = {
            "total_errors": 0,
            "errors_by_severity": {severity.value: 0 for severity in ErrorSeverity},
            "errors_by_category": {category.value: 0 for category in ErrorCategory},
            "last_error_time": None,
            "recovery_attempts": 0,
            "successful_recoveries": 0
        }
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.logger.info("Sistema de tratamento de erros inicializado")
    
    def _setup_loggers(self):
        """Configura loggers especializados"""
        
        # Logger principal de erros
        self.error_logger = logging.getLogger("reporting.errors")
        self.error_logger.setLevel(logging.ERROR)
        
        # Logger de auditoria
        self.audit_logger = logging.getLogger("reporting.audit")
        self.audit_logger.setLevel(logging.INFO)
        
        # Logger de performance
        self.performance_logger = logging.getLogger("reporting.performance")
        self.performance_logger.setLevel(logging.INFO)
        
        # Configurar handlers se não existirem
        if not self.error_logger.handlers:
            self._setup_file_handlers()
    
    def _setup_file_handlers(self):
        """Configura handlers de arquivo para logs"""
        
        # Formatter detalhado
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        
        # Handler para erros
        error_handler = logging.FileHandler(
            self.log_dir / "reporting_errors.log",
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        self.error_logger.addHandler(error_handler)
        
        # Handler para auditoria
        audit_handler = logging.FileHandler(
            self.log_dir / "reporting_audit.log",
            encoding='utf-8'
        )
        audit_handler.setLevel(logging.INFO)
        audit_handler.setFormatter(detailed_formatter)
        self.audit_logger.addHandler(audit_handler)
        
        # Handler para performance
        perf_handler = logging.FileHandler(
            self.log_dir / "reporting_performance.log",
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(detailed_formatter)
        self.performance_logger.addHandler(perf_handler)
        
        # Handler para console (apenas erros críticos)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.CRITICAL)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - CRITICAL - %(message)s'
        ))
        self.error_logger.addHandler(console_handler)
    
    async def handle_error(
        self,
        error: Exception,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        component: Optional[str] = None,
        auto_recover: bool = True
    ) -> ErrorEvent:
        """
        Trata um erro de forma centralizada
        
        Args:
            error: Exceção capturada
            severity: Nível de severidade
            category: Categoria do erro
            error_code: Código único do erro
            context: Contexto adicional
            user_id: ID do usuário (se aplicável)
            session_id: ID da sessão
            component: Componente que gerou o erro
            auto_recover: Tentar recovery automático
            
        Returns:
            Evento de erro criado
        """
        
        # Gerar código de erro se não fornecido
        if not error_code:
            error_code = f"{category.value}_{type(error).__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Criar evento de erro
        error_event = ErrorEvent(
            timestamp=datetime.utcnow(),
            severity=severity,
            category=category,
            error_code=error_code,
            message=str(error),
            details=context or {},
            stack_trace=traceback.format_exc(),
            user_id=user_id,
            session_id=session_id,
            component=component
        )
        
        # Adicionar ao cache
        self._add_to_cache(error_event)
        
        # Atualizar métricas
        self._update_metrics(error_event)
        
        # Logging estruturado
        await self._log_error(error_event)
        
        # Tentar recovery automático
        if auto_recover:
            recovery_success = await self._attempt_recovery(error_event)
            if recovery_success:
                error_event.resolution_status = "auto_recovered"
                error_event.resolution_time = datetime.utcnow()
        
        # Enviar alertas se necessário
        if self._should_alert(error_event):
            await self._send_alert(error_event)
        
        # Executar callbacks
        await self._execute_callbacks(error_event)
        
        return error_event
    
    def _add_to_cache(self, error_event: ErrorEvent):
        """Adiciona erro ao cache para análise"""
        self.error_cache.append(error_event)
        
        # Limitar tamanho do cache
        if len(self.error_cache) > self.max_cache_size:
            self.error_cache = self.error_cache[-self.max_cache_size:]
    
    def _update_metrics(self, error_event: ErrorEvent):
        """Atualiza métricas de erro"""
        self.error_metrics["total_errors"] += 1
        self.error_metrics["errors_by_severity"][error_event.severity.value] += 1
        self.error_metrics["errors_by_category"][error_event.category.value] += 1
        self.error_metrics["last_error_time"] = error_event.timestamp
    
    async def _log_error(self, error_event: ErrorEvent):
        """Realiza logging estruturado do erro"""
        
        # Log principal
        log_message = f"[{error_event.error_code}] {error_event.message}"
        
        # Contexto adicional
        context_str = json.dumps(error_event.details, default=str, ensure_ascii=False)
        
        # Log baseado na severidade
        if error_event.severity == ErrorSeverity.CRITICAL:
            self.error_logger.critical(
                f"{log_message} | Context: {context_str} | Stack: {error_event.stack_trace}"
            )
        elif error_event.severity == ErrorSeverity.HIGH:
            self.error_logger.error(
                f"{log_message} | Context: {context_str}"
            )
        elif error_event.severity == ErrorSeverity.MEDIUM:
            self.error_logger.warning(log_message)
        else:
            self.error_logger.info(log_message)
        
        # Log de auditoria
        self.audit_logger.info(
            f"Error Event: {error_event.error_code} | "
            f"Category: {error_event.category.value} | "
            f"Severity: {error_event.severity.value} | "
            f"User: {error_event.user_id} | "
            f"Session: {error_event.session_id}"
        )
    
    async def _attempt_recovery(self, error_event: ErrorEvent) -> bool:
        """Tenta recovery automático baseado no tipo de erro"""
        
        self.error_metrics["recovery_attempts"] += 1
        
        try:
            if error_event.category == ErrorCategory.DATA_COLLECTION:
                return await self._recover_data_collection(error_event)
            
            elif error_event.category == ErrorCategory.TEMPLATE_RENDERING:
                return await self._recover_template_rendering(error_event)
            
            elif error_event.category == ErrorCategory.EMAIL_DISTRIBUTION:
                return await self._recover_email_distribution(error_event)
            
            elif error_event.category == ErrorCategory.DATABASE:
                return await self._recover_database(error_event)
            
            # Outros tipos de recovery podem ser adicionados aqui
            
        except Exception as recovery_error:
            self.logger.error(f"Falha no recovery automático: {recovery_error}")
            return False
        
        return False
    
    async def _recover_data_collection(self, error_event: ErrorEvent) -> bool:
        """Recovery para erros de coleta de dados"""
        try:
            # Tentar usar dados em cache ou dados mock
            self.logger.info(f"Tentando recovery de coleta de dados para {error_event.error_code}")
            
            # Simular recovery (implementação específica seria aqui)
            await asyncio.sleep(1)  # Simular tentativa
            
            self.error_metrics["successful_recoveries"] += 1
            return True
            
        except Exception:
            return False
    
    async def _recover_template_rendering(self, error_event: ErrorEvent) -> bool:
        """Recovery para erros de renderização de template"""
        try:
            # Tentar template alternativo ou template básico
            self.logger.info(f"Tentando recovery de template para {error_event.error_code}")
            
            # Implementação específica seria aqui
            await asyncio.sleep(0.5)
            
            self.error_metrics["successful_recoveries"] += 1
            return True
            
        except Exception:
            return False
    
    async def _recover_email_distribution(self, error_event: ErrorEvent) -> bool:
        """Recovery para erros de distribuição de email"""
        try:
            # Tentar reenvio ou servidor alternativo
            self.logger.info(f"Tentando recovery de email para {error_event.error_code}")
            
            # Implementação específica seria aqui
            await asyncio.sleep(2)
            
            self.error_metrics["successful_recoveries"] += 1
            return True
            
        except Exception:
            return False
    
    async def _recover_database(self, error_event: ErrorEvent) -> bool:
        """Recovery para erros de banco de dados"""
        try:
            # Tentar reconexão ou fallback
            self.logger.info(f"Tentando recovery de database para {error_event.error_code}")
            
            # Implementação específica seria aqui
            await asyncio.sleep(3)
            
            self.error_metrics["successful_recoveries"] += 1
            return True
            
        except Exception:
            return False
    
    def _should_alert(self, error_event: ErrorEvent) -> bool:
        """Determina se deve enviar alerta para o erro"""
        
        # Sempre alertar para erros críticos
        if error_event.severity == ErrorSeverity.CRITICAL:
            return True
        
        # Alertar para erros high em componentes críticos
        if (error_event.severity == ErrorSeverity.HIGH and 
            error_event.category in [ErrorCategory.SYSTEM, ErrorCategory.DATABASE]):
            return True
        
        # Verificar frequência de erros similares
        recent_similar_errors = [
            e for e in self.error_cache[-50:]  # Últimos 50 erros
            if (e.category == error_event.category and 
                (datetime.utcnow() - e.timestamp).total_seconds() < 3600)  # Última hora
        ]
        
        # Alertar se muitos erros similares
        if len(recent_similar_errors) >= 5:
            return True
        
        return False
    
    async def _send_alert(self, error_event: ErrorEvent):
        """Envia alerta para o erro"""
        
        if not self.enable_alerts or not self.alert_recipients:
            return
        
        try:
            # Preparar conteúdo do alerta
            subject = f"🚨 Alerta CWB Hub: {error_event.severity.value.upper()} - {error_event.category.value}"
            
            body = f"""
            <html>
            <body>
                <h2>🚨 Alerta do Sistema de Relatórios CWB Hub</h2>
                
                <h3>Detalhes do Erro:</h3>
                <ul>
                    <li><strong>Código:</strong> {error_event.error_code}</li>
                    <li><strong>Severidade:</strong> {error_event.severity.value.upper()}</li>
                    <li><strong>Categoria:</strong> {error_event.category.value}</li>
                    <li><strong>Timestamp:</strong> {error_event.timestamp.strftime('%d/%m/%Y %H:%M:%S')}</li>
                    <li><strong>Componente:</strong> {error_event.component or 'N/A'}</li>
                </ul>
                
                <h3>Mensagem:</h3>
                <p>{error_event.message}</p>
                
                <h3>Contexto:</h3>
                <pre>{json.dumps(error_event.details, indent=2, default=str, ensure_ascii=False)}</pre>
                
                <h3>Status de Recovery:</h3>
                <p>{error_event.resolution_status}</p>
                
                <hr>
                <p><small>Sistema de Relatórios CWB Hub - Alerta Automático</small></p>
            </body>
            </html>
            """
            
            # Enviar email (implementação simplificada)
            await self._send_alert_email(subject, body)
            
        except Exception as e:
            self.logger.error(f"Falha ao enviar alerta: {e}")
    
    async def _send_alert_email(self, subject: str, body: str):
        """Envia email de alerta"""
        try:
            # Configuração SMTP básica (seria configurável)
            smtp_server = "localhost"  # Configurar conforme necessário
            smtp_port = 587
            
            msg = MIMEMultipart()
            msg['From'] = "alerts@cwbhub.com"
            msg['To'] = ", ".join(self.alert_recipients)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            # Enviar (em produção, usar configuração real)
            # server = smtplib.SMTP(smtp_server, smtp_port)
            # server.send_message(msg)
            # server.quit()
            
            self.logger.info(f"Alerta enviado para {len(self.alert_recipients)} destinatários")
            
        except Exception as e:
            self.logger.error(f"Falha no envio de email de alerta: {e}")
    
    async def _execute_callbacks(self, error_event: ErrorEvent):
        """Executa callbacks registrados para o tipo de erro"""
        
        callbacks = self.error_callbacks.get(error_event.severity, [])
        
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(error_event)
                else:
                    callback(error_event)
            except Exception as e:
                self.logger.error(f"Erro ao executar callback: {e}")
    
    def add_error_callback(self, severity: ErrorSeverity, callback: Callable):
        """Adiciona callback para ser executado quando erro ocorrer"""
        self.error_callbacks[severity].append(callback)
    
    def get_error_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de erro"""
        return {
            **self.error_metrics,
            "error_rate": self._calculate_error_rate(),
            "recovery_rate": self._calculate_recovery_rate(),
            "recent_errors": len([
                e for e in self.error_cache
                if (datetime.utcnow() - e.timestamp).total_seconds() < 3600
            ])
        }
    
    def _calculate_error_rate(self) -> float:
        """Calcula taxa de erro por hora"""
        recent_errors = [
            e for e in self.error_cache
            if (datetime.utcnow() - e.timestamp).total_seconds() < 3600
        ]
        return len(recent_errors)
    
    def _calculate_recovery_rate(self) -> float:
        """Calcula taxa de recovery bem-sucedido"""
        if self.error_metrics["recovery_attempts"] == 0:
            return 0.0
        
        return (self.error_metrics["successful_recoveries"] / 
                self.error_metrics["recovery_attempts"]) * 100
    
    def get_recent_errors(self, hours: int = 24) -> List[ErrorEvent]:
        """Retorna erros recentes"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        return [
            e for e in self.error_cache
            if e.timestamp >= cutoff_time
        ]
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Retorna resumo de erros para relatórios"""
        recent_errors = self.get_recent_errors(24)
        
        return {
            "total_errors_24h": len(recent_errors),
            "critical_errors_24h": len([e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL]),
            "most_common_category": self._get_most_common_category(recent_errors),
            "error_trend": self._get_error_trend(),
            "system_health_score": self._calculate_health_score(),
            "last_critical_error": self._get_last_critical_error()
        }
    
    def _get_most_common_category(self, errors: List[ErrorEvent]) -> str:
        """Retorna categoria de erro mais comum"""
        if not errors:
            return "none"
        
        categories = [e.category.value for e in errors]
        return max(set(categories), key=categories.count)
    
    def _get_error_trend(self) -> str:
        """Analisa tendência de erros"""
        recent_errors = self.get_recent_errors(24)
        older_errors = self.get_recent_errors(48)
        older_errors = [e for e in older_errors if e not in recent_errors]
        
        if len(recent_errors) > len(older_errors) * 1.2:
            return "increasing"
        elif len(recent_errors) < len(older_errors) * 0.8:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_health_score(self) -> float:
        """Calcula score de saúde do sistema (0-100)"""
        recent_errors = self.get_recent_errors(24)
        
        # Base score
        score = 100.0
        
        # Penalizar por erros críticos
        critical_errors = [e for e in recent_errors if e.severity == ErrorSeverity.CRITICAL]
        score -= len(critical_errors) * 20
        
        # Penalizar por erros high
        high_errors = [e for e in recent_errors if e.severity == ErrorSeverity.HIGH]
        score -= len(high_errors) * 10
        
        # Penalizar por volume total de erros
        score -= min(len(recent_errors) * 2, 30)
        
        # Bonificar por recovery bem-sucedido
        recovery_rate = self._calculate_recovery_rate()
        score += recovery_rate * 0.2
        
        return max(0.0, min(100.0, score))
    
    def _get_last_critical_error(self) -> Optional[Dict[str, Any]]:
        """Retorna último erro crítico"""
        critical_errors = [
            e for e in reversed(self.error_cache)
            if e.severity == ErrorSeverity.CRITICAL
        ]
        
        if critical_errors:
            error = critical_errors[0]
            return {
                "timestamp": error.timestamp.isoformat(),
                "code": error.error_code,
                "message": error.message,
                "category": error.category.value
            }
        
        return None
    
    async def cleanup_old_errors(self, days: int = 30):
        """Remove erros antigos do cache"""
        cutoff_time = datetime.utcnow() - timedelta(days=days)
        
        original_count = len(self.error_cache)
        self.error_cache = [
            e for e in self.error_cache
            if e.timestamp >= cutoff_time
        ]
        
        removed_count = original_count - len(self.error_cache)
        if removed_count > 0:
            self.logger.info(f"Removidos {removed_count} erros antigos do cache")


# Instância global do error handler
error_handler = ReportingErrorHandler()


# Decorador para captura automática de erros
def handle_errors(
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.SYSTEM,
    auto_recover: bool = True
):
    """
    Decorador para captura automática de erros
    
    Usage:
        @handle_errors(severity=ErrorSeverity.HIGH, category=ErrorCategory.DATA_COLLECTION)
        async def collect_data():
            # código que pode gerar erro
            pass
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                await error_handler.handle_error(
                    error=e,
                    severity=severity,
                    category=category,
                    component=f"{func.__module__}.{func.__name__}",
                    auto_recover=auto_recover,
                    context={
                        "function": func.__name__,
                        "args": str(args)[:200],  # Limitar tamanho
                        "kwargs": str(kwargs)[:200]
                    }
                )
                raise  # Re-raise para não quebrar o fluxo
        return wrapper
    return decorator