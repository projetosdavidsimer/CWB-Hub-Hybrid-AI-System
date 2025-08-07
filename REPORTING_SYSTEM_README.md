# 📊 Sistema de Relatórios Automatizados CWB Hub

**Criado pela Equipe Híbrida CWB Hub**

Sistema completo de relatórios automatizados que coleta métricas, gera relatórios personalizados e distribui insights de forma inteligente.

## 🎯 Visão Geral

O Sistema de Relatórios Automatizados é uma solução completa que:

- 📈 **Coleta métricas** do sistema CWB Hub em tempo real
- 🎨 **Gera relatórios** com templates elegantes e customizáveis
- ⏰ **Agenda execuções** automáticas com múltiplas frequências
- 📧 **Distribui relatórios** por email automaticamente
- 📊 **Cria dashboards** interativos em tempo real
- 🔧 **Oferece APIs** para integração externa

## 🏗️ Arquitetura

```
reporting/
├── core/                          # Componentes principais
│   ├── data_collector.py         # Coleta de métricas
│   ├── template_engine.py        # Engine de templates
│   ├── report_engine.py          # Motor de relatórios
│   └── scheduler.py               # Sistema de agendamento
├── models/                        # Modelos de dados
│   └── report_models.py          # Modelos SQLAlchemy e Pydantic
├── templates/                     # Templates HTML
│   ├── executive_summary.html    # Relatório executivo
│   ├── agent_performance.html    # Performance dos agentes
│   ├── collaboration_stats.html  # Estatísticas de colaboração
│   ├── system_usage.html         # Uso do sistema
│   └── dashboard.html             # Dashboard em tempo real
├── exporters/                     # Exportadores de formato
├── distributors/                  # Distribuidores (email, etc.)
│   └── email_distributor.py      # Distribuição por email
└── config/                        # Configurações
    └── report_configs.py          # Configurações centralizadas
```

## 🚀 Instalação e Configuração

### 1. Dependências

O sistema de relatórios adiciona as seguintes dependências ao CWB Hub:

```bash
# Instalar dependências automaticamente
pip install -r requirements.txt
```

**Dependências principais:**
- `jinja2` - Engine de templates
- `weasyprint` - Geração de PDFs
- `pandas` - Manipulação de dados
- `matplotlib` - Gráficos básicos
- `plotly` - Gráficos interativos
- `apscheduler` - Agendamento de tarefas
- `openpyxl` - Exportação Excel

### 2. Configuração do Banco de Dados

O sistema utiliza o PostgreSQL existente do CWB Hub:

```bash
# Configurar banco (se ainda não foi feito)
cd persistence
python setup_database.py
```

### 3. Configuração de Email (Opcional)

Para distribuição automática por email, configure as variáveis de ambiente:

```bash
# .env ou variáveis do sistema
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app
SMTP_USE_TLS=true
```

## 📊 Tipos de Relatórios

### 1. Relatório Executivo (`executive_summary`)
- **Descrição**: Visão geral para gestão executiva
- **Frequência padrão**: Diário
- **Conteúdo**: Métricas principais, tendências, resumo executivo
- **Formatos**: HTML, PDF

### 2. Performance dos Agentes (`agent_performance`)
- **Descrição**: Análise detalhada de cada agente especializado
- **Frequência padrão**: Semanal
- **Conteúdo**: Participação, tempo de resposta, qualidade, colaboração
- **Formatos**: HTML

### 3. Estatísticas de Colaboração (`collaboration_stats`)
- **Descrição**: Métricas de trabalho em equipe entre agentes
- **Frequência padrão**: Semanal
- **Conteúdo**: Interações, consenso, resolução de conflitos
- **Formatos**: HTML, PDF

### 4. Uso do Sistema (`system_usage`)
- **Descrição**: Métricas de infraestrutura e utilização
- **Frequência padrão**: Diário
- **Conteúdo**: CPU, memória, sessões, uptime
- **Formatos**: HTML

### 5. Análise de Qualidade (`quality_analysis`)
- **Descrição**: Qualidade das respostas e satisfação
- **Frequência padrão**: Semanal
- **Conteúdo**: Scores de qualidade, feedback, precisão
- **Formatos**: HTML, PDF

## 🖥️ Uso via CLI

### Gerar Relatórios

```bash
# Relatório executivo em HTML
python cwb_cli.py report-generate executive_summary

# Múltiplos formatos
python cwb_cli.py report-generate executive_summary --formats html pdf json

# Salvar em diretório específico
python cwb_cli.py report-generate agent_performance --output-dir ./reports
```

### Gerenciar Agendamentos

```bash
# Listar agendamentos
python cwb_cli.py report-schedule list

# Criar agendamento diário
python cwb_cli.py report-schedule add --type executive_summary --frequency daily

# Criar agendamento com email
python cwb_cli.py report-schedule add \
  --type collaboration_stats \
  --frequency weekly \
  --recipients admin@empresa.com team@empresa.com

# Pausar agendamento
python cwb_cli.py report-schedule pause --schedule-id daily_executive

# Status do scheduler
python cwb_cli.py report-schedule status
```

### Dashboard

```bash
# Gerar dashboard
python cwb_cli.py dashboard

# Gerar e abrir no navegador
python cwb_cli.py dashboard --open

# Salvar com nome específico
python cwb_cli.py dashboard --output meu_dashboard.html
```

## 🐍 Uso via API Python

### Geração Básica

```python
from reporting.core.report_engine import ReportEngine
from reporting.models.report_models import ReportType, ReportFormat

# Inicializar engine
engine = ReportEngine()

# Gerar relatório
result = await engine.generate_report(
    report_type=ReportType.EXECUTIVE_SUMMARY,
    output_formats=[ReportFormat.HTML, ReportFormat.PDF]
)

if result.status.value == "completed":
    print(f"Relatório gerado: {result.output_files}")
```

### Dashboard em Tempo Real

```python
# Gerar dashboard
dashboard_html = await engine.generate_dashboard_report()

# Salvar
with open("dashboard.html", "w", encoding="utf-8") as f:
    f.write(dashboard_html)
```

### Sistema de Agendamento

```python
from reporting.core.scheduler import ReportScheduler
from reporting.models.report_models import ReportFrequency

# Inicializar scheduler
scheduler = ReportScheduler(engine)
await scheduler.start()

# Agendar relatório
await scheduler.schedule_report(
    schedule_id="weekly_performance",
    report_type=ReportType.AGENT_PERFORMANCE,
    frequency=ReportFrequency.WEEKLY,
    recipients=["team@empresa.com"]
)
```

### Coleta de Dados Customizada

```python
from reporting.core.data_collector import DataCollector

# Coletar métricas
collector = DataCollector()
metrics = await collector.collect_all_metrics()

# Dados específicos para dashboard
dashboard_data = await collector.get_dashboard_data()
```

## 🎨 Customização de Templates

### Estrutura dos Templates

Os templates usam Jinja2 e estão em `reporting/templates/`:

```html
<!-- Exemplo: template customizado -->
<!DOCTYPE html>
<html>
<head>
    <title>{{ report_config.name }}</title>
    <style>
        /* Seus estilos CSS */
    </style>
</head>
<body>
    <h1>{{ system_name }}</h1>
    <p>Gerado em: {{ generated_at.strftime('%d/%m/%Y às %H:%M') }}</p>
    
    <!-- Métricas -->
    <div class="metrics">
        <div class="metric">
            <span class="value">{{ session_metrics.active_sessions | format_number(0) }}</span>
            <span class="label">Sessões Ativas</span>
        </div>
    </div>
    
    <!-- Gráficos (se disponíveis) -->
    {% if charts.sessions_trend %}
    <img src="{{ charts.sessions_trend }}" alt="Tendência de Sessões">
    {% endif %}
</body>
</html>
```

### Filtros Disponíveis

- `format_number(decimals)` - Formata números
- `format_percent(decimals)` - Formata percentuais
- `format_duration(seconds)` - Formata duração
- `status_badge(status)` - Gera badge de status

### Dados Disponíveis nos Templates

```python
{
    "generated_at": datetime,
    "system_name": "CWB Hub Hybrid AI System",
    "version": "1.0.0",
    "session_metrics": {...},
    "agent_metrics": {...},
    "collaboration_metrics": {...},
    "system_metrics": {...},
    "performance_metrics": {...},
    "quality_metrics": {...},
    "charts": {...}  # Gráficos em base64
}
```

## ⚙️ Configuração Avançada

### Arquivo de Configuração

```python
# reporting/config/report_configs.py
from reporting.config.report_configs import get_config

config = get_config()

# Personalizar configurações
config.RETENTION_CONFIG["reports_max_age_days"] = 180
config.PERFORMANCE_CONFIG["max_concurrent_reports"] = 10
config.CACHE_CONFIG["ttl_minutes"] = 30
```

### Configurações de Email

```python
# Configurar SMTP
config.SMTP_CONFIG.update({
    "server": "smtp.empresa.com",
    "port": 587,
    "username": "relatorios@empresa.com",
    "password": "senha-segura"
})
```

### Configurações de Agendamento

```python
# Personalizar scheduler
config.SCHEDULER_CONFIG.update({
    "timezone": "America/Sao_Paulo",
    "max_instances": 5,
    "misfire_grace_time": 600  # 10 minutos
})
```

## 📧 Distribuição por Email

### Configuração Básica

```python
from reporting.distributors.email_distributor import EmailDistributor

# Configurar distribuidor
distributor = EmailDistributor(
    smtp_server="smtp.gmail.com",
    smtp_port=587,
    username="seu-email@gmail.com",
    password="sua-senha-app"
)

# Enviar relatório
await distributor.send_report(
    recipients=["admin@empresa.com"],
    report_files=[Path("relatorio.pdf")],
    report_type="executive_summary"
)
```

### Templates de Email

O sistema inclui templates HTML para emails com:
- Cabeçalho da empresa
- Resumo do relatório
- Lista de arquivos anexos
- Informações de execução
- Rodapé profissional

## 📊 Métricas Coletadas

### Métricas de Sistema
- Uso de CPU, memória e disco
- Uptime do sistema
- Estatísticas de rede

### Métricas de Sessões
- Sessões ativas e totais
- Duração média das sessões
- Taxa de sucesso/falha
- Sessões por hora

### Métricas de Agentes
- Taxa de participação
- Tempo médio de resposta
- Score de qualidade
- Interações totais

### Métricas de Colaboração
- Interações entre agentes
- Taxa de consenso
- Tempo de resolução de conflitos
- Score de colaboração

### Métricas de Qualidade
- Score médio de qualidade
- Satisfação do usuário
- Precisão das respostas
- Feedback recebido

## 🔧 Troubleshooting

### Problemas Comuns

**1. Erro na geração de PDF**
```bash
# Instalar dependências do WeasyPrint
# Ubuntu/Debian
sudo apt-get install python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

# Windows: Instalar GTK+ runtime
```

**2. Erro de conexão SMTP**
```python
# Testar configuração
distributor = EmailDistributor()
if distributor.test_connection():
    print("SMTP OK")
else:
    print("Verificar configurações SMTP")
```

**3. Erro de permissões no banco**
```bash
# Verificar configuração do PostgreSQL
cd persistence
python setup_database.py
```

### Logs e Debugging

```python
import logging

# Habilitar logs detalhados
logging.basicConfig(level=logging.DEBUG)

# Logs específicos do sistema de relatórios
logger = logging.getLogger("reporting")
logger.setLevel(logging.DEBUG)
```

## 🧪 Demonstração

Execute o script de demonstração para ver todas as funcionalidades:

```bash
python demo_reporting_system.py
```

A demonstração inclui:
- ✅ Coleta de dados
- ✅ Geração de templates
- ✅ Criação de relatórios
- ✅ Dashboard interativo
- ✅ Sistema de agendamento
- ✅ Configurações

## 🔮 Roadmap

### Próximas Funcionalidades

- [ ] **Alertas Inteligentes**: Notificações baseadas em thresholds
- [ ] **Relatórios Customizados**: Editor visual de relatórios
- [ ] **Integração com BI**: Conectores para Tableau, Power BI
- [ ] **API REST**: Endpoints para integração externa
- [ ] **Cache Avançado**: Redis para performance
- [ ] **Backup Automático**: Backup de relatórios e configurações
- [ ] **Auditoria**: Log de todas as ações do sistema
- [ ] **Multi-tenant**: Suporte a múltiplas organizações

### Melhorias Planejadas

- [ ] **Performance**: Otimização para grandes volumes
- [ ] **Segurança**: Criptografia de dados sensíveis
- [ ] **Escalabilidade**: Suporte a clusters
- [ ] **Monitoramento**: Métricas do próprio sistema de relatórios

## 🤝 Contribuição

### Como Contribuir

1. **Fork** o repositório
2. **Crie** uma branch para sua feature
3. **Implemente** seguindo os padrões do código
4. **Teste** suas mudanças
5. **Submeta** um Pull Request

### Padrões de Código

- Seguir PEP 8 para Python
- Documentar todas as funções públicas
- Incluir testes para novas funcionalidades
- Usar type hints quando possível

## 📝 Licença

Este sistema é parte do CWB Hub Hybrid AI System e segue a mesma licença MIT.

## 🏢 Equipe

**Criado pela Equipe Híbrida CWB Hub:**

- 👩‍💼 **Ana Beatriz Costa** (CTO) - Estratégia e Visão
- 👨‍💻 **Carlos Eduardo Santos** (Arquiteto) - Arquitetura do Sistema
- 👩‍💻 **Sofia Oliveira** (Full Stack) - Implementação Core
- 👨‍📱 **Gabriel Mendes** (Mobile) - Integração Mobile
- 👩‍🎨 **Isabella Santos** (UX/UI) - Design dos Templates
- 👨‍🔬 **Lucas Pereira** (QA) - Qualidade e Testes
- 👩‍🔧 **Mariana Rodrigues** (DevOps) - Infraestrutura
- 👨‍📊 **Pedro Henrique Almeida** (PM) - Gestão do Projeto

---

**💡 Para suporte técnico ou dúvidas, consulte a documentação completa ou entre em contato com a equipe CWB Hub.**