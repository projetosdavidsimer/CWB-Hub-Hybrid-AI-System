#!/usr/bin/env python3
"""
Demo do Sistema de Relatórios Automatizados CWB Hub
Criado pela Equipe Híbrida CWB Hub

Demonstra todas as funcionalidades do sistema de relatórios:
- Geração de relatórios
- Templates customizados
- Dashboard em tempo real
- Sistema de agendamento
- Distribuição por email
"""

import asyncio
import logging
from pathlib import Path
import sys

# Adicionar paths
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent / "src"))

from reporting.core.report_engine import ReportEngine
from reporting.core.data_collector import DataCollector
from reporting.core.template_engine import TemplateEngine
from reporting.core.scheduler import ReportScheduler
from reporting.models.report_models import ReportType, ReportFormat, ReportFrequency
from reporting.config.report_configs import get_config

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def demo_data_collection():
    """Demonstra coleta de dados"""
    print("\n" + "="*80)
    print("🔍 DEMONSTRAÇÃO: COLETA DE DADOS")
    print("="*80)
    
    collector = DataCollector()
    
    print("📊 Coletando métricas do sistema...")
    metrics = await collector.collect_all_metrics()
    
    print("✅ Dados coletados com sucesso!")
    print(f"📈 Seções de dados: {list(metrics.keys())}")
    
    # Mostrar algumas métricas interessantes
    session_metrics = metrics.get("session_metrics", {})
    agent_metrics = metrics.get("agent_metrics", {})
    
    print(f"\n📋 Resumo das Métricas:")
    print(f"  • Sessões ativas: {session_metrics.get('active_sessions', 0)}")
    print(f"  • Agentes ativos: {agent_metrics.get('total_active_agents', 0)}")
    print(f"  • Taxa de sucesso: {session_metrics.get('success_rate_percent', 0):.1f}%")
    
    return metrics


async def demo_template_engine():
    """Demonstra engine de templates"""
    print("\n" + "="*80)
    print("🎨 DEMONSTRAÇÃO: ENGINE DE TEMPLATES")
    print("="*80)
    
    template_engine = TemplateEngine()
    
    # Dados de exemplo
    sample_data = {
        "session_metrics": {
            "active_sessions": 12,
            "total_sessions_period": 150,
            "success_rate_percent": 94.5
        },
        "agent_metrics": {
            "total_active_agents": 8,
            "avg_participation_rate": 92.3
        },
        "collaboration_metrics": {
            "collaboration_quality_score": 8.9
        }
    }
    
    print("🖼️ Renderizando template de relatório executivo...")
    html_content = template_engine.render_template("executive_summary.html", sample_data)
    
    # Salvar exemplo
    output_file = Path("demo_executive_report.html")
    output_file.write_text(html_content, encoding='utf-8')
    
    print(f"✅ Template renderizado e salvo em: {output_file.absolute()}")
    print(f"📄 Tamanho do HTML: {len(html_content)} caracteres")


async def demo_report_generation():
    """Demonstra geração de relatórios"""
    print("\n" + "="*80)
    print("📊 DEMONSTRAÇÃO: GERAÇÃO DE RELATÓRIOS")
    print("="*80)
    
    report_engine = ReportEngine()
    
    # Gerar diferentes tipos de relatórios
    report_types = [
        ReportType.EXECUTIVE_SUMMARY,
        ReportType.AGENT_PERFORMANCE,
        ReportType.COLLABORATION_STATS
    ]
    
    for report_type in report_types:
        print(f"\n📈 Gerando relatório: {report_type.value}")
        
        try:
            result = await report_engine.generate_report(
                report_type=report_type,
                output_formats=[ReportFormat.HTML]
            )
            
            if result.status.value == "completed":
                print(f"  ✅ Sucesso! Tempo: {result.duration_seconds:.2f}s")
                print(f"  📁 Arquivos: {len(result.output_files)}")
                for file_path in result.output_files:
                    print(f"    • {file_path}")
            else:
                print(f"  ❌ Falha: {result.error_message}")
                
        except Exception as e:
            print(f"  ❌ Erro: {e}")


async def demo_dashboard():
    """Demonstra dashboard em tempo real"""
    print("\n" + "="*80)
    print("📊 DEMONSTRAÇÃO: DASHBOARD EM TEMPO REAL")
    print("="*80)
    
    report_engine = ReportEngine()
    
    print("🔄 Gerando dashboard...")
    dashboard_html = await report_engine.generate_dashboard_report()
    
    # Salvar dashboard
    dashboard_file = Path("demo_dashboard.html")
    dashboard_file.write_text(dashboard_html, encoding='utf-8')
    
    print(f"✅ Dashboard gerado: {dashboard_file.absolute()}")
    print(f"📊 Tamanho: {len(dashboard_html)} caracteres")
    
    # Tentar abrir no navegador
    try:
        import webbrowser
        webbrowser.open(f"file://{dashboard_file.absolute()}")
        print("🌐 Dashboard aberto no navegador!")
    except:
        print("💡 Abra manualmente o arquivo dashboard.html no navegador")


async def demo_scheduler():
    """Demonstra sistema de agendamento"""
    print("\n" + "="*80)
    print("⏰ DEMONSTRAÇÃO: SISTEMA DE AGENDAMENTO")
    print("="*80)
    
    report_engine = ReportEngine()
    scheduler = ReportScheduler(report_engine)
    
    try:
        print("🚀 Iniciando scheduler...")
        await scheduler.start()
        
        # Configurar agendamentos de demonstração
        schedules = [
            {
                "schedule_id": "demo_daily_executive",
                "report_type": ReportType.EXECUTIVE_SUMMARY,
                "frequency": ReportFrequency.DAILY,
                "output_formats": [ReportFormat.HTML]
            },
            {
                "schedule_id": "demo_weekly_agents",
                "report_type": ReportType.AGENT_PERFORMANCE,
                "frequency": ReportFrequency.WEEKLY,
                "output_formats": [ReportFormat.HTML]
            }
        ]
        
        print("\n📅 Configurando agendamentos de demonstração...")
        for schedule_config in schedules:
            success = await scheduler.schedule_report(**schedule_config)
            status = "✅ Sucesso" if success else "❌ Falha"
            print(f"  {status}: {schedule_config['schedule_id']}")
        
        # Listar agendamentos
        print("\n📋 Agendamentos configurados:")
        active_schedules = scheduler.list_schedules()
        
        for schedule in active_schedules:
            print(f"  🔹 {schedule['schedule_id']}")
            print(f"    Tipo: {schedule['report_type']}")
            print(f"    Frequência: {schedule['frequency']}")
            print(f"    Próxima execução: {schedule.get('next_run', 'N/A')}")
        
        # Status do scheduler
        status = scheduler.get_scheduler_status()
        print(f"\n📊 Status do Scheduler:")
        print(f"  • Executando: {'Sim' if status['running'] else 'Não'}")
        print(f"  • Total de jobs: {status['total_jobs']}")
        print(f"  • Agendamentos ativos: {status['active_schedules']}")
        
    finally:
        print("\n🛑 Parando scheduler...")
        await scheduler.stop()


async def demo_configuration():
    """Demonstra sistema de configuração"""
    print("\n" + "="*80)
    print("⚙️ DEMONSTRAÇÃO: SISTEMA DE CONFIGURAÇÃO")
    print("="*80)
    
    config = get_config()
    
    print("📋 Configurações do Sistema:")
    print(f"  • Diretório de saída: {config.REPORTS_OUTPUT_DIR}")
    print(f"  • Diretório de templates: {config.TEMPLATES_DIR}")
    print(f"  • Cache habilitado: {config.CACHE_CONFIG['enabled']}")
    print(f"  • Alertas habilitados: {config.ALERT_CONFIG['enabled']}")
    
    # Validar configurações
    print("\n🔍 Validando configurações...")
    validation = config.validate_config()
    
    for component, is_valid in validation.items():
        status = "✅ OK" if is_valid else "❌ Erro"
        print(f"  {status}: {component}")
    
    # Criar diretórios necessários
    print("\n📁 Criando diretórios necessários...")
    config.create_directories()
    print("✅ Diretórios criados com sucesso!")
    
    # Informações do ambiente
    env_info = config.get_environment_info()
    print(f"\n🌍 Informações do Ambiente:")
    for key, value in env_info.items():
        print(f"  • {key}: {value}")


async def demo_complete_workflow():
    """Demonstra fluxo completo do sistema"""
    print("\n" + "="*80)
    print("🚀 DEMONSTRAÇÃO: FLUXO COMPLETO")
    print("="*80)
    
    print("1️⃣ Inicializando sistema completo...")
    
    # Inicializar componentes
    data_collector = DataCollector()
    template_engine = TemplateEngine()
    report_engine = ReportEngine(data_collector, template_engine)
    
    print("2️⃣ Coletando dados em tempo real...")
    metrics = await data_collector.collect_all_metrics()
    
    print("3️⃣ Gerando relatório executivo completo...")
    result = await report_engine.generate_report(
        report_type=ReportType.EXECUTIVE_SUMMARY,
        output_formats=[ReportFormat.HTML, ReportFormat.JSON]
    )
    
    if result.status.value == "completed":
        print("✅ Relatório completo gerado com sucesso!")
        print(f"⏱️ Tempo total: {result.duration_seconds:.2f} segundos")
        print("📁 Arquivos gerados:")
        for file_path in result.output_files:
            print(f"  • {file_path}")
    
    print("4️⃣ Gerando dashboard final...")
    dashboard_html = await report_engine.generate_dashboard_report()
    
    final_dashboard = Path("demo_final_dashboard.html")
    final_dashboard.write_text(dashboard_html, encoding='utf-8')
    
    print(f"✅ Dashboard final: {final_dashboard.absolute()}")
    
    print("\n🎉 DEMONSTRAÇÃO COMPLETA!")
    print("="*80)
    print("📊 Sistema de Relatórios CWB Hub totalmente funcional!")
    print("🔧 Recursos demonstrados:")
    print("  ✅ Coleta automática de dados")
    print("  ✅ Templates customizáveis")
    print("  ✅ Geração de múltiplos formatos")
    print("  ✅ Dashboard em tempo real")
    print("  ✅ Sistema de agendamento")
    print("  ✅ Configuração flexível")
    print("\n💡 Use a CLI para interagir com o sistema:")
    print("   python cwb_cli.py report-generate executive_summary")
    print("   python cwb_cli.py dashboard --open")
    print("   python cwb_cli.py report-schedule list")


async def main():
    """Função principal da demonstração"""
    print("🎯 SISTEMA DE RELATÓRIOS AUTOMATIZADOS CWB HUB")
    print("Criado pela Equipe Híbrida CWB Hub")
    print("="*80)
    
    try:
        # Executar todas as demonstrações
        await demo_configuration()
        await demo_data_collection()
        await demo_template_engine()
        await demo_report_generation()
        await demo_dashboard()
        await demo_scheduler()
        await demo_complete_workflow()
        
    except KeyboardInterrupt:
        print("\n⚠️ Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante demonstração: {e}")
        logger.exception("Erro na demonstração")


if __name__ == "__main__":
    # Configurar encoding para Windows
    if sys.platform == "win32":
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
    
    asyncio.run(main())