// Testes automatizados para o SDK JavaScript do CWB Hub Hybrid AI System
const CWBHubClient = require('./cwbHubClient');
const axios = require('axios');
const MockAdapter = require('axios-mock-adapter');

describe('CWBHubClient', () => {
  let client, mock;
  const apiUrl = 'http://localhost:8000';
  const apiKey = 'test_key';

  beforeEach(() => {
    client = new CWBHubClient(apiUrl, apiKey);
    mock = new MockAdapter(client.axios);
  });

  afterEach(() => {
    mock.restore();
  });

  test('health()', async () => {
    mock.onGet('/health').reply(200, { status: 'ok' });
    const resp = await client.health();
    expect(resp).toEqual({ status: 'ok' });
  });

  test('analyze()', async () => {
    mock.onPost('/analyze').reply(200, { result: 'analyzed' });
    const resp = await client.analyze({ title: 'test' });
    expect(resp).toEqual({ result: 'analyzed' });
  });

  test('iterate()', async () => {
    mock.onPost('/iterate/abc123').reply(200, { result: 'iterated' });
    const resp = await client.iterate('abc123', 'feedback');
    expect(resp).toEqual({ result: 'iterated' });
  });

  test('status()', async () => {
    mock.onGet('/status/abc123').reply(200, { status: 'session_status' });
    const resp = await client.status('abc123');
    expect(resp).toEqual({ status: 'session_status' });
  });

  test('sessions()', async () => {
    mock.onGet('/sessions').reply(200, { sessions: [1, 2, 3] });
    const resp = await client.sessions();
    expect(resp).toEqual({ sessions: [1, 2, 3] });
  });
});
