"""
Report Scheduler - Sistema de Agendamento de Relatórios
Criado pela Equipe Híbrida CWB Hub

Mariana Rodrigues (DevOps): "Vamos automatizar completamente a geração de 
relatórios com um sistema de agendamento robusto e confiável."

Pedro Henrique Almeida (PM): "Com controle total sobre frequências, 
horários e distribuição automática."
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
import json
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from .report_engine import ReportEngine
from ..models.report_models import ReportType, ReportFormat, ReportFrequency

logger = logging.getLogger(__name__)


class ReportScheduler:
    """
    Sistema de agendamento automático de relatórios
    
    Responsabilidades:
    - Agendar geração automática de relatórios
    - Gerenciar frequências e horários
    - Executar relatórios em background
    - Notificar sobre sucessos e falhas
    """
    
    def __init__(
        self, 
        report_engine: Optional[ReportEngine] = None,
        config_file: Optional[Path] = None
    ):
        self.report_engine = report_engine or ReportEngine()
        
        if config_file is None:
            config_file = Path(__file__).parent.parent / "config" / "schedule_configs.json"
        
        self.config_file = config_file
        self.config_file.parent.mkdir(exist_ok=True)
        
        # Configurar APScheduler
        jobstores = {
            'default': MemoryJobStore()
        }
        executors = {
            'default': AsyncIOExecutor()
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 3,
            'misfire_grace_time': 300  # 5 minutos
        }
        
        self.scheduler = AsyncIOScheduler(
            jobstores=jobstores,
            executors=executors,
            job_defaults=job_defaults,
            timezone='America/Sao_Paulo'
        )
        
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Cache de configurações de agendamento
        self.schedule_configs: Dict[str, Dict[str, Any]] = {}
        
        # Callbacks para notificações
        self.success_callbacks: List[Callable] = []
        self.error_callbacks: List[Callable] = []
        
        # Carregar configurações padrão
        self._load_default_schedules()
    
    async def start(self):
        """Inicia o scheduler"""
        try:
            self.scheduler.start()
            self.logger.info("Scheduler de relatórios iniciado com sucesso")
            
            # Carregar agendamentos salvos
            await self._load_saved_schedules()
            
        except Exception as e:
            self.logger.error(f"Erro ao iniciar scheduler: {e}")
            raise
    
    async def stop(self):
        """Para o scheduler"""
        try:
            self.scheduler.shutdown(wait=True)
            self.logger.info("Scheduler de relatórios parado")
        except Exception as e:
            self.logger.error(f"Erro ao parar scheduler: {e}")
    
    async def schedule_report(
        self,
        schedule_id: str,
        report_type: ReportType,
        frequency: ReportFrequency,
        output_formats: List[ReportFormat] = None,
        cron_expression: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        recipients: Optional[List[str]] = None,
        is_active: bool = True
    ) -> bool:
        """
        Agenda um relatório para geração automática
        
        Args:
            schedule_id: ID único do agendamento
            report_type: Tipo do relatório
            frequency: Frequência de geração
            output_formats: Formatos de saída
            cron_expression: Expressão cron customizada
            parameters: Parâmetros do relatório
            recipients: Lista de emails para envio
            is_active: Se o agendamento está ativo
            
        Returns:
            True se agendado com sucesso
        """
        try:
            if output_formats is None:
                output_formats = [ReportFormat.HTML]
            
            if parameters is None:
                parameters = {}
            
            if recipients is None:
                recipients = []
            
            # Configuração do agendamento
            schedule_config = {
                "schedule_id": schedule_id,
                "report_type": report_type,
                "frequency": frequency,
                "output_formats": output_formats,
                "cron_expression": cron_expression,
                "parameters": parameters,
                "recipients": recipients,
                "is_active": is_active,
                "created_at": datetime.utcnow().isoformat(),
                "last_run": None,
                "next_run": None,
                "run_count": 0,
                "success_count": 0,
                "error_count": 0
            }
            
            # Determinar trigger baseado na frequência
            trigger = self._create_trigger(frequency, cron_expression)
            
            if not trigger:
                self.logger.error(f"Não foi possível criar trigger para frequência: {frequency}")
                return False
            
            # Agendar job
            job = self.scheduler.add_job(
                func=self._execute_scheduled_report,
                trigger=trigger,
                args=[schedule_config],
                id=schedule_id,
                name=f"Relatório {report_type.value}",
                replace_existing=True
            )
            
            # Atualizar próxima execução
            if job.next_run_time:
                schedule_config["next_run"] = job.next_run_time.isoformat()
            
            # Salvar configuração
            self.schedule_configs[schedule_id] = schedule_config
            await self._save_schedules()
            
            self.logger.info(f"Relatório agendado: {schedule_id} ({frequency.value})")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao agendar relatório {schedule_id}: {e}")
            return False
    
    def _create_trigger(
        self, 
        frequency: ReportFrequency, 
        cron_expression: Optional[str] = None
    ):
        """Cria trigger baseado na frequência"""
        
        if cron_expression:
            # Usar expressão cron customizada
            return CronTrigger.from_crontab(cron_expression)
        
        if frequency == ReportFrequency.REAL_TIME:
            # A cada 5 minutos para "tempo real"
            return IntervalTrigger(minutes=5)
        
        elif frequency == ReportFrequency.HOURLY:
            # A cada hora no minuto 0
            return CronTrigger(minute=0)
        
        elif frequency == ReportFrequency.DAILY:
            # Diariamente às 08:00
            return CronTrigger(hour=8, minute=0)
        
        elif frequency == ReportFrequency.WEEKLY:
            # Segundas-feiras às 08:00
            return CronTrigger(day_of_week='mon', hour=8, minute=0)
        
        elif frequency == ReportFrequency.MONTHLY:
            # Primeiro dia do mês às 08:00
            return CronTrigger(day=1, hour=8, minute=0)
        
        else:
            return None
    
    async def _execute_scheduled_report(self, schedule_config: Dict[str, Any]):
        """Executa um relatório agendado"""
        schedule_id = schedule_config["schedule_id"]
        
        try:
            self.logger.info(f"Executando relatório agendado: {schedule_id}")
            
            # Atualizar estatísticas
            schedule_config["run_count"] += 1
            schedule_config["last_run"] = datetime.utcnow().isoformat()
            
            # Gerar relatório
            result = await self.report_engine.generate_report(
                report_type=schedule_config["report_type"],
                output_formats=schedule_config["output_formats"],
                parameters=schedule_config["parameters"]
            )
            
            if result.status.value == "completed":
                schedule_config["success_count"] += 1
                self.logger.info(f"Relatório agendado executado com sucesso: {schedule_id}")
                
                # Notificar sucesso
                await self._notify_success(schedule_config, result)
                
            else:
                schedule_config["error_count"] += 1
                self.logger.error(f"Falha na execução do relatório agendado: {schedule_id}")
                
                # Notificar erro
                await self._notify_error(schedule_config, result.error_message)
            
            # Salvar estatísticas atualizadas
            self.schedule_configs[schedule_id] = schedule_config
            await self._save_schedules()
            
        except Exception as e:
            self.logger.error(f"Erro na execução do relatório agendado {schedule_id}: {e}")
            
            schedule_config["error_count"] += 1
            self.schedule_configs[schedule_id] = schedule_config
            
            await self._notify_error(schedule_config, str(e))
    
    async def _notify_success(
        self, 
        schedule_config: Dict[str, Any], 
        result: Any
    ):
        """Notifica sucesso na execução"""
        try:
            for callback in self.success_callbacks:
                await callback(schedule_config, result)
        except Exception as e:
            self.logger.error(f"Erro ao notificar sucesso: {e}")
    
    async def _notify_error(
        self, 
        schedule_config: Dict[str, Any], 
        error_message: str
    ):
        """Notifica erro na execução"""
        try:
            for callback in self.error_callbacks:
                await callback(schedule_config, error_message)
        except Exception as e:
            self.logger.error(f"Erro ao notificar erro: {e}")
    
    def add_success_callback(self, callback: Callable):
        """Adiciona callback para notificação de sucesso"""
        self.success_callbacks.append(callback)
    
    def add_error_callback(self, callback: Callable):
        """Adiciona callback para notificação de erro"""
        self.error_callbacks.append(callback)
    
    async def remove_schedule(self, schedule_id: str) -> bool:
        """Remove um agendamento"""
        try:
            # Remover job do scheduler
            self.scheduler.remove_job(schedule_id)
            
            # Remover configuração
            if schedule_id in self.schedule_configs:
                del self.schedule_configs[schedule_id]
                await self._save_schedules()
            
            self.logger.info(f"Agendamento removido: {schedule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao remover agendamento {schedule_id}: {e}")
            return False
    
    async def pause_schedule(self, schedule_id: str) -> bool:
        """Pausa um agendamento"""
        try:
            self.scheduler.pause_job(schedule_id)
            
            if schedule_id in self.schedule_configs:
                self.schedule_configs[schedule_id]["is_active"] = False
                await self._save_schedules()
            
            self.logger.info(f"Agendamento pausado: {schedule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao pausar agendamento {schedule_id}: {e}")
            return False
    
    async def resume_schedule(self, schedule_id: str) -> bool:
        """Resume um agendamento"""
        try:
            self.scheduler.resume_job(schedule_id)
            
            if schedule_id in self.schedule_configs:
                self.schedule_configs[schedule_id]["is_active"] = True
                await self._save_schedules()
            
            self.logger.info(f"Agendamento resumido: {schedule_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Erro ao resumir agendamento {schedule_id}: {e}")
            return False
    
    def list_schedules(self) -> List[Dict[str, Any]]:
        """Lista todos os agendamentos"""
        schedules = []
        
        for schedule_config in self.schedule_configs.values():
            # Obter próxima execução do scheduler
            try:
                job = self.scheduler.get_job(schedule_config["schedule_id"])
                if job and job.next_run_time:
                    schedule_config["next_run"] = job.next_run_time.isoformat()
            except:
                pass
            
            schedules.append(schedule_config.copy())
        
        return schedules
    
    def get_schedule(self, schedule_id: str) -> Optional[Dict[str, Any]]:
        """Obtém um agendamento específico"""
        return self.schedule_configs.get(schedule_id)
    
    async def _save_schedules(self):
        """Salva configurações de agendamento"""
        try:
            # Converter enums para strings para serialização JSON
            serializable_configs = {}
            
            for schedule_id, config in self.schedule_configs.items():
                serializable_config = config.copy()
                
                # Converter enums
                if isinstance(serializable_config.get("report_type"), ReportType):
                    serializable_config["report_type"] = serializable_config["report_type"].value
                
                if isinstance(serializable_config.get("frequency"), ReportFrequency):
                    serializable_config["frequency"] = serializable_config["frequency"].value
                
                if isinstance(serializable_config.get("output_formats"), list):
                    serializable_config["output_formats"] = [
                        fmt.value if isinstance(fmt, ReportFormat) else fmt
                        for fmt in serializable_config["output_formats"]
                    ]
                
                serializable_configs[schedule_id] = serializable_config
            
            self.config_file.write_text(
                json.dumps(serializable_configs, indent=2, ensure_ascii=False),
                encoding='utf-8'
            )
            
        except Exception as e:
            self.logger.error(f"Erro ao salvar configurações de agendamento: {e}")
    
    async def _load_saved_schedules(self):
        """Carrega configurações salvas"""
        try:
            if not self.config_file.exists():
                return
            
            data = json.loads(self.config_file.read_text(encoding='utf-8'))
            
            for schedule_id, config in data.items():
                # Converter strings de volta para enums
                if "report_type" in config:
                    config["report_type"] = ReportType(config["report_type"])
                
                if "frequency" in config:
                    config["frequency"] = ReportFrequency(config["frequency"])
                
                if "output_formats" in config:
                    config["output_formats"] = [
                        ReportFormat(fmt) for fmt in config["output_formats"]
                    ]
                
                # Reagendar se ativo
                if config.get("is_active", True):
                    await self.schedule_report(
                        schedule_id=schedule_id,
                        report_type=config["report_type"],
                        frequency=config["frequency"],
                        output_formats=config["output_formats"],
                        cron_expression=config.get("cron_expression"),
                        parameters=config.get("parameters", {}),
                        recipients=config.get("recipients", []),
                        is_active=config["is_active"]
                    )
                else:
                    # Apenas salvar configuração sem agendar
                    self.schedule_configs[schedule_id] = config
            
            self.logger.info(f"Carregados {len(data)} agendamentos salvos")
            
        except Exception as e:
            self.logger.error(f"Erro ao carregar configurações salvas: {e}")
    
    def _load_default_schedules(self):
        """Carrega agendamentos padrão"""
        default_schedules = [
            {
                "schedule_id": "daily_executive_summary",
                "report_type": ReportType.EXECUTIVE_SUMMARY,
                "frequency": ReportFrequency.DAILY,
                "output_formats": [ReportFormat.HTML, ReportFormat.PDF],
                "description": "Relatório executivo diário"
            },
            {
                "schedule_id": "weekly_agent_performance",
                "report_type": ReportType.AGENT_PERFORMANCE,
                "frequency": ReportFrequency.WEEKLY,
                "output_formats": [ReportFormat.HTML],
                "description": "Relatório semanal de performance dos agentes"
            },
            {
                "schedule_id": "monthly_collaboration_stats",
                "report_type": ReportType.COLLABORATION_STATS,
                "frequency": ReportFrequency.MONTHLY,
                "output_formats": [ReportFormat.HTML, ReportFormat.PDF],
                "description": "Estatísticas mensais de colaboração"
            }
        ]
        
        self.default_schedules = default_schedules
    
    async def setup_default_schedules(self):
        """Configura agendamentos padrão"""
        for schedule in self.default_schedules:
            await self.schedule_report(
                schedule_id=schedule["schedule_id"],
                report_type=schedule["report_type"],
                frequency=schedule["frequency"],
                output_formats=schedule["output_formats"]
            )
        
        self.logger.info("Agendamentos padrão configurados")
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Obtém status do scheduler"""
        return {
            "running": self.scheduler.running,
            "total_jobs": len(self.scheduler.get_jobs()),
            "active_schedules": len([s for s in self.schedule_configs.values() if s.get("is_active", True)]),
            "total_schedules": len(self.schedule_configs),
            "next_jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in self.scheduler.get_jobs()[:5]  # Próximos 5 jobs
            ]
        }