# Instruções para Testes Automatizados CWB Hub

## Dependências do Sistema

- Para rodar todos os testes (unitários, integração, performance, carga) é necessário ter o PostgreSQL client (libpq) instalado no sistema.

### Windows
- Instale o PostgreSQL: https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
- Ou apenas o client: https://www.postgresql.org/ftp/pgadmin/pgadmin4/v6.20/windows/
- Adicione o diretório bin do PostgreSQL ao PATH do sistema.

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install -y libpq-dev
```

### macOS
```bash
brew install postgresql
```

## Rodando os Testes

1. Instale as dependências Python:
```bash
pip install -r requirements.txt
```

2. Execute os testes com cobertura:
```bash
pytest --cov=src --cov-report=term-missing
```

## CI/CD Pipeline
- Certifique-se de que o ambiente de CI tenha o PostgreSQL client instalado.
- Configure variáveis de ambiente para banco de testes, se necessário.

## Observação
- Testes de integração e performance dependem do banco de dados estar acessível.
- Para cobertura > 90%, garanta que todos os módulos e endpoints estejam cobertos por testes.
