# CWB Hub AI Assistant - VSCode Extension

**Equipe de 8 profissionais sênior de IA híbrida diretamente no seu IDE**

## 🎯 Visão Geral

O CWB Hub AI Assistant traz a expertise de uma equipe completa de 8 profissionais sênior diretamente para o seu VSCode. Obtenha consultoria técnica especializada, análise de projetos, revisão de código e orientação arquitetural sem sair do seu ambiente de desenvolvimento.

## 👥 Equipe CWB Hub

- **👩‍💼 Ana Beatriz Costa** - CTO (Estratégia & Inovação)
- **👨‍💻 Carlos Eduardo Santos** - Arquiteto de Software Sênior
- **👩‍💻 Sofia Oliveira** - Engenheira Full Stack
- **👨‍📱 Gabriel Mendes** - Engenheiro Mobile
- **👩‍🎨 Isabella Santos** - Designer UX/UI Sênior
- **👨‍🔬 Lucas Pereira** - Engenheiro de QA
- **👩‍🔧 Mariana Rodrigues** - Engenheira DevOps
- **👨‍📊 Pedro Henrique Almeida** - Agile Project Manager

## ✨ Funcionalidades

### 🏗️ Análise de Projeto
- Análise completa da arquitetura do seu projeto
- Identificação de tecnologias e padrões
- Sugestões de melhorias e boas práticas
- Avaliação de riscos e oportunidades

### 👥 Consulta à Equipe
- Faça perguntas específicas para a equipe
- Obtenha respostas especializadas de cada profissional
- Contexto automático do arquivo/projeto atual
- Histórico de consultas

### 🔍 Revisão de Código
- Análise detalhada de qualidade do código
- Identificação de bugs e problemas
- Sugestões de otimização e performance
- Verificação de boas práticas e segurança

### 🏛️ Consultoria Arquitetural
- Orientação sobre padrões de design
- Estratégias de escalabilidade
- Decisões de arquitetura
- Melhores práticas de desenvolvimento

## 🚀 Como Usar

### Instalação

1. Instale a extensão do marketplace do VSCode
2. Configure o endpoint da API do CWB Hub
3. Adicione sua chave de API (se necessário)
4. Comece a usar!

### Comandos Disponíveis

- `Ctrl+Shift+P` → `CWB Hub: Analisar Projeto`
- `Ctrl+Shift+P` → `CWB Hub: Consultar Equipe`
- `Ctrl+Shift+P` → `CWB Hub: Revisar Código`
- `Ctrl+Shift+P` → `CWB Hub: Consultoria Arquitetural`
- `Ctrl+Shift+P` → `CWB Hub: Ver Equipe`

### Menu de Contexto

- **Clique direito no código** �� `CWB Hub: Revisar Código`
- **Clique direito no explorador** → `CWB Hub: Analisar Projeto`

### Sidebar

- **Equipe CWB Hub**: Visualize todos os profissionais disponíveis
- **Histórico**: Acesse consultas anteriores

## ⚙️ Configuração

### Configurações Disponíveis

```json
{
  "cwb-hub.apiEndpoint": "http://localhost:8000",
  "cwb-hub.apiKey": "sua-chave-api",
  "cwb-hub.autoAnalyze": false,
  "cwb-hub.showNotifications": true
}
```

### Configuração da API

1. Abra as configurações do VSCode (`Ctrl+,`)
2. Procure por "CWB Hub"
3. Configure o endpoint da API
4. Adicione sua chave de API (opcional)

## 🔧 Desenvolvimento

### Pré-requisitos

- Node.js 16+
- VSCode 1.74+
- TypeScript

### Setup Local

```bash
# Clone o repositório
git clone https://github.com/projetosdavidsimer/CWB-Hub-Hybrid-AI-System.git

# Navegue para o plugin
cd CWB-Hub-Hybrid-AI-System/plugins/vscode

# Instale dependências
npm install

# Compile o TypeScript
npm run compile

# Execute em modo de desenvolvimento
# Pressione F5 no VSCode para abrir uma nova janela com a extensão
```

### Build e Publicação

```bash
# Compile para produção
npm run vscode:prepublish

# Gere o pacote VSIX
npm run package

# Publique no marketplace (requer vsce configurado)
npm run publish
```

## 📋 Requisitos

### Sistema
- VSCode 1.74.0 ou superior
- Conexão com internet para API do CWB Hub

### API CWB Hub
- Servidor CWB Hub rodando (local ou remoto)
- Endpoint acessível
- Chave de API (opcional, dependendo da configuração)

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](../../LICENSE) para detalhes.

## 🆘 Suporte

- **Issues**: [GitHub Issues](https://github.com/projetosdavidsimer/CWB-Hub-Hybrid-AI-System/issues)
- **Documentação**: [CWB Hub Docs](https://github.com/projetosdavidsimer/CWB-Hub-Hybrid-AI-System)
- **Email**: suporte@cwb-hub.com

## 🎉 Exemplos de Uso

### Análise de Projeto React

```
🏗️ Analisando projeto React...

✅ Estrutura bem organizada
✅ Componentes funcionais modernos
⚠️ Faltam testes unitários
💡 Sugestão: Implementar React Testing Library
```

### Revisão de Código

```
🔍 Revisando função de autenticação...

✅ Lógica correta
⚠️ Falta validação de entrada
🔒 Considere hash mais seguro para senhas
📈 Performance: Use useMemo para cálculos pesados
```

### Consultoria Arquitetural

```
🏛️ Consultoria sobre Microserviços...

📋 Análise da situação atual
🎯 Padrões recomendados
⚡ Estratégias de escalabilidade
🔐 Considerações de segurança
```

---

**Desenvolvido pela equipe CWB Hub - onde inovação e tecnologia se encontram.**