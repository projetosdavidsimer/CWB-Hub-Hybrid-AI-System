"use strict";
/**
 * Provider para histórico de consultas
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
exports.HistoryProvider = void 0;
const vscode = __importStar(require("vscode"));
class HistoryProvider {
    constructor(context) {
        this._onDidChangeTreeData = new vscode.EventEmitter();
        this.onDidChangeTreeData = this._onDidChangeTreeData.event;
        this.history = [];
        this.context = context;
        this.loadHistory();
    }
    refresh() {
        this._onDidChangeTreeData.fire();
    }
    addToHistory(item) {
        const historyItem = {
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
    getIconForType(type) {
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
    getTreeItem(element) {
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
    getChildren(element) {
        if (!element) {
            return Promise.resolve(this.history);
        }
        return Promise.resolve([]);
    }
    getParent(element) {
        return null;
    }
    formatTimestamp(timestamp) {
        const now = new Date();
        const diff = now.getTime() - timestamp.getTime();
        const minutes = Math.floor(diff / 60000);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        if (days > 0) {
            return `${days}d atrás`;
        }
        else if (hours > 0) {
            return `${hours}h atrás`;
        }
        else if (minutes > 0) {
            return `${minutes}m atrás`;
        }
        else {
            return 'agora';
        }
    }
    saveHistory() {
        this.context.globalState.update('cwb-hub.history', this.history);
    }
    loadHistory() {
        const saved = this.context.globalState.get('cwb-hub.history', []);
        this.history = saved.map(item => ({
            ...item,
            timestamp: new Date(item.timestamp)
        }));
    }
    clearHistory() {
        this.history = [];
        this.saveHistory();
        this.refresh();
    }
}
exports.HistoryProvider = HistoryProvider;
//# sourceMappingURL=historyProvider.js.map