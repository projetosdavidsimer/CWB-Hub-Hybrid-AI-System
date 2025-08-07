# SDKs Oficiais - CWB Hub Hybrid AI System

## Python SDK

- **Arquivo:** `python/cwb_hub_sdk.py`
- **Exemplo de uso:** `python/example_usage.py`

### Instalação
```bash
pip install requests
```

### Uso Básico
```python
from cwb_hub_sdk import CWBHubClient
client = CWBHubClient(api_url="http://localhost:8000", api_key="SUA_API_KEY")
print(client.health())
```

Veja o exemplo completo em `python/example_usage.py`.

---

## JavaScript/Node.js SDK

- **Arquivo:** `js/cwbHubClient.js`
- **Exemplo de uso:** `js/exampleUsage.js`

### Instalação
```bash
npm install axios
```

### Uso Básico
```js
const CWBHubClient = require('./cwbHubClient');
const client = new CWBHubClient('http://localhost:8000', 'SUA_API_KEY');
client.health().then(console.log);
```

Veja o exemplo completo em `js/exampleUsage.js`.

---

## Funcionalidades dos SDKs
- Verificar status da API
- Enviar projetos para análise
- Iterar soluções com feedback
- Consultar status de sessões
- Listar sessões recentes

---

## Documentação Completa
- [CLI_GUIDE.md](../CLI_GUIDE.md)
- [QUICK_REFERENCE.md](../QUICK_REFERENCE.md)
- [README.md](../README.md)

---

**Dúvidas?** Consulte os exemplos, documentação ou abra uma issue no repositório.
