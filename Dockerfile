# Dockerfile para CWB Hub Hybrid AI System (API + CLI)
FROM python:3.10-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# Copiar arquivos do projeto
COPY . /app

# Instalar dependências Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install fastapi uvicorn

# Expor porta padrão da API
EXPOSE 8000

# Comando padrão: iniciar API FastAPI
CMD ["uvicorn", "web_interface.main:app", "--host", "0.0.0.0", "--port", "8000"]
