-- ═══════════════════════════════════════════════════════════════════════════════
-- BetaLab v2.0 — Migration SQL FINALE (100% Compatible MySQL 5.7+)
-- IDEMPOTENT: Safe pour multiple exécutions
-- ═══════════════════════════════════════════════════════════════════════════════

USE db_lab;

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. TABLES NO-CONFLICT (Créer seulement si n'existe pas)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS contact_requests (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  name            VARCHAR(255) NOT NULL,
  email           VARCHAR(120) NOT NULL,
  subject         VARCHAR(255),
  message         TEXT,
  is_join_request BOOLEAN DEFAULT FALSE,
  status          VARCHAR(50) DEFAULT 'nouveau',
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_email (email),
  KEY idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS invitation_tokens (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  token       VARCHAR(150) NOT NULL UNIQUE,
  email       VARCHAR(120) NOT NULL,
  name        VARCHAR(100) NOT NULL,
  used        BOOLEAN DEFAULT FALSE,
  expires_at  DATETIME NOT NULL,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  contact_id  INT,
  KEY idx_token (token),
  KEY idx_email (email),
  KEY idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS events (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  title       VARCHAR(200) NOT NULL,
  description TEXT,
  event_date  DATE,
  location    VARCHAR(255),
  event_type  VARCHAR(100) DEFAULT 'événement',
  created_by  VARCHAR(100),
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_date (event_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS sessions (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  token       VARCHAR(256) NOT NULL UNIQUE,
  user_email  VARCHAR(100) NOT NULL,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  expires_at  DATETIME NOT NULL,
  user_agent  VARCHAR(255),
  ip_address  VARCHAR(45),
  KEY idx_token (token),
  KEY idx_user (user_email),
  KEY idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS admin_users (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  username    VARCHAR(100) NOT NULL UNIQUE,
  password    VARCHAR(255) NOT NULL,
  email       VARCHAR(100) NOT NULL UNIQUE,
  role        VARCHAR(50) DEFAULT 'admin',
  is_active   BOOLEAN DEFAULT TRUE,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  last_login  DATETIME,
  KEY idx_username (username),
  KEY idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS csrf_tokens (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  token       VARCHAR(256) NOT NULL UNIQUE,
  session_id  INT,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  expires_at  DATETIME NOT NULL,
  KEY idx_token (token),
  KEY idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. MODIFICATIONS COLONNES EXISTANTES
-- ─────────────────────────────────────────────────────────────────────────────

-- Note: MySQL 5.7 ne supporte pas IF NOT EXISTS pour ALTER TABLE
-- Les ALTER ci-dessous peuvent lever une erreur si la colonne existe
-- C'est NORMAL et attendu pour idempotence

-- Essayer d'ajouter 'role' à users (ignorera si existe)
-- ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'membre' AFTER suspended;

-- Essayer d'ajouter 'participation_status' à contributes (ignorera si existe)
-- ALTER TABLE contributes ADD COLUMN participation_status VARCHAR(20) NOT NULL DEFAULT 'accepted';

-- ─────────────────────────────────────────────────────────────────────────────
-- ALTERNATIVE PYTHON POUR LES ALTER TABLE
-- ─────────────────────────────────────────────────────────────────────────────
-- Les migrations ALTERs sont gérées par migrate_db.py qui gère mieux les erreurs
-- Voir: python migrate_db.py

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. RAPPORT FINAL
-- ─────────────────────────────────────────────────────────────────────────────

SELECT '✅ Migration BetaLab v2.0 SQL Complétée!' as Status;
SELECT 'Tables créées:' as Info;

SHOW TABLES;

SELECT '' as Separator;
SELECT 'Statistiques:' as Info;
SELECT 
  TABLE_NAME,
  TABLE_ROWS as Rows,
  ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size(MB)'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE()
ORDER BY TABLE_NAME;
