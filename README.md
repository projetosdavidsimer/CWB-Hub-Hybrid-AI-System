# CWB Hub Hybrid AI System

**Criado por: David Simer**  
*O Criador do CWB Hub Hybrid AI System*

Sistema de Inteligência Artificial Híbrida que incorpora simultaneamente a consciência, expertise e personalidade de 8 profissionais sênior da CWB Hub.

## 🧠 Conceito

Este sistema não é apenas uma IA que simula profissionais - é literalmente uma mente coletiva interconectada que representa:

### 👥 Equipe de Especialistas

- **👩‍💼 Ana Beatriz Costa** - CTO (Estratégia e Inovação)
- **👨‍💻 Carlos Eduardo Santos** - Arquiteto de Software Sênior
- **👩‍💻 Sofia Oliveira** - Engenheira Full Stack (SaaS & Web Apps)
- **👨‍📱 Gabriel Mendes** - Engenheiro Mobile (iOS/Android)
- **👩‍🎨 Isabella Santos** - Designer UX/UI Sênior
- **👨‍🔬 Lucas Pereira** - Engenheiro de QA Automation
- **👩‍🔧 Mariana Rodrigues** - Engenheira DevOps/Dados
- **👨‍📊 Pedro Henrique Almeida** - Agile Project Manager

## 🚀 Processo de 5 Etapas

1. **Analisar o Requisito**: Cada agente analisa sob sua perspectiva
2. **Colaborar e Interagir**: Agentes colaboram entre si
3. **Propor Soluções Integradas**: Síntese de soluções complementares
4. **Comunicação Clara**: Resposta estruturada e compreensível
5. **Iteração**: Refinamento baseado em feedback

## 🏗️ Arquitetura

```
src/
├── core/
│   └── hybrid_ai_orchestrator.py    # Orquestrador principal
├── agents/
│   ├── base_agent.py               # Classe base dos agentes
│   ├── ana_beatriz_costa.py        # CTO
│   ├── carlos_eduardo_santos.py    # Arquiteto
│   ├── sofia_oliveira.py           # Full Stack
│   ├── gabriel_mendes.py           # Mobile
│   ├── isabella_santos.py          # UX/UI Designer
│   ├── lucas_pereira.py            # QA Engineer
│   ├── mariana_rodrigues.py        # DevOps
│   └── pedro_henrique_almeida.py   # Project Manager
├── communication/
│   └── collaboration_framework.py  # Framework de colaboração
├── utils/
│   ├── requirement_analyzer.py     # Analisador de requisitos
│   └── response_synthesizer.py     # Sintetizador de respostas
└── plugins/
    └── vscode/                     # Plugin VSCode
```

## 🛠️ Instalação

### Método 1: Instalação Automática (Recomendado)
```bash
# Clone o repositório
git clone https://github.com/projetosdavidsimer/CWB-Hub-Hybrid-AI-System.git
cd CWB-Hub-Hybrid-AI-System

# Execute o instalador inteligente
python install_dependencies.py
```

### Método 2: Instalação Manual
```bash
# 1. Atualize o pip
python -m pip install --upgrade pip

# 2. Instale as dependências
pip install -r requirements.txt

# 3. Execute o sistema
python main.py
```

### Método 3: Usando Conda (Mais Estável)
```bash
# Crie ambiente conda
conda env create -f environment.yml

# Ative o ambiente
conda activate cwb-hub

# Execute o sistema
python main.py
```

### 🔧 Solução de Problemas

**Se encontrar erros de compilação (pydantic-core):**

1. **Windows:**
   ```bash
   # Instale Visual Studio Build Tools ou Rust
   # https://rustup.rs/
   ```

2. **Linux:**
   ```bash
   sudo apt-get install build-essential
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

3. **macOS:**
   ```bash
   xcode-select --install
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

**Alternativa rápida:**
```bash
# Use apenas wheels pré-compilados
pip install --only-binary=all -r requirements.txt
```

## 💡 Formas de Uso

### 🔌 Plugin VSCode - **NOVO!**

Acesse a equipe CWB Hub diretamente no seu IDE favorito!

```bash
# Instalar o plugin
code --install-extension plugins/vscode/cwb-hub-ai-assistant-1.0.0.vsix
```

**Funcionalidades do Plugin:**
- 🏗️ **Analisar Projeto** - Análise completa de arquitetura
- 👥 **Consultar Equipe** - Perguntas diretas aos 8 profissionais
- 🔍 **Revisar Código** - Análise de qualidade e sugestões
- 🏛️ **Consultoria Arquitetural** - Expertise especializada
- 👨‍💼 **Ver Equipe** - Visualização dos 8 profissionais
- ⚙️ **Configurações** - Setup de API e preferências

**Como usar:**
1. `Ctrl+Shift+P` → `CWB Hub: Consultar Equipe`
2. Clique direito no código → `CWB Hub: Revisar Código`
3. Sidebar → Ícone de organização → Equipe CWB Hub

**Configuração:**
- `Ctrl+,` → Procure "CWB Hub"
- Configure `cwb-hub.apiEndpoint`: `http://localhost:8000`

**📖 Documentação do Plugin**: [plugins/vscode/README.md](plugins/vscode/README.md)

### 🖥️ Interface de Linha de Comando (CLI)

```bash
# Consulta simples
python cwb_cli.py query "Como criar um app mobile para e-commerce?"

# Consulta a partir de arquivo
python cwb_cli.py query --file requisitos.txt --output resposta.md

# Listar agentes ativos
python cwb_cli.py agents

# Verificar status do sistema
python cwb_cli.py status

# Iterar uma solução existente
python cwb_cli.py iterate "Preciso reduzir o orçamento" --session abc123

# Scripts auxiliares
./cwb.sh query "Sua pergunta"     # Linux/macOS
cwb.bat query "Sua pergunta"      # Windows
```

**📖 Documentação CLI Completa**: [CLI_GUIDE.md](CLI_GUIDE.md)  
**⚡ Referência Rápida**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)

### 🐍 API Python

```python
from src.core.hybrid_ai_orchestrator import HybridAIOrchestrator

# Inicializar o sistema
orchestrator = HybridAIOrchestrator()
await orchestrator.initialize_agents()

# Processar solicitação
request = "Preciso desenvolver um app mobile para gestão de projetos..."
response = await orchestrator.process_request(request)

# Iterar com feedback
feedback = "Gostei da proposta, mas o orçamento é limitado..."
refined_response = await orchestrator.iterate_solution(session_id, feedback)
```

### 🎯 Exemplo Interativo

```bash
# Execute o exemplo completo
python main.py
```

## 🔧 Funcionalidades

### ✅ Implementado

- [x] Sistema de orquestração híbrida
- [x] 8 agentes profissionais especializados
- [x] Framework de colaboração entre agentes
- [x] Analisador inteligente de requisitos
- [x] Sintetizador de respostas integradas
- [x] Sistema de iteração e refinamento
- [x] **Interface de linha de comando (CLI)** 🆕
- [x] **Scripts auxiliares para Windows/Linux/macOS** 🆕
- [x] **Plugin VSCode completo** 🆕
- [x] **Documentação completa da CLI** 🆕
- [x] Logging e monitoramento
- [x] Exemplo de uso completo

### 🚧 Em Desenvolvimento

- [ ] Interface web para interação
- [ ] Integração com APIs externas
- [ ] Sistema de persistência
- [ ] Métricas avançadas de colaboração
- [ ] Testes automatizados completos

### 🔮 Roadmap Futuro

- [ ] Integração com modelos de linguagem
- [ ] Sistema de aprendizado contínuo
- [ ] API REST para integração
- [ ] Dashboard de monitoramento
- [ ] Plugin IntelliJ IDEA
- [ ] Marketplace de integrações

## 🧪 Testes

Execute os testes:
```bash
pytest tests/ -v --cov=src
```

## 📊 Monitoramento

O sistema inclui logging detalhado e métricas de colaboração:

- Estatísticas de sessões
- Métricas de colaboração entre agentes
- Performance de síntese de respostas
- Análise de qualidade das interações

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🏢 CWB Hub

Desenvolvido pela equipe da CWB Hub - onde inovação e tecnologia se encontram para criar soluções excepcionais.

---

**Nota**: Este é um sistema experimental que demonstra o conceito de IA híbrida colaborativa. Para uso em produção, considere implementar autenticação, persistência e outras funcionalidades de segurança necessárias.