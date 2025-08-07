/**
 * Cliente da API CWB Hub
 * Comunicação com a equipe de 8 profissionais sênior
 */

import axios, { AxiosInstance } from 'axios';
import * as vscode from 'vscode';

export interface ProjectInfo {
    name: string;
    path: string;
    fileCount: number;
    languages: string[];
    hasPackageJson: boolean;
    hasPomXml: boolean;
    hasRequirementsTxt: boolean;
    hasDockerfile: boolean;
}

export interface EditorContext {
    fileName: string;
    language: string;
    lineCount: number;
    selection?: {
        start: number;
        end: number;
    };
}

export interface CodeContext {
    language: string;
    fileName: string;
}

export interface TeamMember {
    id: string;
    name: string;
    role: string;
    description: string;
    skills: string[];
    avatar?: string;
}

export interface CWBHubResponse {
    success: boolean;
    data: any;
    session_id?: string;
    agents_involved: string[];
    confidence: number;
    timestamp: string;
}

export class CWBHubClient {
    private client: AxiosInstance;
    private apiKey: string = '';
    private baseURL: string = 'http://localhost:8000';

    constructor() {
        this.updateConfiguration();
        
        this.client = axios.create({
            timeout: 30000, // 30 segundos
            headers: {
                'Content-Type': 'application/json',
                'User-Agent': 'CWB-Hub-VSCode-Extension/1.0.0'
            }
        });

        // Interceptor para adicionar API key
        this.client.interceptors.request.use((config) => {
            if (this.apiKey) {
                config.headers['Authorization'] = `Bearer ${this.apiKey}`;
            }
            return config;
        });

        // Interceptor para tratar erros
        this.client.interceptors.response.use(
            (response) => response,
            (error) => {
                console.error('CWB Hub API Error:', error);
                if (error.response?.status === 401) {
                    vscode.window.showErrorMessage('❌ API Key inválida. Verifique as configurações.');
                } else if (error.response?.status === 429) {
                    vscode.window.showWarningMessage('⚠️ Muitas requisições. Tente novamente em alguns segundos.');
                } else if (error.code === 'ECONNREFUSED') {
                    vscode.window.showErrorMessage('❌ Não foi possível conectar ao CWB Hub. Verifique se o serviço está rodando.');
                }
                throw error;
            }
        );

        // Escutar mudanças na configuração
        vscode.workspace.onDidChangeConfiguration((e) => {
            if (e.affectsConfiguration('cwb-hub')) {
                this.updateConfiguration();
            }
        });
    }

    private updateConfiguration() {
        const config = vscode.workspace.getConfiguration('cwb-hub');
        this.baseURL = config.get<string>('apiEndpoint') || 'http://localhost:8000';
        this.apiKey = config.get<string>('apiKey') || '';
        
        if (this.client) {
            this.client.defaults.baseURL = this.baseURL;
        }
    }

    /**
     * Analisa um projeto com a equipe CWB Hub
     */
    async analyzeProject(projectInfo: ProjectInfo): Promise<CWBHubResponse> {
        const request = `
ANÁLISE DE PROJETO - VSCODE EXTENSION
CRIADO POR: CWB Hub VSCode Extension

INFORMAÇÕES DO PROJETO:
- Nome: ${projectInfo.name}
- Arquivos: ${projectInfo.fileCount}
- Linguagens: ${projectInfo.languages.join(', ')}
- Tecnologias detectadas:
  ${projectInfo.hasPackageJson ? '✅ Node.js (package.json)' : ''}
  ${projectInfo.hasPomXml ? '✅ Java (pom.xml)' : ''}
  ${projectInfo.hasRequirementsTxt ? '✅ Python (requirements.txt)' : ''}
  ${projectInfo.hasDockerfile ? '✅ Docker (Dockerfile)' : ''}

SOLICITAÇÃO:
Por favor, analisem este projeto e forneçam:
1. Avaliação da arquitetura atual
2. Sugestões de melhorias
3. Boas práticas recomendadas
4. Possíveis problemas identificados
5. Próximos passos sugeridos

Considerem as tecnologias detectadas e forneçam uma análise abrangente da equipe CWB Hub.
        `;

        try {
            const response = await this.client.post('/analyze', {
                request: request.trim(),
                context: {
                    source: 'vscode-extension',
                    project_info: projectInfo
                }
            });

            return {
                success: true,
                data: response.data.response || response.data,
                session_id: response.data.session_id,
                agents_involved: response.data.agents_involved || [],
                confidence: response.data.confidence || 0.9,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            throw new Error(`Erro na análise do projeto: ${error}`);
        }
    }

    /**
     * Faz uma pergunta para a equipe CWB Hub
     */
    async askTeam(question: string, context?: EditorContext | null): Promise<CWBHubResponse> {
        let request = `
CONSULTA À EQUIPE CWB HUB - VSCODE EXTENSION
CRIADO POR: CWB Hub VSCode Extension

PERGUNTA:
${question}
        `;

        if (context) {
            request += `

CONTEXTO DO EDITOR:
- Arquivo: ${context.fileName}
- Linguagem: ${context.language}
- Linhas: ${context.lineCount}
${context.selection ? `- Seleção: linhas ${context.selection.start}-${context.selection.end}` : ''}
            `;
        }

        request += `

Por favor, forneçam uma resposta detalhada da equipe CWB Hub considerando a expertise de cada profissional.
        `;

        try {
            const response = await this.client.post('/analyze', {
                request: request.trim(),
                context: {
                    source: 'vscode-extension',
                    editor_context: context
                }
            });

            return {
                success: true,
                data: response.data.response || response.data,
                session_id: response.data.session_id,
                agents_involved: response.data.agents_involved || [],
                confidence: response.data.confidence || 0.9,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            throw new Error(`Erro na consulta à equipe: ${error}`);
        }
    }

    /**
     * Solicita revisão de código
     */
    async reviewCode(code: string, context: CodeContext): Promise<CWBHubResponse> {
        const request = `
REVISÃO DE CÓDIGO - VSCODE EXTENSION
CRIADO POR: CWB Hub VSCode Extension

ARQUIVO: ${context.fileName}
LINGUAGEM: ${context.language}

CÓDIGO PARA REVISÃO:
\`\`\`${context.language}
${code}
\`\`\`

SOLICITAÇÃO:
Por favor, revisem este código e forneçam:
1. Análise de qualidade do código
2. Possíveis bugs ou problemas
3. Sugestões de melhorias
4. Boas práticas não seguidas
5. Otimizações de performance
6. Considerações de segurança

Considerem a expertise de cada membro da equipe CWB Hub para uma revisão completa.
        `;

        try {
            const response = await this.client.post('/analyze', {
                request: request.trim(),
                context: {
                    source: 'vscode-extension',
                    code_context: context,
                    code_length: code.length
                }
            });

            return {
                success: true,
                data: response.data.response || response.data,
                session_id: response.data.session_id,
                agents_involved: response.data.agents_involved || [],
                confidence: response.data.confidence || 0.9,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            throw new Error(`Erro na revisão de código: ${error}`);
        }
    }

    /**
     * Solicita consultoria arquitetural
     */
    async getArchitectureAdvice(topic: string, details: string): Promise<CWBHubResponse> {
        const request = `
CONSULTORIA ARQUITETURAL - VSCODE EXTENSION
CRIADO POR: CWB Hub VSCode Extension

TÓPICO: ${topic}

DETALHES:
${details}

SOLICITAÇÃO:
Por favor, forneçam consultoria arquitetural especializada sobre este tópico:
1. Análise da situação atual
2. Melhores práticas recomendadas
3. Padrões de design aplicáveis
4. Considerações de escalabilidade
5. Aspectos de segurança
6. Implementação sugerida
7. Riscos e mitigações

Considerem a expertise dos arquitetos e especialistas da equipe CWB Hub.
        `;

        try {
            const response = await this.client.post('/analyze', {
                request: request.trim(),
                context: {
                    source: 'vscode-extension',
                    consultation_topic: topic
                }
            });

            return {
                success: true,
                data: response.data.response || response.data,
                session_id: response.data.session_id,
                agents_involved: response.data.agents_involved || [],
                confidence: response.data.confidence || 0.9,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            throw new Error(`Erro na consultoria arquitetural: ${error}`);
        }
    }

    /**
     * Obtém informações da equipe CWB Hub
     */
    async getTeamInfo(): Promise<TeamMember[]> {
        try {
            // Como não temos endpoint específico, retornamos informações estáticas da equipe
            return [
                {
                    id: 'ana_beatriz_costa',
                    name: 'Dra. Ana Beatriz Costa',
                    role: 'Chief Technology Officer (CTO)',
                    description: 'Visionária tecnológica que define estratégias e lidera inovação na CWB Hub',
                    skills: ['Liderança estratégica', 'Arquitetura de Software', 'Inovação Tecnológica', 'Cloud Computing', 'Machine Learning/IA']
                },
                {
                    id: 'carlos_eduardo_santos',
                    name: 'Carlos Eduardo Santos',
                    role: 'Arquiteto de Software Sênior',
                    description: 'Especialista em arquitetura de sistemas complexos e escaláveis',
                    skills: ['Arquitetura de Software', 'Microserviços', 'Design Patterns', 'Performance', 'Escalabilidade']
                },
                {
                    id: 'sofia_oliveira',
                    name: 'Sofia Oliveira',
                    role: 'Engenheira Full Stack',
                    description: 'Especialista em desenvolvimento web moderno e SaaS',
                    skills: ['React/Vue.js', 'Node.js', 'APIs REST', 'Banco de Dados', 'DevOps']
                },
                {
                    id: 'gabriel_mendes',
                    name: 'Gabriel Mendes',
                    role: 'Engenheiro Mobile',
                    description: 'Especialista em desenvolvimento mobile nativo e híbrido',
                    skills: ['iOS/Swift', 'Android/Kotlin', 'React Native', 'Flutter', 'Mobile UX']
                },
                {
                    id: 'isabella_santos',
                    name: 'Isabella Santos',
                    role: 'Designer UX/UI Sênior',
                    description: 'Especialista em experiência do usuário e design de interfaces',
                    skills: ['UX Research', 'UI Design', 'Prototipagem', 'Design Systems', 'Usabilidade']
                },
                {
                    id: 'lucas_pereira',
                    name: 'Lucas Pereira',
                    role: 'Engenheiro de QA Automation',
                    description: 'Especialista em qualidade de software e automação de testes',
                    skills: ['Automação de Testes', 'CI/CD', 'Performance Testing', 'Security Testing', 'Quality Assurance']
                },
                {
                    id: 'mariana_rodrigues',
                    name: 'Mariana Rodrigues',
                    role: 'Engenheira DevOps/Dados',
                    description: 'Especialista em infraestrutura, dados e operações',
                    skills: ['Kubernetes', 'Docker', 'AWS/Azure', 'Big Data', 'Monitoramento']
                },
                {
                    id: 'pedro_henrique_almeida',
                    name: 'Pedro Henrique Almeida',
                    role: 'Agile Project Manager',
                    description: 'Especialista em metodologias ágeis e gestão de projetos',
                    skills: ['Scrum/Kanban', 'Gestão de Equipes', 'Planejamento', 'Stakeholder Management', 'Métricas']
                }
            ];
        } catch (error) {
            throw new Error(`Erro ao obter informações da equipe: ${error}`);
        }
    }

    /**
     * Verifica se a API está disponível
     */
    async checkHealth(): Promise<boolean> {
        try {
            const response = await this.client.get('/health');
            return response.status === 200;
        } catch (error) {
            return false;
        }
    }

    /**
     * Itera uma solução existente
     */
    async iterateSolution(sessionId: string, feedback: string): Promise<CWBHubResponse> {
        try {
            const response = await this.client.post(`/iterate/${sessionId}`, {
                feedback: feedback
            });

            return {
                success: true,
                data: response.data.response || response.data,
                session_id: sessionId,
                agents_involved: response.data.agents_involved || [],
                confidence: response.data.confidence || 0.9,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            throw new Error(`Erro na iteração da solução: ${error}`);
        }
    }
}