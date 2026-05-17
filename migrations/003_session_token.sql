-- Migración 003: session_token para invalidar sesiones concurrentes
-- Aplicar con: mysql -u user -p freshsteps < migrations/003_session_token.sql

ALTER TABLE usuario
    ADD COLUMN IF NOT EXISTS session_token VARCHAR(64) NULL DEFAULT NULL;
