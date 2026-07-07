-- SGCS — Script de inicialização da base de dados
-- Executado automaticamente na primeira criação do contentor PostgreSQL

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

SELECT 'Base de dados SGCS inicializada com sucesso.' AS mensagem;
