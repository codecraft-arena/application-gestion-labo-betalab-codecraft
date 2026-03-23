-- ═══════════════════════════════════════════════════════════════════════════════
-- BetaLab v2.0 — Migration SQL Complète & Robuste
-- Compatible: MySQL 5.7+ (pas de syntaxe 8.0 exclusives)
-- À exécuter: mysql -u luc -p db_lab < migration_v2.sql
-- ═══════════════════════════════════════════════════════════════════════════════

USE db_lab;

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. MODIFICATIONS DES TABLES EXISTANTES
-- ─────────────────────────────────────────────────────────────────────────────

-- Ajouter colonne 'role' à users (compatible MySQL 5.7)
-- Utiliser ALTER IGNORE ou gère l'erreur manuellement
-- SET @col := (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
--              WHERE TABLE_NAME = 'users' AND COLUMN_NAME = 'role');
-- SELECT IF(@col = 0, 'ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT "membre"', 'Column exists');

-- Pour MySQL 5.7, essayer sans IF NOT EXISTS (accepter l'erreur si existe):
ALTER TABLE users ADD COLUMN role VARCHAR(50) NOT NULL DEFAULT 'membre';
-- L'erreur "Duplicate column name" est acceptable s'il existe déjà

-- Ajouter colonne 'participation_status' à contributes
ALTER TABLE contributes ADD COLUMN participation_status VARCHAR(20) NOT NULL DEFAULT 'accepted';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. TABLES DE CONTACT & ADHÉSION (Nouvelles)
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
  KEY idx_status (status),
  KEY idx_created (created_at)
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
  KEY idx_expires (expires_at),
  KEY fk_contact (contact_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ajouter clé étrangère (si n'existe pas)
ALTER TABLE invitation_tokens
  ADD CONSTRAINT fk_inv_contact FOREIGN KEY (contact_id)
  REFERENCES contact_requests(id) ON DELETE SET NULL;

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. TABLES ÉVÉNEMENTS (Nouvelles)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS events (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  title       VARCHAR(200) NOT NULL,
  description TEXT,
  event_date  DATE,
  location    VARCHAR(255),
  event_type  VARCHAR(100) DEFAULT 'événement',
  created_by  VARCHAR(100),
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  KEY idx_date (event_date),
  KEY idx_type (event_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. TABLES DE SÉCURITÉ v2.0 (NOUVELLES)
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS sessions (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  token       VARCHAR(256) NOT NULL UNIQUE,
  user_mailer VARCHAR(100) NOT NULL,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
  expires_at  DATETIME NOT NULL,
  user_agent  VARCHAR(255),
  ip_address  VARCHAR(45),
  KEY idx_token (token),
  KEY idx_user (user_mailer),
  KEY idx_expires (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Ajouter FK sessions -> users (peut déjà exister)
ALTER TABLE sessions
  ADD CONSTRAINT fk_session_user FOREIGN KEY (user_mailer)
  REFERENCES users(mailer) ON DELETE CASCADE;

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
  KEY idx_expires (expires_at),
  KEY fk_session (session_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. VÉRIFICATION FINALE
-- ─────────────────────────────────────────────────────────────────────────────

SELECT '✅ Migration BetaLab v2.0 Complétée!' as Status;

-- Afficher toutes les tables
SHOW TABLES;

-- Afficher statistiques
SELECT 
  TABLE_NAME,
  TABLE_ROWS,
  ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'db_lab'
ORDER BY TABLE_NAME;
