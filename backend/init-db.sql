-- =============================================================================
-- AI Strategy Hub - Database Initialization
-- =============================================================================
-- Questo script viene eseguito automaticamente alla creazione del database

-- Abilita estensione pgvector per embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Verifica installazione
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';

-- Log
DO $$
BEGIN
    RAISE NOTICE 'pgvector extension installed successfully!';
END
$$;
