/**
 * Provider para visualização da equipe CWB Hub
 */

import * as vscode from 'vscode';

export class TeamProvider implements vscode.TreeDataProvider<TeamMember> {
    private _onDidChangeTreeData: vscode.EventEmitter<TeamMember | undefined | null | void> = new vscode.EventEmitter<TeamMember | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<TeamMember | undefined | null | void> = this._onDidChangeTreeData.event;

    private teamMembers: TeamMember[] = [
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

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: TeamMember): vscode.TreeItem {
        const item = new vscode.TreeItem(element.name, vscode.TreeItemCollapsibleState.None);
        
        item.description = element.role;
        item.tooltip = `${element.name} - ${element.role}\n${element.expertise}`;
        item.iconPath = new vscode.ThemeIcon(element.icon, 
            element.status === 'online' ? new vscode.ThemeColor('charts.green') : undefined
        );
        
        item.contextValue = 'teamMember';
        item.command = {
            command: 'cwb-hub.consultMember',
            title: 'Consultar',
            arguments: [element]
        };

        return item;
    }

    getChildren(element?: TeamMember): Thenable<TeamMember[]> {
        if (!element) {
            return Promise.resolve(this.teamMembers);
        }
        return Promise.resolve([]);
    }

    getParent(element: TeamMember): vscode.ProviderResult<TeamMember> {
        return null;
    }
}

interface TeamMember {
    id: string;
    name: string;
    role: string;
    status: 'online' | 'offline' | 'busy';
    expertise: string;
    icon: string;
}