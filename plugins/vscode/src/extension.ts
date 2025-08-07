/**
 * CWB Hub AI Assistant - VSCode Extension
 * Equipe de 8 profissionais sênior de IA híbrida
 * Criado por: David Simer
 */

import * as vscode from 'vscode';
import { CWBHubClient } from './cwbHubClient';
import { TeamProvider } from './providers/teamProvider';
import { HistoryProvider } from './providers/historyProvider';
import { WebviewProvider } from './providers/webviewProvider';

let cwbHubClient: CWBHubClient;
let teamProvider: TeamProvider;
let historyProvider: HistoryProvider;

export function activate(context: vscode.ExtensionContext) {
    console.log('🚀 CWB Hub AI Assistant ativado!');

    // Inicializar cliente da API
    cwbHubClient = new CWBHubClient();
    
    // Inicializar providers
    teamProvider = new TeamProvider();
    historyProvider = new HistoryProvider(context);
    
    // Registrar providers de visualização
    vscode.window.registerTreeDataProvider('cwb-hub-team', teamProvider);
    vscode.window.registerTreeDataProvider('cwb-hub-history', historyProvider);

    // Registrar comandos
    registerCommands(context);

    // Mostrar mensagem de boas-vindas
    showWelcomeMessage();

    // Verificar configuração
    checkConfiguration();
}

function registerCommands(context: vscode.ExtensionContext) {
    // Comando: Analisar Projeto
    const analyzeProject = vscode.commands.registerCommand('cwb-hub.analyzeProject', async () => {
        await handleAnalyzeProject();
    });

    // Comando: Consultar Equipe
    const askTeam = vscode.commands.registerCommand('cwb-hub.askTeam', async () => {
        await handleAskTeam();
    });

    // Comando: Revisar Código
    const reviewCode = vscode.commands.registerCommand('cwb-hub.reviewCode', async () => {
        await handleReviewCode();
    });

    // Comando: Consultoria Arquitetural
    const architectureAdvice = vscode.commands.registerCommand('cwb-hub.architectureAdvice', async () => {
        await handleArchitectureAdvice();
    });

    // Comando: Mostrar Equipe
    const showTeam = vscode.commands.registerCommand('cwb-hub.showTeam', async () => {
        await handleShowTeam();
    });

    // Comando: Configurações
    const settings = vscode.commands.registerCommand('cwb-hub.settings', async () => {
        await handleSettings();
    });

    // Registrar todos os comandos
    context.subscriptions.push(
        analyzeProject,
        askTeam,
        reviewCode,
        architectureAdvice,
        showTeam,
        settings
    );
}

async function handleAnalyzeProject() {
    try {
        vscode.window.showInformationMessage('🏗️ Analisando projeto com a equipe CWB Hub...');

        const workspaceFolder = vscode.workspace.workspaceFolders?.[0];
        if (!workspaceFolder) {
            vscode.window.showErrorMessage('❌ Nenhum projeto aberto no workspace');
            return;
        }

        // Coletar informações do projeto
        const projectInfo = await collectProjectInfo(workspaceFolder);
        
        // Enviar para análise da equipe CWB Hub
        const analysis = await cwbHubClient.analyzeProject(projectInfo);
        
        // Mostrar resultado
        await showAnalysisResult(analysis);
        
        // Adicionar ao histórico
        historyProvider.addToHistory({
            type: 'project-analysis',
            timestamp: new Date(),
            summary: 'Análise de projeto',
            result: analysis
        });

    } catch (error) {
        vscode.window.showErrorMessage(`❌ Erro na análise: ${error}`);
    }
}

async function handleAskTeam() {
    try {
        const question = await vscode.window.showInputBox({
            prompt: '💬 Qual sua pergunta para a equipe CWB Hub?',
            placeHolder: 'Ex: Como implementar autenticação JWT em Node.js?'
        });

        if (!question) {
            return;
        }

        vscode.window.showInformationMessage('👥 Consultando equipe CWB Hub...');

        // Obter contexto do editor atual
        const context = getCurrentEditorContext();
        
        // Consultar equipe
        const response = await cwbHubClient.askTeam(question, context);
        
        // Mostrar resposta
        await showTeamResponse(response);
        
        // Adicionar ao histórico
        historyProvider.addToHistory({
            type: 'team-consultation',
            timestamp: new Date(),
            summary: question.substring(0, 50) + '...',
            result: response
        });

    } catch (error) {
        vscode.window.showErrorMessage(`❌ Erro na consulta: ${error}`);
    }
}

async function handleReviewCode() {
    try {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('❌ Nenhum arquivo aberto para revisão');
            return;
        }

        const selection = editor.selection;
        const code = selection.isEmpty ? 
            editor.document.getText() : 
            editor.document.getText(selection);

        if (!code.trim()) {
            vscode.window.showErrorMessage('❌ Nenhum código selecionado para revisão');
            return;
        }

        vscode.window.showInformationMessage('🔍 Revisando código com a equipe CWB Hub...');

        // Revisar código
        const review = await cwbHubClient.reviewCode(code, {
            language: editor.document.languageId,
            fileName: editor.document.fileName
        });
        
        // Mostrar resultado da revisão
        await showCodeReview(review);
        
        // Adicionar ao histórico
        historyProvider.addToHistory({
            type: 'code-review',
            timestamp: new Date(),
            summary: `Revisão de ${editor.document.fileName}`,
            result: review
        });

    } catch (error) {
        vscode.window.showErrorMessage(`❌ Erro na revisão: ${error}`);
    }
}

async function handleArchitectureAdvice() {
    try {
        const options = [
            'Arquitetura de Software',
            'Padrões de Design',
            'Escalabilidade',
            'Performance',
            'Segurança',
            'DevOps e Infraestrutura',
            'Banco de Dados',
            'APIs e Microserviços'
        ];

        const selectedTopic = await vscode.window.showQuickPick(options, {
            placeHolder: '🏛️ Selecione o tópico para consultoria arquitetural'
        });

        if (!selectedTopic) {
            return;
        }

        const details = await vscode.window.showInputBox({
            prompt: `💭 Descreva sua questão sobre ${selectedTopic}`,
            placeHolder: 'Ex: Como estruturar microserviços para alta disponibilidade?'
        });

        if (!details) {
            return;
        }

        vscode.window.showInformationMessage('🏛️ Consultando arquitetos da equipe CWB Hub...');

        // Obter consultoria arquitetural
        const advice = await cwbHubClient.getArchitectureAdvice(selectedTopic, details);
        
        // Mostrar consultoria
        await showArchitectureAdvice(advice);
        
        // Adicionar ao histórico
        historyProvider.addToHistory({
            type: 'architecture-advice',
            timestamp: new Date(),
            summary: `${selectedTopic}: ${details.substring(0, 30)}...`,
            result: advice
        });

    } catch (error) {
        vscode.window.showErrorMessage(`❌ Erro na consultoria: ${error}`);
    }
}

async function handleShowTeam() {
    try {
        // Obter informações da equipe
        const teamInfo = await cwbHubClient.getTeamInfo();
        
        // Mostrar equipe em webview
        const panel = vscode.window.createWebviewPanel(
            'cwb-hub-team',
            '👥 Equipe CWB Hub',
            vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        panel.webview.html = WebviewProvider.getTeamHtml(teamInfo);

    } catch (error) {
        vscode.window.showErrorMessage(`❌ Erro ao carregar equipe: ${error}`);
    }
}

async function handleSettings() {
    // Abrir configurações da extensão
    vscode.commands.executeCommand('workbench.action.openSettings', 'cwb-hub');
}

async function collectProjectInfo(workspaceFolder: vscode.WorkspaceFolder) {
    // Coletar informações básicas do projeto
    const files = await vscode.workspace.findFiles('**/*', '**/node_modules/**', 100);
    
    return {
        name: workspaceFolder.name,
        path: workspaceFolder.uri.fsPath,
        fileCount: files.length,
        languages: getProjectLanguages(files),
        hasPackageJson: files.some(f => f.fsPath.endsWith('package.json')),
        hasPomXml: files.some(f => f.fsPath.endsWith('pom.xml')),
        hasRequirementsTxt: files.some(f => f.fsPath.endsWith('requirements.txt')),
        hasDockerfile: files.some(f => f.fsPath.endsWith('Dockerfile'))
    };
}

function getProjectLanguages(files: vscode.Uri[]): string[] {
    const extensions = new Set<string>();
    files.forEach(file => {
        const ext = file.fsPath.split('.').pop()?.toLowerCase();
        if (ext) {
            extensions.add(ext);
        }
    });
    return Array.from(extensions);
}

function getCurrentEditorContext() {
    const editor = vscode.window.activeTextEditor;
    if (!editor) {
        return null;
    }

    return {
        fileName: editor.document.fileName,
        language: editor.document.languageId,
        lineCount: editor.document.lineCount,
        selection: editor.selection.isEmpty ? undefined : {
            start: editor.selection.start.line,
            end: editor.selection.end.line
        }
    };
}

async function showAnalysisResult(analysis: any) {
    const panel = vscode.window.createWebviewPanel(
        'cwb-hub-analysis',
        '🏗️ Análise do Projeto - CWB Hub',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );

    panel.webview.html = WebviewProvider.getAnalysisHtml(analysis);
}

async function showTeamResponse(response: any) {
    const panel = vscode.window.createWebviewPanel(
        'cwb-hub-response',
        '👥 Resposta da Equipe CWB Hub',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );

    panel.webview.html = WebviewProvider.getResponseHtml(response);
}

async function showCodeReview(review: any) {
    const panel = vscode.window.createWebviewPanel(
        'cwb-hub-review',
        '🔍 Revisão de Código - CWB Hub',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );

    panel.webview.html = WebviewProvider.getReviewHtml(review);
}

async function showArchitectureAdvice(advice: any) {
    const panel = vscode.window.createWebviewPanel(
        'cwb-hub-architecture',
        '🏛️ Consultoria Arquitetural - CWB Hub',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );

    panel.webview.html = WebviewProvider.getArchitectureHtml(advice);
}

function showWelcomeMessage() {
    vscode.window.showInformationMessage(
        '🎉 CWB Hub AI Assistant ativado! Sua equipe de 8 profissionais sênior está pronta.',
        'Ver Equipe',
        'Configurar'
    ).then(selection => {
        if (selection === 'Ver Equipe') {
            vscode.commands.executeCommand('cwb-hub.showTeam');
        } else if (selection === 'Configurar') {
            vscode.commands.executeCommand('cwb-hub.settings');
        }
    });
}

function checkConfiguration() {
    const config = vscode.workspace.getConfiguration('cwb-hub');
    const apiEndpoint = config.get<string>('apiEndpoint');
    const apiKey = config.get<string>('apiKey');

    if (!apiEndpoint || !apiKey) {
        vscode.window.showWarningMessage(
            '⚠️ Configure o endpoint e chave da API do CWB Hub',
            'Configurar'
        ).then(selection => {
            if (selection === 'Configurar') {
                vscode.commands.executeCommand('cwb-hub.settings');
            }
        });
    }
}

export function deactivate() {
    console.log('👋 CWB Hub AI Assistant desativado');
}