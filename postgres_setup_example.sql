-- Arquivo de exemplo pro setup do postgresSQL
-- Copiar para postgres_setup.sql e rodar o script sudo -u postgres psql -f postgres_setup.sql
-- Troque os nomes e a senhas (mesmas do arquivo .env) 

DROP DATABASE IF EXISTS impacto;
DROP USER IF EXISTS gt_impacto;

CREATE DATABASE impacto;
CREATE USER gt_impacto WITH PASSWORD 'your_secure_password';

ALTER ROLE gt_impacto SET client_encoding TO 'utf8';
ALTER ROLE gt_impacto SET default_transaction_isolation TO 'read committed';
ALTER ROLE gt_impacto SET timezone TO 'UTC';

GRANT ALL PRIVILEGES ON DATABASE impacto TO gt_impacto;