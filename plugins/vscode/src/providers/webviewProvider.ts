/**
 * Provider para webviews do CWB Hub
 */

export class WebviewProvider {
    
    static getTeamHtml(teamInfo: any[]): string {
        return `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Equipe CWB Hub</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            font-size: 24px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
            margin-bottom: 10px;
        }
        .subtitle {
            color: var(--vscode-descriptionForeground);
            font-size: 14px;
        }
        .team-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .member-card {
            background: var(--vscode-editor-inactiveSelectionBackground);
            border: 1px solid var(--vscode-panel-border);
            border-radius: 8px;
            padding: 20px;
            transition: transform 0.2s;
        }
        .member-card:hover {
            transform: translateY(-2px);
            border-color: var(--vscode-textLink-foreground);
        }
        .member-header {
            display: flex;
            align-items: center;
            margin-bottom: 15px;
        }
        .member-avatar {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: var(--vscode-textLink-foreground);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 18px;
            margin-right: 15px;
        }
        .member-info h3 {
            margin: 0;
            color: var(--vscode-editor-foreground);
            font-size: 16px;
        }
        .member-info .role {
            color: var(--vscode-textLink-foreground);
            font-size: 14px;
            margin: 2px 0;
        }
        .member-description {
            color: var(--vscode-descriptionForeground);
            font-size: 13px;
            line-height: 1.4;
            margin-bottom: 15px;
        }
        .skills {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }
        .skill-tag {
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
        }
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            background: #4CAF50;
            margin-left: auto;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">👥 Equipe CWB Hub</div>
        <div class="subtitle">8 Profissionais Sênior de IA Híbrida</div>
    </div>
    
    <div class="team-grid">
        ${teamInfo.map(member => `
            <div class="member-card">
                <div class="member-header">
                    <div class="member-avatar">
                        ${member.name.split(' ').map((n: string) => n[0]).join('').substring(0, 2)}
                    </div>
                    <div class="member-info">
                        <h3>${member.name}</h3>
                        <div class="role">${member.role}</div>
                    </div>
                    <div class="status-indicator"></div>
                </div>
                <div class="member-description">
                    ${member.description}
                </div>
                <div class="skills">
                    ${member.skills.slice(0, 4).map((skill: string) => `
                        <span class="skill-tag">${skill}</span>
                    `).join('')}
                </div>
            </div>
        `).join('')}
    </div>
</body>
</html>`;
    }

    static getAnalysisHtml(analysis: any): string {
        return `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análise do Projeto - CWB Hub</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            line-height: 1.6;
        }
        .header {
            border-bottom: 2px solid var(--vscode-textLink-foreground);
            padding-bottom: 15px;
            margin-bottom: 25px;
        }
        .title {
            font-size: 24px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
            margin: 0;
        }
        .subtitle {
            color: var(--vscode-descriptionForeground);
            margin: 5px 0 0 0;
        }
        .content {
            white-space: pre-wrap;
            background: var(--vscode-textCodeBlock-background);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid var(--vscode-textLink-foreground);
        }
        .metadata {
            margin-top: 20px;
            padding: 15px;
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 8px;
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }
        .confidence {
            display: inline-block;
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">🏗️ Análise do Projeto</h1>
        <p class="subtitle">Análise completa da equipe CWB Hub</p>
    </div>
    
    <div class="content">${analysis.data || analysis}</div>
    
    <div class="metadata">
        <strong>Sessão:</strong> ${analysis.session_id || 'N/A'}<br>
        <strong>Confiança:</strong> <span class="confidence">${Math.round((analysis.confidence || 0.9) * 100)}%</span><br>
        <strong>Timestamp:</strong> ${analysis.timestamp || new Date().toLocaleString()}<br>
        <strong>Agentes Envolvidos:</strong> ${(analysis.agents_involved || []).length || 8} profissionais
    </div>
</body>
</html>`;
    }

    static getResponseHtml(response: any): string {
        return `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resposta da Equipe - CWB Hub</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            line-height: 1.6;
        }
        .header {
            border-bottom: 2px solid var(--vscode-textLink-foreground);
            padding-bottom: 15px;
            margin-bottom: 25px;
        }
        .title {
            font-size: 24px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
            margin: 0;
        }
        .subtitle {
            color: var(--vscode-descriptionForeground);
            margin: 5px 0 0 0;
        }
        .content {
            white-space: pre-wrap;
            background: var(--vscode-textCodeBlock-background);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid var(--vscode-textLink-foreground);
        }
        .metadata {
            margin-top: 20px;
            padding: 15px;
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 8px;
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }
        .confidence {
            display: inline-block;
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">👥 Resposta da Equipe</h1>
        <p class="subtitle">Consultoria especializada da equipe CWB Hub</p>
    </div>
    
    <div class="content">${response.data || response}</div>
    
    <div class="metadata">
        <strong>Sessão:</strong> ${response.session_id || 'N/A'}<br>
        <strong>Confiança:</strong> <span class="confidence">${Math.round((response.confidence || 0.9) * 100)}%</span><br>
        <strong>Timestamp:</strong> ${response.timestamp || new Date().toLocaleString()}<br>
        <strong>Agentes Envolvidos:</strong> ${(response.agents_involved || []).length || 8} profissionais
    </div>
</body>
</html>`;
    }

    static getReviewHtml(review: any): string {
        return `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Revisão de Código - CWB Hub</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            line-height: 1.6;
        }
        .header {
            border-bottom: 2px solid var(--vscode-textLink-foreground);
            padding-bottom: 15px;
            margin-bottom: 25px;
        }
        .title {
            font-size: 24px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
            margin: 0;
        }
        .subtitle {
            color: var(--vscode-descriptionForeground);
            margin: 5px 0 0 0;
        }
        .content {
            white-space: pre-wrap;
            background: var(--vscode-textCodeBlock-background);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid var(--vscode-textLink-foreground);
        }
        .metadata {
            margin-top: 20px;
            padding: 15px;
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 8px;
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }
        .confidence {
            display: inline-block;
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">🔍 Revisão de Código</h1>
        <p class="subtitle">Análise detalhada da equipe CWB Hub</p>
    </div>
    
    <div class="content">${review.data || review}</div>
    
    <div class="metadata">
        <strong>Sessão:</strong> ${review.session_id || 'N/A'}<br>
        <strong>Confiança:</strong> <span class="confidence">${Math.round((review.confidence || 0.9) * 100)}%</span><br>
        <strong>Timestamp:</strong> ${review.timestamp || new Date().toLocaleString()}<br>
        <strong>Agentes Envolvidos:</strong> ${(review.agents_involved || []).length || 8} profissionais
    </div>
</body>
</html>`;
    }

    static getArchitectureHtml(advice: any): string {
        return `
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Consultoria Arquitetural - CWB Hub</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            line-height: 1.6;
        }
        .header {
            border-bottom: 2px solid var(--vscode-textLink-foreground);
            padding-bottom: 15px;
            margin-bottom: 25px;
        }
        .title {
            font-size: 24px;
            font-weight: bold;
            color: var(--vscode-textLink-foreground);
            margin: 0;
        }
        .subtitle {
            color: var(--vscode-descriptionForeground);
            margin: 5px 0 0 0;
        }
        .content {
            white-space: pre-wrap;
            background: var(--vscode-textCodeBlock-background);
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid var(--vscode-textLink-foreground);
        }
        .metadata {
            margin-top: 20px;
            padding: 15px;
            background: var(--vscode-editor-inactiveSelectionBackground);
            border-radius: 8px;
            font-size: 12px;
            color: var(--vscode-descriptionForeground);
        }
        .confidence {
            display: inline-block;
            background: var(--vscode-badge-background);
            color: var(--vscode-badge-foreground);
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1 class="title">🏛️ Consultoria Arquitetural</h1>
        <p class="subtitle">Expertise especializada da equipe CWB Hub</p>
    </div>
    
    <div class="content">${advice.data || advice}</div>
    
    <div class="metadata">
        <strong>Sessão:</strong> ${advice.session_id || 'N/A'}<br>
        <strong>Confiança:</strong> <span class="confidence">${Math.round((advice.confidence || 0.9) * 100)}%</span><br>
        <strong>Timestamp:</strong> ${advice.timestamp || new Date().toLocaleString()}<br>
        <strong>Agentes Envolvidos:</strong> ${(advice.agents_involved || []).length || 8} profissionais
    </div>
</body>
</html>`;
    }
}