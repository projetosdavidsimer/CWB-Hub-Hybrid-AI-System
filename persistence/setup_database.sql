
-- CWB Hub Database Setup
-- Execute como superuser do PostgreSQL

-- Criar usuário
CREATE USER cwb_user WITH PASSWORD 'cwb_password_2025';

-- Criar banco de dados
CREATE DATABASE cwb_hub OWNER cwb_user;

-- Conceder privilégios
GRANT ALL PRIVILEGES ON DATABASE cwb_hub TO cwb_user;

-- Conectar ao banco cwb_hub e conceder privilégios no schema
\c cwb_hub
GRANT ALL ON SCHEMA public TO cwb_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cwb_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cwb_user;

-- Configurações de performance
ALTER DATABASE cwb_hub SET shared_preload_libraries = 'pg_stat_statements';
ALTER DATABASE cwb_hub SET log_statement = 'all';
ALTER DATABASE cwb_hub SET log_min_duration_statement = 1000;
    