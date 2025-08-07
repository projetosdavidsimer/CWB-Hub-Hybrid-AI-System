#!/usr/bin/env python3
"""
Cost Monitor - Sistema de monitoramento de custos LLM
Melhoria #6 - Integração com Modelos de Linguagem
"""

import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import asyncio

logger = logging.getLogger(__name__)


@dataclass
class CostEntry:
    """Entrada de custo"""
    timestamp: float
    model: str
    provider: str
    tokens_used: int
    cost: float
    agent_id: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class CostAlert:
    """Alerta de custo"""
    alert_type: str  # daily, weekly, monthly, model_specific
    threshold: float
    current_amount: float
    triggered_at: float
    message: str


class CostMonitor:
    """Monitor de custos para LLMs"""
    
    def __init__(self):
        self.cost_entries: List[CostEntry] = []
        self.alerts: List[CostAlert] = []
        
        # Configurações de alerta
        self.alert_thresholds = {
            "daily": 50.0,      # $50/dia
            "weekly": 300.0,    # $300/semana
            "monthly": 1000.0,  # $1000/mês
            "per_request": 5.0  # $5 por requisição
        }
        
        # Limites por modelo
        self.model_limits = {
            "gpt-4": {"daily": 100.0, "per_request": 2.0},
            "gpt-4o": {"daily": 50.0, "per_request": 1.0},
            "claude-3-5-sonnet-20240620": {"daily": 75.0, "per_request": 1.5},
            "gemini-pro": {"daily": 25.0, "per_request": 0.5}
        }
        
        # Estatísticas
        self.stats = {
            "total_cost": 0.0,
            "total_tokens": 0,
            "total_requests": 0,
            "cost_by_provider": {},
            "cost_by_model": {},
            "cost_by_agent": {},
            "alerts_triggered": 0
        }
        
        # Última limpeza de dados antigos
        self.last_cleanup = time.time()
    
    async def track_usage(
        self,
        model: str,
        tokens_used: int,
        cost: float,
        agent_id: Optional[str] = None,
        session_id: Optional[str] = None
    ):
        """Registra uso e custo"""
        # Determinar provedor baseado no modelo
        provider = self._get_provider_from_model(model)
        
        # Criar entrada
        entry = CostEntry(
            timestamp=time.time(),
            model=model,
            provider=provider,
            tokens_used=tokens_used,
            cost=cost,
            agent_id=agent_id,
            session_id=session_id
        )
        
        self.cost_entries.append(entry)
        
        # Atualizar estatísticas
        await self._update_stats(entry)
        
        # Verificar alertas
        await self._check_alerts(entry)
        
        # Limpeza periódica
        await self._periodic_cleanup()
        
        logger.debug(f"💰 Custo registrado: {model} - ${cost:.4f} ({tokens_used} tokens)")
    
    def _get_provider_from_model(self, model: str) -> str:
        """Determina provedor baseado no nome do modelo"""
        if model.startswith("gpt"):
            return "openai"
        elif model.startswith("claude"):
            return "anthropic"
        elif model.startswith("gemini"):
            return "gemini"
        else:
            return "unknown"
    
    async def _update_stats(self, entry: CostEntry):
        """Atualiza estatísticas"""
        self.stats["total_cost"] += entry.cost
        self.stats["total_tokens"] += entry.tokens_used
        self.stats["total_requests"] += 1
        
        # Por provedor
        if entry.provider not in self.stats["cost_by_provider"]:
            self.stats["cost_by_provider"][entry.provider] = 0.0
        self.stats["cost_by_provider"][entry.provider] += entry.cost
        
        # Por modelo
        if entry.model not in self.stats["cost_by_model"]:
            self.stats["cost_by_model"][entry.model] = 0.0
        self.stats["cost_by_model"][entry.model] += entry.cost
        
        # Por agente
        if entry.agent_id:
            if entry.agent_id not in self.stats["cost_by_agent"]:
                self.stats["cost_by_agent"][entry.agent_id] = 0.0
            self.stats["cost_by_agent"][entry.agent_id] += entry.cost
    
    async def _check_alerts(self, entry: CostEntry):
        """Verifica se algum alerta deve ser disparado"""
        current_time = time.time()
        
        # Verificar alerta por requisição
        if entry.cost > self.alert_thresholds["per_request"]:
            alert = CostAlert(
                alert_type="per_request",
                threshold=self.alert_thresholds["per_request"],
                current_amount=entry.cost,
                triggered_at=current_time,
                message=f"Requisição custosa: ${entry.cost:.2f} com {entry.model}"
            )
            await self._trigger_alert(alert)
        
        # Verificar alertas diários
        daily_cost = await self.get_cost_for_period("day")
        if daily_cost > self.alert_thresholds["daily"]:
            alert = CostAlert(
                alert_type="daily",
                threshold=self.alert_thresholds["daily"],
                current_amount=daily_cost,
                triggered_at=current_time,
                message=f"Limite diário excedido: ${daily_cost:.2f}"
            )
            await self._trigger_alert(alert)
        
        # Verificar alertas semanais
        weekly_cost = await self.get_cost_for_period("week")
        if weekly_cost > self.alert_thresholds["weekly"]:
            alert = CostAlert(
                alert_type="weekly",
                threshold=self.alert_thresholds["weekly"],
                current_amount=weekly_cost,
                triggered_at=current_time,
                message=f"Limite semanal excedido: ${weekly_cost:.2f}"
            )
            await self._trigger_alert(alert)
        
        # Verificar alertas mensais
        monthly_cost = await self.get_cost_for_period("month")
        if monthly_cost > self.alert_thresholds["monthly"]:
            alert = CostAlert(
                alert_type="monthly",
                threshold=self.alert_thresholds["monthly"],
                current_amount=monthly_cost,
                triggered_at=current_time,
                message=f"Limite mensal excedido: ${monthly_cost:.2f}"
            )
            await self._trigger_alert(alert)
    
    async def _trigger_alert(self, alert: CostAlert):
        """Dispara um alerta"""
        # Verificar se alerta similar já foi disparado recentemente
        recent_alerts = [
            a for a in self.alerts
            if a.alert_type == alert.alert_type and 
               alert.triggered_at - a.triggered_at < 3600  # 1 hora
        ]
        
        if recent_alerts:
            return  # Não disparar alerta duplicado
        
        self.alerts.append(alert)
        self.stats["alerts_triggered"] += 1
        
        logger.warning(f"🚨 ALERTA DE CUSTO: {alert.message}")
        
        # Aqui você pode adicionar integração com sistemas de notificação
        # como email, Slack, webhooks, etc.
    
    async def get_cost_for_period(self, period: str, model: Optional[str] = None) -> float:
        """Calcula custo para um período específico"""
        current_time = time.time()
        
        # Definir início do período
        if period == "day":
            start_time = current_time - (24 * 3600)
        elif period == "week":
            start_time = current_time - (7 * 24 * 3600)
        elif period == "month":
            start_time = current_time - (30 * 24 * 3600)
        else:
            start_time = 0  # Todo o período
        
        # Filtrar entradas
        filtered_entries = [
            entry for entry in self.cost_entries
            if entry.timestamp >= start_time and
               (model is None or entry.model == model)
        ]
        
        return sum(entry.cost for entry in filtered_entries)
    
    async def get_cost_summary(self) -> Dict[str, Any]:
        """Retorna resumo de custos"""
        current_time = time.time()
        
        return {
            "total_cost": self.stats["total_cost"],
            "total_tokens": self.stats["total_tokens"],
            "total_requests": self.stats["total_requests"],
            "average_cost_per_request": (
                self.stats["total_cost"] / max(self.stats["total_requests"], 1)
            ),
            "cost_by_provider": self.stats["cost_by_provider"],
            "cost_by_model": self.stats["cost_by_model"],
            "cost_by_agent": self.stats["cost_by_agent"],
            "daily_cost": await self.get_cost_for_period("day"),
            "weekly_cost": await self.get_cost_for_period("week"),
            "monthly_cost": await self.get_cost_for_period("month"),
            "alerts_triggered": self.stats["alerts_triggered"],
            "recent_alerts": len([
                a for a in self.alerts
                if current_time - a.triggered_at < 3600
            ])
        }
    
    async def get_cost_breakdown(self, period: str = "day") -> Dict[str, Any]:
        """Retorna breakdown detalhado de custos"""
        current_time = time.time()
        
        # Definir período
        if period == "day":
            start_time = current_time - (24 * 3600)
            hours = 24
        elif period == "week":
            start_time = current_time - (7 * 24 * 3600)
            hours = 7 * 24
        else:
            start_time = current_time - (30 * 24 * 3600)
            hours = 30 * 24
        
        # Filtrar entradas do período
        period_entries = [
            entry for entry in self.cost_entries
            if entry.timestamp >= start_time
        ]
        
        # Agrupar por hora
        hourly_costs = {}
        for entry in period_entries:
            hour = int((entry.timestamp - start_time) // 3600)
            if hour not in hourly_costs:
                hourly_costs[hour] = 0.0
            hourly_costs[hour] += entry.cost
        
        # Top modelos por custo
        model_costs = {}
        for entry in period_entries:
            if entry.model not in model_costs:
                model_costs[entry.model] = 0.0
            model_costs[entry.model] += entry.cost
        
        top_models = sorted(
            model_costs.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # Top agentes por custo
        agent_costs = {}
        for entry in period_entries:
            if entry.agent_id:
                if entry.agent_id not in agent_costs:
                    agent_costs[entry.agent_id] = 0.0
                agent_costs[entry.agent_id] += entry.cost
        
        top_agents = sorted(
            agent_costs.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        return {
            "period": period,
            "total_cost": sum(entry.cost for entry in period_entries),
            "total_requests": len(period_entries),
            "hourly_costs": hourly_costs,
            "top_models": top_models,
            "top_agents": top_agents,
            "cost_trend": self._calculate_trend(period_entries)
        }
    
    def _calculate_trend(self, entries: List[CostEntry]) -> str:
        """Calcula tendência de custo"""
        if len(entries) < 2:
            return "insufficient_data"
        
        # Dividir em duas metades
        mid_point = len(entries) // 2
        first_half = entries[:mid_point]
        second_half = entries[mid_point:]
        
        first_half_cost = sum(e.cost for e in first_half)
        second_half_cost = sum(e.cost for e in second_half)
        
        if second_half_cost > first_half_cost * 1.1:
            return "increasing"
        elif second_half_cost < first_half_cost * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    async def set_alert_threshold(self, alert_type: str, threshold: float):
        """Define limite de alerta"""
        if alert_type in self.alert_thresholds:
            self.alert_thresholds[alert_type] = threshold
            logger.info(f"🔔 Limite de alerta atualizado: {alert_type} = ${threshold}")
        else:
            logger.warning(f"⚠️ Tipo de alerta inválido: {alert_type}")
    
    async def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Retorna alertas recentes"""
        current_time = time.time()
        cutoff_time = current_time - (hours * 3600)
        
        recent_alerts = [
            {
                "alert_type": alert.alert_type,
                "threshold": alert.threshold,
                "current_amount": alert.current_amount,
                "triggered_at": alert.triggered_at,
                "message": alert.message,
                "hours_ago": (current_time - alert.triggered_at) / 3600
            }
            for alert in self.alerts
            if alert.triggered_at >= cutoff_time
        ]
        
        return sorted(recent_alerts, key=lambda x: x["triggered_at"], reverse=True)
    
    async def _periodic_cleanup(self):
        """Limpeza periódica de dados antigos"""
        current_time = time.time()
        
        # Limpar a cada 6 horas
        if current_time - self.last_cleanup < 6 * 3600:
            return
        
        # Manter apenas dados dos últimos 90 dias
        cutoff_time = current_time - (90 * 24 * 3600)
        
        # Limpar entradas antigas
        old_count = len(self.cost_entries)
        self.cost_entries = [
            entry for entry in self.cost_entries
            if entry.timestamp >= cutoff_time
        ]
        
        # Limpar alertas antigos (manter 30 dias)
        alert_cutoff = current_time - (30 * 24 * 3600)
        old_alert_count = len(self.alerts)
        self.alerts = [
            alert for alert in self.alerts
            if alert.triggered_at >= alert_cutoff
        ]
        
        removed_entries = old_count - len(self.cost_entries)
        removed_alerts = old_alert_count - len(self.alerts)
        
        if removed_entries > 0 or removed_alerts > 0:
            logger.info(
                f"🧹 Limpeza de dados: {removed_entries} entradas e "
                f"{removed_alerts} alertas removidos"
            )
        
        self.last_cleanup = current_time
    
    async def export_cost_data(self, format: str = "json") -> str:
        """Exporta dados de custo"""
        data = {
            "export_timestamp": time.time(),
            "summary": await self.get_cost_summary(),
            "entries": [asdict(entry) for entry in self.cost_entries],
            "alerts": [asdict(alert) for alert in self.alerts],
            "thresholds": self.alert_thresholds
        }
        
        if format == "json":
            return json.dumps(data, indent=2)
        else:
            # Adicionar outros formatos se necessário (CSV, Excel, etc.)
            return json.dumps(data, indent=2)