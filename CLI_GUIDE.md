# CWB Hub Hybrid AI System - Guia da Interface de Linha de Comando

**Criado por: David Simer**  
*Interface de linha de comando para o CWB Hub Hybrid AI System*

## 📋 Visão Geral

A CLI do CWB Hub permite interagir com o sistema de IA híbrida diretamente da linha de comando, oferecendo acesso completo aos 8 especialistas da equipe CWB Hub de forma eficiente e automatizada.

## 🚀 Instalação e Configuração

### Pré-requisitos
- Python 3.8 ou superior
- Dependências do CWB Hub instaladas

### Verificação da Instalação
```bash
# Verificar se o sistema está funcionando
python cwb_cli.py agents

# Ou usando os scripts auxiliares
./cwb.sh agents        # Linux/macOS
cwb.bat agents         # Windows
```

## 📖 Comandos Disponíveis

### 1. `query` - Fazer Consultas

Envia uma solicitação para a equipe de especialistas CWB Hub.

#### Sintaxe
```bash
python cwb_cli.py query [SOLICITAÇÃO] [OPÇÕES]
```

#### Opções
- `--file, -f`: Ler solicitação de arquivo
- `--output, -o`: Salvar resposta em arquivo
- `--no-save`: Não salvar sessão
- `--stats`: Mostrar estatísticas de colaboração
- `--verbose, -v`: Modo verboso

#### Exemplos
```bash
# Consulta simples
python cwb_cli.py query "Como criar um aplicativo mobile para e-commerce?"

# Consulta a partir de arquivo
python cwb_cli.py query --file requisitos.txt --output resposta.md

# Consulta com estatísticas
python cwb_cli.py query "Desenvolver API REST" --stats --verbose

# Consulta interativa (digite Ctrl+D para finalizar)
python cwb_cli.py query
```

### 2. `iterate` - Iterar Soluções

Refina uma solução existente com base em feedback.

#### Sintaxe
```bash
python cwb_cli.py iterate [FEEDBACK] [OPÇÕES]
```

#### Opções
- `--session, -s`: ID da sessão específica
- `--file, -f`: Ler feedback de arquivo
- `--output, -o`: Salvar resposta em arquivo

#### Exemplos
```bash
# Iterar com feedback direto
python cwb_cli.py iterate "Preciso reduzir o orçamento pela metade"

# Iterar sessão específica
python cwb_cli.py iterate --session abc123 "Focar apenas em iOS"

# Feedback a partir de arquivo
python cwb_cli.py iterate --file feedback.txt --output solucao_v2.md
```

### 3. `status` - Verificar Status

Mostra informações sobre sessões ativas e estatísticas do sistema.

#### Sintaxe
```bash
python cwb_cli.py status [OPÇÕES]
```

#### Opções
- `--session, -s`: Status de sessão específica
- `--collaboration, -c`: Estatísticas de colaboração

#### Exemplos
```bash
# Listar todas as sessões
python cwb_cli.py status

# Status de sessão específica
python cwb_cli.py status --session abc123

# Estatísticas de colaboração
python cwb_cli.py status --collaboration
```

### 4. `agents` - Listar Agentes

Exibe todos os agentes ativos da equipe CWB Hub.

#### Sintaxe
```bash
python cwb_cli.py agents
```

#### Exemplo
```bash
python cwb_cli.py agents
```

## 🛠️ Scripts Auxiliares

### Windows (`cwb.bat`)
```cmd
REM Consulta simples
cwb.bat query "Como implementar autenticação JWT?"

REM Verificar agentes
cwb.bat agents

REM Ajuda
cwb.bat --help
```

### Linux/macOS (`cwb.sh`)
```bash
# Consulta simples
./cwb.sh query "Como implementar autenticação JWT?"

# Verificar agentes
./cwb.sh agents

# Ajuda
./cwb.sh --help
```

## 📝 Exemplos Práticos

### Exemplo 1: Desenvolvimento de App Mobile
```bash
# Consulta inicial
python cwb_cli.py query "Preciso desenvolver um app mobile para delivery de comida com as seguintes funcionalidades: cadastro de usuários, catálogo de restaurantes, carrinho de compras, pagamento integrado e rastreamento de pedidos." --output app_mobile_plan.md

# Iteração com restrições
python cwb_cli.py iterate "O orçamento é limitado a R$ 50.000 e o prazo é de 3 meses. Priorize funcionalidades essenciais." --output app_mobile_mvp.md
```

### Exemplo 2: Arquitetura de Sistema
```bash
# Consulta sobre arquitetura
python cwb_cli.py query --file arquitetura_requisitos.txt --output arquitetura_proposta.md --stats

# Refinamento baseado em feedback
python cwb_cli.py iterate "A solução precisa suportar 100.000 usuários simultâneos e ter alta disponibilidade" --output arquitetura_escalavel.md
```

### Exemplo 3: Workflow Automatizado
```bash
#!/bin/bash
# Script para análise automatizada de projetos

echo "🚀 Iniciando análise automatizada..."

# Ler requisitos do arquivo
python cwb_cli.py query --file projeto_requisitos.txt --output analise_inicial.md --verbose

# Verificar se a análise foi bem-sucedida
if [ $? -eq 0 ]; then
    echo "✅ Análise inicial concluída"
    
    # Aplicar feedback padrão
    python cwb_cli.py iterate "Considere as melhores práticas de segurança e performance" --output analise_final.md
    
    echo "✅ Análise completa salva em analise_final.md"
else
    echo "❌ Erro na análise inicial"
fi
```

## 🔧 Configurações Avançadas

### Variáveis de Ambiente
```bash
# Configurar nível de log
export CWB_LOG_LEVEL=DEBUG

# Configurar timeout personalizado
export CWB_TIMEOUT=300

# Configurar diretório de saída padrão
export CWB_OUTPUT_DIR=/path/to/outputs
```

### Arquivo de Configuração (`.cwbconfig`)
```json
{
    "default_output_format": "markdown",
    "auto_save_sessions": true,
    "verbose_mode": false,
    "collaboration_stats": true,
    "max_session_history": 10
}
```

## 📊 Formatos de Saída

### Resposta Padrão
```
💡 RESPOSTA DA EQUIPE CWB HUB
================================================================================

[Resposta estruturada da equipe com contribuições de cada especialista]

📊 ESTATÍSTICAS
- Agentes participantes: 8
- Tempo de processamento: 2.3s
- Sessão ID: abc123def456
```

### Formato JSON (com --json)
```json
{
    "session_id": "abc123def456",
    "response": "...",
    "agents_involved": [...],
    "processing_time": 2.3,
    "collaboration_stats": {...}
}
```

## 🚨 Solução de Problemas

### Erro: "Sistema não inicializado"
```bash
# Verificar se as dependências estão instaladas
python install_dependencies.py

# Verificar se o diretório src existe
ls -la src/
```

### Erro: "Módulo não encontrado"
```bash
# Verificar PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Ou reinstalar dependências
pip install -r requirements.txt
```

### Erro: "Sessão não encontrada"
```bash
# Listar sessões ativas
python cwb_cli.py status

# Usar ID de sessão específico
python cwb_cli.py iterate "feedback" --session [SESSION_ID]
```

### Performance Lenta
```bash
# Usar modo menos verboso
python cwb_cli.py query "..." --no-save

# Verificar recursos do sistema
python cwb_cli.py status --collaboration
```

## 🔗 Integração com Outras Ferramentas

### Git Hooks
```bash
#!/bin/bash
# .git/hooks/pre-commit
# Análise automática de código antes do commit

python cwb_cli.py query "Analise as mudanças no código e sugira melhorias" --file <(git diff --cached) --output code_review.md
```

### CI/CD Pipeline
```yaml
# .github/workflows/cwb-analysis.yml
name: CWB Hub Analysis
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: python install_dependencies.py
      - name: Run CWB Analysis
        run: |
          python cwb_cli.py query "Analise este projeto e sugira melhorias" --output analysis.md
          cat analysis.md >> $GITHUB_STEP_SUMMARY
```

### VS Code Integration
```json
// .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "CWB Hub Query",
            "type": "shell",
            "command": "python",
            "args": ["cwb_cli.py", "query", "${input:userQuery}"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        }
    ],
    "inputs": [
        {
            "id": "userQuery",
            "description": "Digite sua consulta para a equipe CWB Hub",
            "default": "Como melhorar este código?",
            "type": "promptString"
        }
    ]
}
```

## 📚 Recursos Adicionais

- **Documentação Completa**: [README.md](README.md)
- **Guia de Instalação**: [GUIA_USO_ATUALIZADO.md](GUIA_USO_ATUALIZADO.md)
- **Status do Projeto**: [PROJECT_STATUS.md](PROJECT_STATUS.md)
- **Relatório de Validação**: [VALIDATION_REPORT.md](VALIDATION_REPORT.md)

## 🤝 Suporte

Para suporte e dúvidas:
1. Verifique este guia primeiro
2. Execute `python cwb_cli.py --help`
3. Consulte os logs com `--verbose`
4. Abra uma issue no repositório

---

**Criado por David Simer - CWB Hub Hybrid AI System**  
*Transformando ideias em soluções através da inteligência coletiva*