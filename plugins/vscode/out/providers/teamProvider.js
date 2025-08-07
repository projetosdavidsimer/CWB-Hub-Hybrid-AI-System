"use strict";
/**
 * Provider para visualização da equipe CWB Hub
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.TeamProvider = void 0;
const vscode = __importStar(require("vscode"));
class TeamProvider {
    constructor() {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this.teamMembers = [
            {
                id: 'ana_beatriz_costa',
                name: 'Ana Beatriz Costa',
                role: 'CTO',
                status: 'online',
                expertise: 'Estratégia & Inovação',
                icon: 'person-filled'
            },
            {
                id: 'carlos_eduardo_santos',
                name: 'Carlos Eduardo Santos',
                role: 'Arquiteto de Software',
                status: 'online',
                expertise: 'Arquitetura & Escalabilidade',
                icon: 'tools'
            },
            {
                id: 'sofia_oliveira',
                name: 'Sofia Oliveira',
                role: 'Engenheira Full Stack',
                status: 'online',
                expertise: 'Web & SaaS',
                icon: 'code'
            },
            {
                id: 'gabriel_mendes',
                name: 'Gabriel Mendes',
                role: 'Engenheiro Mobile',
                status: 'online',
                expertise: 'iOS & Android',
                icon: 'device-mobile'
            },
            {
                id: 'isabella_santos',
                name: 'Isabella Santos',
                role: 'Designer UX/UI',
                status: 'online',
                expertise: 'Experiência do Usuário',
                icon: 'paintcan'
            },
            {
                id: 'lucas_pereira',
                name: 'Lucas Pereira',
                role: 'Engenheiro QA',
                status: 'online',
                expertise: 'Qualidade & Testes',
                icon: 'verified'
            },
            {
                id: 'mariana_rodrigues',
                name: 'Mariana Rodrigues',
                role: 'Engenheira DevOps',
                status: 'online',
                expertise: 'Infraestrutura & Dados',
                icon: 'server'
            },
            {
                id: 'pedro_henrique_almeida',
                name: 'Pedro Henrique Almeida',
                role: 'Project Manager',
                status: 'online',
                expertise: 'Metodologias Ágeis',
                icon: 'organization'
            }
        ];
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    getTreeItem(element) {
        const item = new vscode.TreeItem(element.name, vscode.TreeItemCollapsibleState.None);
        item.description = element.role;
        item.tooltip = `${element.name} - ${element.role}\n${element.expertise}`;
        item.iconPath = new vscode.ThemeIcon(element.icon, element.status === 'online' ? new vscode.ThemeColor('charts.green') : undefined);
        item.contextValue = 'teamMember';
        item.command = {
            command: 'cwb-hub.consultMember',
            title: 'Consultar',
            arguments: [element]
        };
        return item;
    }
    getChildren(element) {
        if (!element) {
            return Promise.resolve(this.teamMembers);
        }
        return Promise.resolve([]);
    }
    getParent(element) {
        return null;
    }
}
exports.TeamProvider = TeamProvider;
//# sourceMappingURL=teamProvider.js.map