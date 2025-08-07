/**
 * Provider para histórico de consultas
 */

import * as vscode from 'vscode';

export class HistoryProvider implements vscode.TreeDataProvider<HistoryItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<HistoryItem | undefined | null | void> = new vscode.EventEmitter<HistoryItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<HistoryItem | undefined | null | void> = this._onDidChangeTreeData.event;

    private history: HistoryItem[] = [];
    private context: vscode.ExtensionContext;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.loadHistory();
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    addToHistory(item: HistoryEntry): void {
        const historyItem: HistoryItem = {
            id: Date.now().toString(),
            type: item.type,
            summary: item.summary,
            timestamp: item.timestamp,
            result: item.result,
            icon: this.getIconForType(item.type)
        };

        this.history.unshift(historyItem);
        
        // Manter apenas os últimos 50 itens
        if (this.history.length > 50) {
            this.history = this.history.slice(0, 50);
        }

        this.saveHistory();
        this.refresh();
    }

    private getIconForType(type: string): string {
        switch (type) {
            case 'project-analysis':
                return 'project';
            case 'team-consultation':
                return 'comment-discussion';
            case 'code-review':
                return 'search';
            case 'architecture-advice':
                return 'organization';
            default:
                return 'history';
        }
    }

    getTreeItem(element: HistoryItem): vscode.TreeItem {
        const item = new vscode.TreeItem(element.summary, vscode.TreeItemCollapsibleState.None);
        
        item.description = this.formatTimestamp(element.timestamp);
        item.tooltip = `${element.summary}\n${element.timestamp.toLocaleString()}`;
        item.iconPath = new vscode.ThemeIcon(element.icon);
        item.contextValue = 'historyItem';
        
        item.command = {
            command: 'cwb-hub.showHistoryItem',
            title: 'Ver Resultado',
            arguments: [element]
        };

        return item;
    }

    getChildren(element?: HistoryItem): Thenable<HistoryItem[]> {
        if (!element) {
            return Promise.resolve(this.history);
        }
        return Promise.resolve([]);
    }

    getParent(element: HistoryItem): vscode.ProviderResult<HistoryItem> {
        return null;
    }

    private formatTimestamp(timestamp: Date): string {
        const now = new Date();
        const diff = now.getTime() - timestamp.getTime();
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);

        if (days > 0) {
            return `${days}d atrás`;
        } else if (hours > 0) {
            return `${hours}h atrás`;
        } else if (minutes > 0) {
            return `${minutes}m atrás`;
        } else {
            return 'agora';
        }
    }

    private saveHistory(): void {
        this.context.globalState.update('cwb-hub.history', this.history);
    }

    private loadHistory(): void {
        const saved = this.context.globalState.get<HistoryItem[]>('cwb-hub.history', []);
        this.history = saved.map(item => ({
            ...item,
            timestamp: new Date(item.timestamp)
        }));
    }

    clearHistory(): void {
        this.history = [];
        this.saveHistory();
        this.refresh();
    }
}

export interface HistoryEntry {
    type: 'project-analysis' | 'team-consultation' | 'code-review' | 'architecture-advice';
    timestamp: Date;
    summary: string;
    result: any;
}

interface HistoryItem extends HistoryEntry {
    id: string;
    icon: string;
}