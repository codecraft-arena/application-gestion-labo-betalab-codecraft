-- ═══════════════════════════════════════════════════════════════════════════
-- BetaLab — Migrations pour le flux d'adhésion
-- À exécuter sur la base db_lab
-- ═══════════════════════════════════════════════════════════════════════════

USE db_lab;

-- 1. Colonne role sur users (si pas encore faite)
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS role VARCHAR(50) NOT NULL DEFAULT 'membre';

-- 2. Colonne participation_status sur contributes (si pas encore faite)
ALTER TABLE contributes
  ADD COLUMN IF NOT EXISTS participation_status VARCHAR(20) NOT NULL DEFAULT 'accepted';

-- 3. Table events
CREATE TABLE IF NOT EXISTS events (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  title       VARCHAR(200) NOT NULL,
  description TEXT,
  event_date  DATE,
  location    VARCHAR(255),
  event_type  VARCHAR(100) DEFAULT 'événement',
  created_by  VARCHAR(100)
);

-- 4. Table des demandes de contact
CREATE TABLE IF NOT EXISTS contact_requests (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  name            VARCHAR(255) NOT NULL,
  email           VARCHAR(120) NOT NULL,
  subject         VARCHAR(255),
  message         TEXT,
  is_join_request BOOLEAN DEFAULT FALSE,
  status          VARCHAR(50)  DEFAULT 'nouveau',
  created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP
);

-- 5. Table des tokens d'invitation
CREATE TABLE IF NOT EXISTS invitation_tokens (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  token       VARCHAR(150) NOT NULL UNIQUE,
  email       VARCHAR(120) NOT NULL,
  name        VARCHAR(100) NOT NULL,
  used        BOOLEAN      DEFAULT FALSE,
  expires_at  DATETIME     NOT NULL,
  created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
  contact_id  INT,
  CONSTRAINT fk_inv_contact FOREIGN KEY (contact_id)
    REFERENCES contact_requests(id) ON DELETE SET NULL
);

-- Vérification
SHOW TABLES;
