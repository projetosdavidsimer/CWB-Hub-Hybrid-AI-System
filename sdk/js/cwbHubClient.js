// CWB Hub JavaScript SDK
// SDK oficial para integração com a API REST do CWB Hub Hybrid AI System
// Autor: David Simer

const axios = require('axios');

class CWBHubClient {
  /**
   * @param {string} apiUrl - URL base da API REST
   * @param {string} [apiKey] - Chave de autenticação opcional
   */
  constructor(apiUrl, apiKey = null) {
    this.apiUrl = apiUrl.replace(/\/$/, '');
    this.apiKey = apiKey;
    this.axios = axios.create({
      baseURL: this.apiUrl,
      headers: {
        'Content-Type': 'application/json',
        ...(apiKey ? { 'Authorization': `Bearer ${apiKey}` } : {})
      }
    });
  }

  setApiKey(apiKey) {
    this.apiKey = apiKey;
    this.axios.defaults.headers['Authorization'] = `Bearer ${apiKey}`;
  }

  async health() {
    const resp = await this.axios.get('/health');
    return resp.data;
  }

  async analyze(projectData) {
    const resp = await this.axios.post('/analyze', projectData);
    return resp.data;
  }

  async iterate(sessionId, feedback) {
    const resp = await this.axios.post(`/iterate/${sessionId}`, { feedback });
    return resp.data;
  }

  async status(sessionId) {
    const resp = await this.axios.get(`/status/${sessionId}`);
    return resp.data;
  }

  async sessions() {
    const resp = await this.axios.get('/sessions');
    return resp.data;
  }
}

module.exports = CWBHubClient;
