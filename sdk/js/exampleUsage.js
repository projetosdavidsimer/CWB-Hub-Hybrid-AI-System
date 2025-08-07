// Exemplo de uso do SDK JavaScript do CWB Hub Hybrid AI System
const CWBHubClient = require('./cwbHubClient');

const API_URL = 'http://localhost:8000'; // Altere para o endpoint da sua API
const API_KEY = 'SUA_API_KEY_AQUI'; // Opcional, se necessário

const client = new CWBHubClient(API_URL, API_KEY);

async function main() {
  // Verificar status da API
  const health = await client.health();
  console.log('Status da API:', health);

  // Enviar projeto para análise
  const projectData = {
    title: 'App Mobile de Gestão de Projetos',
    description: 'Preciso desenvolver um app mobile para gestão de projetos com colaboração em tempo real, dashboard e integração com Slack.',
    requirements: [
      'Colaboração em tempo real',
      'Sincronização offline',
      'Dashboard de métricas',
      'Integração com Slack',
      'Interface intuitiva'
    ]
  };
  const response = await client.analyze(projectData);
  console.log('Resposta da equipe CWB Hub:', response);

  // Iterar solução com feedback
  const sessionId = response.session_id;
  if (sessionId) {
    const feedback = 'O orçamento é limitado, priorize funcionalidades essenciais.';
    const refined = await client.iterate(sessionId, feedback);
    console.log('Solução refinada:', refined);
  }

  // Consultar status da sessão
  if (sessionId) {
    const status = await client.status(sessionId);
    console.log('Status da sessão:', status);
  }

  // Listar sessões recentes
  const sessions = await client.sessions();
  console.log('Sessões recentes:', sessions);
}

main().catch(console.error);
