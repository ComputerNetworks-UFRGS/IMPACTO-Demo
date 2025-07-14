-- Arquivo de exemplo para resetar o PostgreSQL
-- Copiar para reset_db.sql e rodar o script sudo -u postgres psql -f reset_db.sql
-- Troque os nomes e a senhas (mesmas do arquivo .env)

-- Limpa banco e usuário existentes
DROP DATABASE IF EXISTS impacto;
DROP USER IF EXISTS gt_impacto;

-- Recria banco e usuário
CREATE DATABASE impacto;
CREATE USER gt_impacto WITH PASSWORD 'your_secure_password';

-- Configura o usuário
ALTER ROLE gt_impacto SET client_encoding TO 'utf8';
ALTER ROLE gt_impacto SET default_transaction_isolation TO 'read committed';
ALTER ROLE gt_impacto SET timezone TO 'UTC';

-- Concede privilégios básicos
GRANT ALL PRIVILEGES ON DATABASE impacto TO gt_impacto;

-- Conecta ao banco
\c impacto

-- Concede privilégios de schema (necessário para Django)
GRANT ALL ON SCHEMA public TO gt_impacto;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO gt_impacto;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO gt_impacto;