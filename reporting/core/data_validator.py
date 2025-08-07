"""
Data Validator - Sistema de Validação e Qualidade de Dados
Criado pela Equipe Híbrida CWB Hub

Lucas Pereira (QA): "Validação rigorosa de dados para garantir a 
confiabilidade e precisão de todos os relatórios gerados."

Carlos Eduardo Santos (Arquiteto): "Sistema robusto de validação com 
múltiplas camadas de verificação e correção automática."
"""

import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import statistics
import json

from .error_handler import error_handler, ErrorSeverity, ErrorCategory, handle_errors

logger = logging.getLogger(__name__)


class ValidationSeverity(str, Enum):
    """Níveis de severidade das validações"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ValidationRule(str, Enum):
    """Tipos de regras de validação"""
    REQUIRED = "required"
    TYPE_CHECK = "type_check"
    RANGE_CHECK = "range_check"
    FORMAT_CHECK = "format_check"
    CONSISTENCY_CHECK = "consistency_check"
    BUSINESS_RULE = "business_rule"
    STATISTICAL_CHECK = "statistical_check"
    TEMPORAL_CHECK = "temporal_check"


@dataclass
class ValidationResult:
    """Resultado de uma validação"""
    field_name: str
    rule_type: ValidationRule
    severity: ValidationSeverity
    is_valid: bool
    message: str
    expected_value: Optional[Any] = None
    actual_value: Optional[Any] = None
    suggested_fix: Optional[str] = None
    auto_correctable: bool = False


@dataclass
class DataQualityReport:
    """Relatório de qualidade dos dados"""
    timestamp: datetime
    total_validations: int
    passed_validations: int
    failed_validations: int
    quality_score: float
    validation_results: List[ValidationResult] = field(default_factory=list)
    data_completeness: float = 0.0
    data_accuracy: float = 0.0
    data_consistency: float = 0.0
    data_timeliness: float = 0.0
    recommendations: List[str] = field(default_factory=list)


class DataValidator:
    """
    Sistema de validação e qualidade de dados para relatórios
    
    Responsabilidades:
    - Validar integridade dos dados coletados
    - Verificar consistência entre métricas
    - Detectar anomalias e outliers
    - Sugerir correções automáticas
    - Gerar relatórios de qualidade
    """
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Configurações de validação
        self.validation_config = self._get_validation_config()
        
        # Cache de dados históricos para comparação
        self.historical_data = {}
        
        # Estatísticas de validação
        self.validation_stats = {
            "total_validations": 0,
            "successful_validations": 0,
            "failed_validations": 0,
            "auto_corrections": 0,
            "quality_scores": []
        }
        
        self.logger.info("Data Validator inicializado")
    
    @handle_errors(severity=ErrorSeverity.MEDIUM, category=ErrorCategory.DATA_COLLECTION)
    async def validate_metrics_data(self, data: Dict[str, Any]) -> DataQualityReport:
        """
        Valida dados de métricas coletados
        
        Args:
            data: Dados de métricas para validação
            
        Returns:
            Relatório de qualidade dos dados
        """
        
        self.logger.info("Iniciando validação de dados de métricas")
        
        validation_results = []
        
        # Validações estruturais
        validation_results.extend(await self._validate_structure(data))
        
        # Validações de tipo e formato
        validation_results.extend(await self._validate_types_and_formats(data))
        
        # Validações de range e limites
        validation_results.extend(await self._validate_ranges(data))
        
        # Validações de consistência
        validation_results.extend(await self._validate_consistency(data))
        
        # Validações de regras de negócio
        validation_results.extend(await self._validate_business_rules(data))
        
        # Validações estatísticas
        validation_results.extend(await self._validate_statistical_patterns(data))
        
        # Validações temporais
        validation_results.extend(await self._validate_temporal_aspects(data))
        
        # Gerar relatório de qualidade
        quality_report = self._generate_quality_report(validation_results, data)
        
        # Atualizar estatísticas
        self._update_validation_stats(quality_report)
        
        # Armazenar dados para comparações futuras
        self._store_historical_data(data)
        
        self.logger.info(f"Validação concluída. Score de qualidade: {quality_report.quality_score:.2f}%")
        
        return quality_report
    
    async def _validate_structure(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Valida estrutura básica dos dados"""
        
        results = []
        required_sections = [
            "system_metrics",
            "session_metrics", 
            "agent_metrics",
            "collaboration_metrics",
            "performance_metrics"
        ]
        
        for section in required_sections:
            if section not in data:
                results.append(ValidationResult(
                    field_name=section,
                    rule_type=ValidationRule.REQUIRED,
                    severity=ValidationSeverity.CRITICAL,
                    is_valid=False,
                    message=f"Seção obrigatória '{section}' não encontrada",
                    suggested_fix=f"Adicionar seção '{section}' aos dados coletados",
                    auto_correctable=False
                ))
            else:
                results.append(ValidationResult(
                    field_name=section,
                    rule_type=ValidationRule.REQUIRED,
                    severity=ValidationSeverity.INFO,
                    is_valid=True,
                    message=f"Seção '{section}' presente"
                ))
        
        return results
    
    async def _validate_types_and_formats(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Valida tipos de dados e formatos"""
        
        results = []
        
        # Definir tipos esperados
        type_expectations = {
            "system_metrics.cpu_usage_percent": (float, int),
            "system_metrics.memory_usage_percent": (float, int),
            "system_metrics.uptime_hours": (float, int),
            "session_metrics.active_sessions": int,
            "session_metrics.success_rate_percent": (float, int),
            "agent_metrics.total_active_agents": int,
            "collaboration_metrics.collaboration_quality_score": (float, int)
        }
        
        for field_path, expected_types in type_expectations.items():
            value = self._get_nested_value(data, field_path)
            
            if value is not None:
                if isinstance(value, expected_types):
                    results.append(ValidationResult(
                        field_name=field_path,
                        rule_type=ValidationRule.TYPE_CHECK,
                        severity=ValidationSeverity.INFO,
                        is_valid=True,
                        message=f"Tipo correto para '{field_path}'"
                    ))
                else:
                    results.append(ValidationResult(
                        field_name=field_path,
                        rule_type=ValidationRule.TYPE_CHECK,
                        severity=ValidationSeverity.HIGH,
                        is_valid=False,
                        message=f"Tipo incorreto para '{field_path}'. Esperado: {expected_types}, Atual: {type(value)}",
                        expected_value=str(expected_types),
                        actual_value=str(type(value)),
                        suggested_fix=f"Converter '{field_path}' para tipo numérico",
                        auto_correctable=True
                    ))
        
        return results
    
    async def _validate_ranges(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Valida ranges e limites dos valores"""
        
        results = []
        
        # Definir ranges esperados
        range_expectations = {
            "system_metrics.cpu_usage_percent": (0, 100),
            "system_metrics.memory_usage_percent": (0, 100),
            "system_metrics.disk_usage_percent": (0, 100),
            "session_metrics.success_rate_percent": (0, 100),
            "session_metrics.active_sessions": (0, 10000),
            "agent_metrics.total_active_agents": (0, 20),
            "collaboration_metrics.collaboration_quality_score": (0, 10),
            "performance_metrics.error_rate_percent": (0, 100)
        }
        
        for field_path, (min_val, max_val) in range_expectations.items():
            value = self._get_nested_value(data, field_path)
            
            if value is not None and isinstance(value, (int, float)):
                if min_val <= value <= max_val:
                    results.append(ValidationResult(
                        field_name=field_path,
                        rule_type=ValidationRule.RANGE_CHECK,
                        severity=ValidationSeverity.INFO,
                        is_valid=True,
                        message=f"Valor dentro do range para '{field_path}'"
                    ))
                else:
                    severity = ValidationSeverity.CRITICAL if value < 0 else ValidationSeverity.HIGH
                    results.append(ValidationResult(
                        field_name=field_path,
                        rule_type=ValidationRule.RANGE_CHECK,
                        severity=severity,
                        is_valid=False,
                        message=f"Valor fora do range para '{field_path}'. Range: [{min_val}, {max_val}], Valor: {value}",
                        expected_value=f"[{min_val}, {max_val}]",
                        actual_value=value,
                        suggested_fix=f"Verificar coleta de dados para '{field_path}'",
                        auto_correctable=False
                    ))
        
        return results
    
    async def _validate_consistency(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Valida consistência entre métricas relacionadas"""
        
        results = []
        
        # Validar consistência entre sessões ativas e total
        active_sessions = self._get_nested_value(data, "session_metrics.active_sessions")
        total_sessions = self._get_nested_value(data, "session_metrics.total_sessions_period")
        
        if active_sessions is not None and total_sessions is not None:
            if active_sessions <= total_sessions:
                results.append(ValidationResult(
                    field_name="session_consistency",
                    rule_type=ValidationRule.CONSISTENCY_CHECK,
                    severity=ValidationSeverity.INFO,
                    is_valid=True,
                    message="Consistência entre sessões ativas e total"
                ))
            else:
                results.append(ValidationResult(
                    field_name="session_consistency",
                    rule_type=ValidationRule.CONSISTENCY_CHECK,
                    severity=ValidationSeverity.HIGH,
                    is_valid=False,
                    message=f"Sessões ativas ({active_sessions}) maior que total ({total_sessions})",
                    suggested_fix="Verificar lógica de contagem de sessões",
                    auto_correctable=False
                ))
        
        # Validar consistência entre sucessos e falhas
        success_rate = self._get_nested_value(data, "session_metrics.success_rate_percent")
        successful_sessions = self._get_nested_value(data, "session_metrics.successful_sessions")
        failed_sessions = self._get_nested_value(data, "session_metrics.failed_sessions")
        
        if all(v is not None for v in [success_rate, successful_sessions, failed_sessions]):
            total_calculated = successful_sessions + failed_sessions
            if total_calculated > 0:
                calculated_rate = (successful_sessions / total_calculated) * 100
                if abs(calculated_rate - success_rate) <= 1:  # Tolerância de 1%
                    results.append(ValidationResult(
                        field_name="success_rate_consistency",
                        rule_type=ValidationRule.CONSISTENCY_CHECK,
                        severity=ValidationSeverity.INFO,
                        is_valid=True,
                        message="Taxa de sucesso consistente com contadores"
                    ))
                else:
                    results.append(ValidationResult(
                        field_name="success_rate_consistency",
                        rule_type=ValidationRule.CONSISTENCY_CHECK,
                        severity=ValidationSeverity.MEDIUM,
                        is_valid=False,
                        message=f"Taxa de sucesso inconsistente. Calculada: {calculated_rate:.1f}%, Reportada: {success_rate}%",
                        suggested_fix="Verificar cálculo da taxa de sucesso",
                        auto_correctable=True
                    ))
        
        return results
    
    async def _validate_business_rules(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Valida regras de negócio específicas"""
        
        results = []
        
        # Regra: Sistema deve ter pelo menos 8 agentes ativos (equipe completa)
        total_agents = self._get_nested_value(data, "agent_metrics.total_active_agents")
        if total_agents is not None:
            if total_agents >= 8:
                results.append(ValidationResult(
                    field_name="agent_count_rule",
                    rule_type=ValidationRule.BUSINESS_RULE,
                    severity=ValidationSeverity.INFO,
                    is_valid=True,
                    message="Equipe completa de agentes ativa"
                ))
            else:
                results.append(ValidationResult(
                    field_name="agent_count_rule",
                    rule_type=ValidationRule.BUSINESS_RULE,
                    severity=ValidationSeverity.HIGH,
                    is_valid=False,
                    message=f"Apenas {total_agents} agentes ativos. Esperado: 8 (equipe completa)",
                    expected_value=8,
                    actual_value=total_agents,
                    suggested_fix="Verificar status dos agentes inativos",
                    auto_correctable=False
                ))
        
        # Regra: Taxa de sucesso deve ser >= 90% para sistema saudável
        success_rate = self._get_nested_value(data, "session_metrics.success_rate_percent")
        if success_rate is not None:
            if success_rate >= 90:
                results.append(ValidationResult(
                    field_name="success_rate_rule",
                    rule_type=ValidationRule.BUSINESS_RULE,
                    severity=ValidationSeverity.INFO,
                    is_valid=True,
                    message="Taxa de sucesso dentro do target"
                ))
            else:
                severity = ValidationSeverity.CRITICAL if success_rate < 80 else ValidationSeverity.HIGH
                results.append(ValidationResult(
                    field_name="success_rate_rule",
                    rule_type=ValidationRule.BUSINESS_RULE,
                    severity=severity,
                    is_valid=False,
                    message=f"Taxa de sucesso abaixo do target. Atual: {success_rate}%, Target: ≥90%",
                    expected_value="≥90%",
                    actual_value=f"{success_rate}%",
                    suggested_fix="Investigar causas de falhas nas sessões",
                    auto_correctable=False
                ))
        
        # Regra: Score de colaboração deve ser >= 8.0
        collab_score = self._get_nested_value(data, "collaboration_metrics.collaboration_quality_score")
        if collab_score is not None:
            if collab_score >= 8.0:
                results.append(ValidationResult(
                    field_name="collaboration_score_rule",
                    rule_type=ValidationRule.BUSINESS_RULE,
                    severity=ValidationSeverity.INFO,
                    is_valid=True,
                    message="Score de colaboração excelente"
                ))
            else:
                results.append(ValidationResult(
                    field_name="collaboration_score_rule",
                    rule_type=ValidationRule.BUSINESS_RULE,
                    severity=ValidationSeverity.MEDIUM,
                    is_valid=False,
                    message=f"Score de colaboração abaixo do ideal. Atual: {collab_score}, Ideal: ≥8.0",
                    expected_value="≥8.0",
                    actual_value=collab_score,
                    suggested_fix="Analisar dinâmica de colaboração entre agentes",
                    auto_correctable=False
                ))
        
        return results
    
    async def _validate_statistical_patterns(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Valida padrões estatísticos e detecta anomalias"""
        
        results = []
        
        # Comparar com dados históricos se disponíveis
        if self.historical_data:
            results.extend(await self._detect_anomalies(data))
        
        # Validar distribuições esperadas
        agent_metrics = data.get("agent_metrics", {}).get("agent_details", {})
        if agent_metrics:
            participation_rates = [
                metrics.get("participation_rate", 0) 
                for metrics in agent_metrics.values()
            ]
            
            if participation_rates:
                avg_participation = statistics.mean(participation_rates)
                std_participation = statistics.stdev(participation_rates) if len(participation_rates) > 1 else 0
                
                # Verificar se há agentes com participação muito baixa
                outliers = [rate for rate in participation_rates if rate < avg_participation - 2 * std_participation]
                
                if not outliers:
                    results.append(ValidationResult(
                        field_name="agent_participation_distribution",
                        rule_type=ValidationRule.STATISTICAL_CHECK,
                        severity=ValidationSeverity.INFO,
                        is_valid=True,
                        message="Distribuição de participação dos agentes normal"
                    ))
                else:
                    results.append(ValidationResult(
                        field_name="agent_participation_distribution",
                        rule_type=ValidationRule.STATISTICAL_CHECK,
                        severity=ValidationSeverity.MEDIUM,
                        is_valid=False,
                        message=f"Detectados {len(outliers)} agentes com participação anormalmente baixa",
                        suggested_fix="Investigar agentes com baixa participação",
                        auto_correctable=False
                    ))
        
        return results
    
    async def _validate_temporal_aspects(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Valida aspectos temporais dos dados"""
        
        results = []
        
        # Verificar se dados são recentes (coletados nas últimas 2 horas)
        collection_time = data.get("collection_timestamp")
        if collection_time:
            try:
                if isinstance(collection_time, str):
                    collection_dt = datetime.fromisoformat(collection_time.replace('Z', '+00:00'))
                else:
                    collection_dt = collection_time
                
                age_hours = (datetime.utcnow() - collection_dt.replace(tzinfo=None)).total_seconds() / 3600
                
                if age_hours <= 2:
                    results.append(ValidationResult(
                        field_name="data_freshness",
                        rule_type=ValidationRule.TEMPORAL_CHECK,
                        severity=ValidationSeverity.INFO,
                        is_valid=True,
                        message="Dados recentes e atualizados"
                    ))
                else:
                    severity = ValidationSeverity.HIGH if age_hours > 24 else ValidationSeverity.MEDIUM
                    results.append(ValidationResult(
                        field_name="data_freshness",
                        rule_type=ValidationRule.TEMPORAL_CHECK,
                        severity=severity,
                        is_valid=False,
                        message=f"Dados desatualizados. Idade: {age_hours:.1f} horas",
                        suggested_fix="Verificar processo de coleta de dados",
                        auto_correctable=False
                    ))
            except Exception as e:
                results.append(ValidationResult(
                    field_name="data_freshness",
                    rule_type=ValidationRule.TEMPORAL_CHECK,
                    severity=ValidationSeverity.MEDIUM,
                    is_valid=False,
                    message=f"Erro ao validar timestamp: {e}",
                    suggested_fix="Verificar formato do timestamp",
                    auto_correctable=False
                ))
        
        return results
    
    async def _detect_anomalies(self, data: Dict[str, Any]) -> List[ValidationResult]:
        """Detecta anomalias comparando com dados históricos"""
        
        results = []
        
        # Campos para comparação histórica
        comparison_fields = [
            "session_metrics.active_sessions",
            "session_metrics.success_rate_percent",
            "system_metrics.cpu_usage_percent",
            "system_metrics.memory_usage_percent",
            "agent_metrics.avg_response_time"
        ]
        
        for field_path in comparison_fields:
            current_value = self._get_nested_value(data, field_path)
            historical_values = self.historical_data.get(field_path, [])
            
            if current_value is not None and len(historical_values) >= 5:
                avg_historical = statistics.mean(historical_values)
                std_historical = statistics.stdev(historical_values) if len(historical_values) > 1 else 0
                
                # Detectar outliers (valores fora de 2 desvios padrão)
                if std_historical > 0:
                    z_score = abs(current_value - avg_historical) / std_historical
                    
                    if z_score <= 2:
                        results.append(ValidationResult(
                            field_name=f"{field_path}_anomaly",
                            rule_type=ValidationRule.STATISTICAL_CHECK,
                            severity=ValidationSeverity.INFO,
                            is_valid=True,
                            message=f"Valor normal para '{field_path}'"
                        ))
                    else:
                        severity = ValidationSeverity.HIGH if z_score > 3 else ValidationSeverity.MEDIUM
                        results.append(ValidationResult(
                            field_name=f"{field_path}_anomaly",
                            rule_type=ValidationRule.STATISTICAL_CHECK,
                            severity=severity,
                            is_valid=False,
                            message=f"Anomalia detectada em '{field_path}'. Z-score: {z_score:.2f}",
                            expected_value=f"~{avg_historical:.2f}",
                            actual_value=current_value,
                            suggested_fix=f"Investigar causa da variação em '{field_path}'",
                            auto_correctable=False
                        ))
        
        return results
    
    def _generate_quality_report(
        self, 
        validation_results: List[ValidationResult], 
        data: Dict[str, Any]
    ) -> DataQualityReport:
        """Gera relatório de qualidade dos dados"""
        
        total_validations = len(validation_results)
        passed_validations = len([r for r in validation_results if r.is_valid])
        failed_validations = total_validations - passed_validations
        
        # Calcular score de qualidade (0-100)
        if total_validations == 0:
            quality_score = 100.0
        else:
            base_score = (passed_validations / total_validations) * 100
            
            # Penalizar por severidade dos erros
            severity_penalties = {
                ValidationSeverity.CRITICAL: 20,
                ValidationSeverity.HIGH: 10,
                ValidationSeverity.MEDIUM: 5,
                ValidationSeverity.LOW: 2
            }
            
            total_penalty = 0
            for result in validation_results:
                if not result.is_valid:
                    total_penalty += severity_penalties.get(result.severity, 0)
            
            quality_score = max(0, base_score - total_penalty)
        
        # Calcular métricas específicas de qualidade
        completeness = self._calculate_completeness(data)
        accuracy = self._calculate_accuracy(validation_results)
        consistency = self._calculate_consistency(validation_results)
        timeliness = self._calculate_timeliness(data)
        
        # Gerar recomendações
        recommendations = self._generate_recommendations(validation_results)
        
        return DataQualityReport(
            timestamp=datetime.utcnow(),
            total_validations=total_validations,
            passed_validations=passed_validations,
            failed_validations=failed_validations,
            quality_score=quality_score,
            validation_results=validation_results,
            data_completeness=completeness,
            data_accuracy=accuracy,
            data_consistency=consistency,
            data_timeliness=timeliness,
            recommendations=recommendations
        )
    
    def _calculate_completeness(self, data: Dict[str, Any]) -> float:
        """Calcula score de completude dos dados"""
        
        required_fields = [
            "system_metrics.cpu_usage_percent",
            "system_metrics.memory_usage_percent",
            "session_metrics.active_sessions",
            "session_metrics.success_rate_percent",
            "agent_metrics.total_active_agents",
            "collaboration_metrics.collaboration_quality_score"
        ]
        
        present_fields = 0
        for field_path in required_fields:
            if self._get_nested_value(data, field_path) is not None:
                present_fields += 1
        
        return (present_fields / len(required_fields)) * 100
    
    def _calculate_accuracy(self, validation_results: List[ValidationResult]) -> float:
        """Calcula score de precisão dos dados"""
        
        accuracy_validations = [
            r for r in validation_results 
            if r.rule_type in [ValidationRule.TYPE_CHECK, ValidationRule.RANGE_CHECK, ValidationRule.FORMAT_CHECK]
        ]
        
        if not accuracy_validations:
            return 100.0
        
        passed_accuracy = len([r for r in accuracy_validations if r.is_valid])
        return (passed_accuracy / len(accuracy_validations)) * 100
    
    def _calculate_consistency(self, validation_results: List[ValidationResult]) -> float:
        """Calcula score de consistência dos dados"""
        
        consistency_validations = [
            r for r in validation_results 
            if r.rule_type == ValidationRule.CONSISTENCY_CHECK
        ]
        
        if not consistency_validations:
            return 100.0
        
        passed_consistency = len([r for r in consistency_validations if r.is_valid])
        return (passed_consistency / len(consistency_validations)) * 100
    
    def _calculate_timeliness(self, data: Dict[str, Any]) -> float:
        """Calcula score de atualidade dos dados"""
        
        collection_time = data.get("collection_timestamp")
        if not collection_time:
            return 50.0  # Score neutro se não há timestamp
        
        try:
            if isinstance(collection_time, str):
                collection_dt = datetime.fromisoformat(collection_time.replace('Z', '+00:00'))
            else:
                collection_dt = collection_time
            
            age_hours = (datetime.utcnow() - collection_dt.replace(tzinfo=None)).total_seconds() / 3600
            
            # Score baseado na idade dos dados
            if age_hours <= 1:
                return 100.0
            elif age_hours <= 6:
                return 90.0
            elif age_hours <= 24:
                return 70.0
            else:
                return max(0, 50 - (age_hours - 24) * 2)
                
        except Exception:
            return 50.0
    
    def _generate_recommendations(self, validation_results: List[ValidationResult]) -> List[str]:
        """Gera recomendações baseadas nos resultados de validação"""
        
        recommendations = []
        
        # Agrupar erros por tipo
        error_counts = {}
        for result in validation_results:
            if not result.is_valid:
                error_counts[result.rule_type] = error_counts.get(result.rule_type, 0) + 1
        
        # Gerar recomendações baseadas nos tipos de erro mais comuns
        if error_counts.get(ValidationRule.RANGE_CHECK, 0) > 2:
            recommendations.append("Revisar limites e ranges das métricas coletadas")
        
        if error_counts.get(ValidationRule.CONSISTENCY_CHECK, 0) > 1:
            recommendations.append("Verificar lógica de cálculo entre métricas relacionadas")
        
        if error_counts.get(ValidationRule.BUSINESS_RULE, 0) > 0:
            recommendations.append("Investigar violações de regras de negócio")
        
        if error_counts.get(ValidationRule.STATISTICAL_CHECK, 0) > 0:
            recommendations.append("Analisar anomalias detectadas nos padrões de dados")
        
        # Recomendações específicas para erros críticos
        critical_errors = [r for r in validation_results if r.severity == ValidationSeverity.CRITICAL and not r.is_valid]
        if critical_errors:
            recommendations.append("URGENTE: Corrigir erros críticos antes de gerar relatórios")
        
        return recommendations
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Obtém valor de campo aninhado usando notação de ponto"""
        
        try:
            keys = field_path.split('.')
            value = data
            
            for key in keys:
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    return None
            
            return value
            
        except Exception:
            return None
    
    def _store_historical_data(self, data: Dict[str, Any]):
        """Armazena dados para comparações históricas"""
        
        fields_to_store = [
            "session_metrics.active_sessions",
            "session_metrics.success_rate_percent",
            "system_metrics.cpu_usage_percent",
            "system_metrics.memory_usage_percent",
            "agent_metrics.avg_response_time"
        ]
        
        for field_path in fields_to_store:
            value = self._get_nested_value(data, field_path)
            if value is not None and isinstance(value, (int, float)):
                if field_path not in self.historical_data:
                    self.historical_data[field_path] = []
                
                self.historical_data[field_path].append(value)
                
                # Manter apenas últimos 100 valores
                if len(self.historical_data[field_path]) > 100:
                    self.historical_data[field_path] = self.historical_data[field_path][-100:]
    
    def _update_validation_stats(self, quality_report: DataQualityReport):
        """Atualiza estatísticas de validação"""
        
        self.validation_stats["total_validations"] += quality_report.total_validations
        self.validation_stats["successful_validations"] += quality_report.passed_validations
        self.validation_stats["failed_validations"] += quality_report.failed_validations
        
        # Contar correções automáticas
        auto_corrections = len([
            r for r in quality_report.validation_results 
            if not r.is_valid and r.auto_correctable
        ])
        self.validation_stats["auto_corrections"] += auto_corrections
        
        # Armazenar scores de qualidade
        self.validation_stats["quality_scores"].append(quality_report.quality_score)
        
        # Manter apenas últimos 50 scores
        if len(self.validation_stats["quality_scores"]) > 50:
            self.validation_stats["quality_scores"] = self.validation_stats["quality_scores"][-50:]
    
    def _get_validation_config(self) -> Dict[str, Any]:
        """Obtém configurações de validação"""
        
        return {
            "enable_statistical_validation": True,
            "enable_business_rules": True,
            "anomaly_detection_threshold": 2.0,  # Z-score threshold
            "data_freshness_hours": 2,
            "quality_score_threshold": 80.0,
            "auto_correction_enabled": True
        }
    
    async def auto_correct_data(self, data: Dict[str, Any], validation_results: List[ValidationResult]) -> Dict[str, Any]:
        """Aplica correções automáticas nos dados quando possível"""
        
        corrected_data = data.copy()
        corrections_applied = 0
        
        for result in validation_results:
            if not result.is_valid and result.auto_correctable:
                try:
                    if result.rule_type == ValidationRule.TYPE_CHECK:
                        # Tentar converter tipo
                        value = self._get_nested_value(corrected_data, result.field_name)
                        if value is not None:
                            corrected_value = self._convert_to_numeric(value)
                            if corrected_value is not None:
                                self._set_nested_value(corrected_data, result.field_name, corrected_value)
                                corrections_applied += 1
                    
                    elif result.rule_type == ValidationRule.CONSISTENCY_CHECK:
                        # Recalcular valores inconsistentes
                        if "success_rate" in result.field_name:
                            corrected_data = self._recalculate_success_rate(corrected_data)
                            corrections_applied += 1
                    
                except Exception as e:
                    self.logger.warning(f"Falha na correção automática de {result.field_name}: {e}")
        
        if corrections_applied > 0:
            self.logger.info(f"Aplicadas {corrections_applied} correções automáticas")
        
        return corrected_data
    
    def _convert_to_numeric(self, value: Any) -> Optional[Union[int, float]]:
        """Converte valor para numérico"""
        
        try:
            if isinstance(value, str):
                # Remover caracteres não numéricos
                clean_value = re.sub(r'[^\d.-]', '', value)
                if '.' in clean_value:
                    return float(clean_value)
                else:
                    return int(clean_value)
            return None
        except Exception:
            return None
    
    def _set_nested_value(self, data: Dict[str, Any], field_path: str, value: Any):
        """Define valor de campo aninhado"""
        
        keys = field_path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
    
    def _recalculate_success_rate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recalcula taxa de sucesso baseada nos contadores"""
        
        successful = self._get_nested_value(data, "session_metrics.successful_sessions")
        failed = self._get_nested_value(data, "session_metrics.failed_sessions")
        
        if successful is not None and failed is not None:
            total = successful + failed
            if total > 0:
                success_rate = (successful / total) * 100
                self._set_nested_value(data, "session_metrics.success_rate_percent", success_rate)
        
        return data
    
    def get_validation_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas de validação"""
        
        stats = self.validation_stats.copy()
        
        if stats["quality_scores"]:
            stats["avg_quality_score"] = statistics.mean(stats["quality_scores"])
            stats["min_quality_score"] = min(stats["quality_scores"])
            stats["max_quality_score"] = max(stats["quality_scores"])
        
        if stats["total_validations"] > 0:
            stats["success_rate"] = (stats["successful_validations"] / stats["total_validations"]) * 100
        
        return stats
    
    def get_data_quality_summary(self) -> Dict[str, Any]:
        """Retorna resumo da qualidade dos dados para relatórios"""
        
        stats = self.get_validation_statistics()
        
        return {
            "overall_quality_score": stats.get("avg_quality_score", 0),
            "validation_success_rate": stats.get("success_rate", 0),
            "total_validations_performed": stats.get("total_validations", 0),
            "auto_corrections_applied": stats.get("auto_corrections", 0),
            "data_quality_trend": self._get_quality_trend(),
            "last_validation": datetime.utcnow().isoformat()
        }
    
    def _get_quality_trend(self) -> str:
        """Analisa tendência da qualidade dos dados"""
        
        scores = self.validation_stats.get("quality_scores", [])
        
        if len(scores) < 5:
            return "insufficient_data"
        
        recent_scores = scores[-5:]
        older_scores = scores[-10:-5] if len(scores) >= 10 else scores[:-5]
        
        if not older_scores:
            return "stable"
        
        recent_avg = statistics.mean(recent_scores)
        older_avg = statistics.mean(older_scores)
        
        if recent_avg > older_avg + 5:
            return "improving"
        elif recent_avg < older_avg - 5:
            return "declining"
        else:
            return "stable"


# Instância global do validador
data_validator = DataValidator()