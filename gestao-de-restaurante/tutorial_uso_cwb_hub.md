# 🎯 Tutorial: Como Usar CWB Hub no Seu Projeto

**Criado por: David Simer**  
*Tutorial prático para usar o CWB Hub Hybrid AI System*

---

## 📋 **Cenário Real: Você no VSCode**

Você está na pasta `gestao-de-restaurante` com o VSCode aberto e quer usar o **CWB Hub Hybrid AI System** para desenvolver seu projeto.

---

## 🚀 **Passo a Passo Prático**

### **1. Estrutura do Projeto**

```
📁 Homem da Casa/
├── 📁 src/                    ← CWB Hub Hybrid AI System
│   ├── 📁 core/
│   ├── 📁 agents/
│   └── 📁 utils/
├── 📁 gestao-de-restaurante/  ← SEU PROJETO AQUI
│   ├── cwb_hub_client.py
│   ├── tutorial_uso_cwb_hub.md
│   └── README.md
```

### **2. Como Executar (3 Opções)**

#### **Opção A: Executar do Diretório Pai**
```bash
# No terminal, volte para a pasta pai
cd "c:\Users\David\Desktop\Homem da Casa"

# Execute o demo do seu projeto
python demo_system.py
```

#### **Opção B: Usar Python Path**
```bash
# Na pasta do seu projeto
cd gestao-de-restaurante

# Executar com PYTHONPATH
set PYTHONPATH=..\src && python cwb_hub_client.py
```

#### **Opção C: Script Direto (Recomendado)**
```bash
# Na pasta raiz do CWB Hub
cd "c:\Users\David\Desktop\Homem da Casa"

# Executar demo específico para restaurante
python -c "
import asyncio
import sys
sys.path.insert(0, 'src')
from core.hybrid_ai_orchestrator import HybridAIOrchestrator

async def demo_restaurante():
    print('🏢 CWB HUB - PROJETO RESTAURANTE')
    print('👨‍💻 Criado por: David Simer')
    print('='*50)
    
    orchestrator = HybridAIOrchestrator()
    await orchestrator.initialize_agents()
    
    plano = '''
    PROJETO: Sistema de Gestão de Restaurante
    CRIADO POR: David Simer
    
    Preciso de um sistema que:
    - Controle pedidos digitalmente
    - Tenha app para garçons
    - Gerencie estoque
    - Gere relatórios de vendas
    - Integre com WhatsApp para delivery
    
    Orçamento moderado, cronograma de 3 meses para MVP.
    '''
    
    response = await orchestrator.process_request(plano)
    print('📥 RESPOSTA DA EQUIPE:')
    print('='*50)
    print(response)
    
    await orchestrator.shutdown()

asyncio.run(demo_restaurante())
"
```

---

## 💡 **Exemplo de Uso Simples**

### **Seu Plano de Negócio:**
```
SISTEMA DE GESTÃO DE RESTAURANTE

OBJETIVO:
Automatizar meu restaurante familiar

FUNCIONALIDADES:
1. Controle de pedidos
2. App para garçons  
3. Gestão de estoque
4. Relatórios financeiros
5. Delivery via WhatsApp

CRONOGRAMA: 3 meses
ORÇAMENTO: Moderado
```

### **O que a Equipe CWB Hub vai entregar:**

#### 👩‍💼 **Ana (CTO) - Estratégia:**
- Análise de viabilidade
- Roadmap tecnológico
- ROI esperado

#### 👨‍💻 **Carlos (Arquiteto) - Arquitetura:**
- Estrutura do banco de dados
- APIs necessárias
- Escalabilidade

#### 👩‍💻 **Sofia (Full Stack) - Desenvolvimento:**
- Tecnologias recomendadas (React, Node.js, etc.)
- Estrutura do código
- Cronograma de desenvolvimento

#### 👨‍📱 **Gabriel (Mobile) - App:**
- App nativo ou híbrido
- Funcionalidades offline
- Interface para garçons

#### 👩‍🎨 **Isabella (UX/UI) - Design:**
- Wireframes
- Interface intuitiva
- Experiência do usuário

#### 👨‍🔬 **Lucas (QA) - Testes:**
- Plano de testes
- Automação
- Controle de qualidade

#### 👩‍🔧 **Mariana (DevOps) - Infraestrutura:**
- Hospedagem (AWS, Google Cloud)
- Backup e segurança
- Deploy automatizado

#### 👨‍📊 **Pedro (PM) - Gestão:**
- Cronograma detalhado
- Marcos e entregas
- Gestão de recursos

---

## 🔧 **Resolvendo Problemas de Importação**

### **Problema:** `reportMissingImports`

**Solução 1: Configurar VSCode**
```json
// .vscode/settings.json
{
    "python.analysis.extraPaths": ["../src"],
    "python.defaultInterpreterPath": "python"
}
```

**Solução 2: Executar da Pasta Correta**
```bash
# Sempre execute da pasta raiz do CWB Hub
cd "c:\Users\David\Desktop\Homem da Casa"
python demo_system.py
```

**Solução 3: Usar PYTHONPATH**
```bash
set PYTHONPATH=c:\Users\David\Desktop\Homem da Casa\src
python seu_script.py
```

---

## 🎯 **Fluxo de Trabalho Recomendado**

### **1. Preparar Plano de Negócio**
- Defina objetivos claros
- Liste funcionalidades desejadas
- Estabeleça cronograma e orçamento

### **2. Executar CWB Hub**
```bash
cd "c:\Users\David\Desktop\Homem da Casa"
python demo_system.py
```

### **3. Fornecer Seu Plano**
- Cole seu plano quando solicitado
- Seja específico sobre necessidades

### **4. Receber Análise Completa**
- 8 profissionais analisam seu projeto
- Solução integrada e detalhada

### **5. Dar Feedback**
- Comente sobre orçamento, cronograma
- Priorize funcionalidades
- Ajuste requisitos

### **6. Receber Solução Refinada**
- Proposta ajustada ao seu feedback
- Plano de implementação detalhado

---

## 📊 **Exemplo de Resultado**

Após usar o CWB Hub, você terá:

✅ **Análise técnica completa**  
✅ **Arquitetura do sistema**  
✅ **Tecnologias recomendadas**  
✅ **Cronograma detalhado**  
✅ **Estimativas de custo**  
✅ **Plano de testes**  
✅ **Estratégia de deploy**  
✅ **Gestão do projeto**  

---

## 🎉 **Resultado Final**

Você sairá com um **plano completo** para desenvolver seu sistema de gestão de restaurante, criado por uma equipe de 8 profissionais sênior trabalhando em colaboração!

---

## 🔗 **Links Úteis**

- **Repositório:** https://github.com/projetosdavidsimer/CWB-Hub-Hybrid-AI-System
- **Documentação:** README.md na pasta raiz
- **Créditos:** CREDITS.md

---

**🏢 Powered by CWB Hub Hybrid AI System**  
**👨‍💻 Criado por David Simer**