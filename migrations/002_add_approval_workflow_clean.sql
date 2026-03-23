-- ============================================================================
-- MIGRATION: Admin Approval Workflow System
-- ============================================================================
-- This migration implements the complete admin approval system where:
-- 1. Profile modifications require admin approval
-- 2. Questions/Suggestions require admin approval  
-- 3. Activity modifications require admin approval
-- 4. User participation auto-approved when user accepts admin invitation
-- 5. Admin responses auto-approve questions

-- ============================================================================
-- 1. CREATE NEW TABLE: profile_modification_request (if not exists)
-- ============================================================================
CREATE TABLE IF NOT EXISTS profile_modification_request (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_email VARCHAR(30) NOT NULL,
    field_name VARCHAR(50) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    request_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP NULL,
    reviewed_by VARCHAR(30) NULL,
    admin_notes TEXT NULL,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(email) ON DELETE SET NULL,
    KEY idx_request_status (request_status),
    KEY idx_user_email (user_email),
    KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================================================
-- 2. CREATE NEW TABLE: activity_modification_request (if not exists)
-- ============================================================================
CREATE TABLE IF NOT EXISTS activity_modification_request (
    id INT PRIMARY KEY AUTO_INCREMENT,
    activity_id VARCHAR(255) NOT NULL,
    user_email VARCHAR(30) NOT NULL,
    field_name VARCHAR(50) NOT NULL,
    old_value TEXT,
    new_value TEXT,
    request_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP NULL,
    reviewed_by VARCHAR(30) NULL,
    admin_notes TEXT NULL,
    FOREIGN KEY (activity_id) REFERENCES activities(id_activity) ON DELETE CASCADE,
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,
    FOREIGN KEY (reviewed_by) REFERENCES users(email) ON DELETE SET NULL,
    KEY idx_request_status (request_status),
    KEY idx_activity_id (activity_id),
    KEY idx_user_email (user_email),
    KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================================================
-- 3. MODIFY TABLE: questions - Add approval/visibility columns
-- ============================================================================
@table_questions_visibility = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME='questions' AND COLUMN_NAME='visibility' AND TABLE_SCHEMA=DATABASE());

SET @alter_questions = IF(
    @table_questions_visibility = 0,
    "ALTER TABLE questions ADD COLUMN visibility VARCHAR(20) DEFAULT 'pending'",
    "SELECT 'Column visibility already exists'");

PREPARE stmt FROM @alter_questions;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

@table_questions_reviewed_at = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME='questions' AND COLUMN_NAME='reviewed_at' AND TABLE_SCHEMA=DATABASE());

SET @alter_questions2 = IF(
    @table_questions_reviewed_at = 0,
    "ALTER TABLE questions ADD COLUMN reviewed_at TIMESTAMP NULL, ADD COLUMN reviewed_by VARCHAR(30) NULL, ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    "SELECT 'Columns already exist'");

PREPARE stmt FROM @alter_questions2;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================================
-- 4. MODIFY TABLE: suggestions - Add approval/visibility columns
-- ============================================================================
@table_suggestions_visibility = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME='suggestions' AND COLUMN_NAME='visibility' AND TABLE_SCHEMA=DATABASE());

SET @alter_suggestions = IF(
    @table_suggestions_visibility = 0,
    "ALTER TABLE suggestions ADD COLUMN visibility VARCHAR(20) DEFAULT 'pending', ADD COLUMN reviewed_at TIMESTAMP NULL, ADD COLUMN reviewed_by VARCHAR(30) NULL, ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    "SELECT 'Columns already exist'");

PREPARE stmt FROM @alter_suggestions;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================================
-- 5. MODIFY TABLE: activities - Add user creation tracking & approval status
-- ============================================================================
@table_activities_created_by = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME='activities' AND COLUMN_NAME='created_by' AND TABLE_SCHEMA=DATABASE());

SET @alter_activities = IF(
    @table_activities_created_by = 0,
    "ALTER TABLE activities ADD COLUMN created_by VARCHAR(30) NULL, ADD COLUMN user_approval_status VARCHAR(30) DEFAULT 'approved', ADD COLUMN reviewed_at TIMESTAMP NULL, ADD COLUMN reviewed_by VARCHAR(30) NULL",
    "SELECT 'Columns already exist'");

PREPARE stmt FROM @alter_activities;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================================
-- 6. MODIFY TABLE: contributes - Add admin approval status
-- ============================================================================
@table_contributes_approval = (SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS 
    WHERE TABLE_NAME='contributes' AND COLUMN_NAME='approval_status' AND TABLE_SCHEMA=DATABASE());

SET @alter_contributes = IF(
    @table_contributes_approval = 0,
    "ALTER TABLE contributes ADD COLUMN approval_status VARCHAR(30) DEFAULT 'auto_approved'",
    "SELECT 'Column already exists'");

PREPARE stmt FROM @alter_contributes;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================================
-- 7. CREATE INDICES for performance
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_profile_mod_pending ON profile_modification_request(user_email, request_status);
CREATE INDEX IF NOT EXISTS idx_activity_mod_pending ON activity_modification_request(activity_id, request_status);
CREATE INDEX IF NOT EXISTS idx_questions_visibility ON questions(visibility);
CREATE INDEX IF NOT EXISTS idx_suggestions_visibility ON suggestions(visibility);
CREATE INDEX IF NOT EXISTS idx_activities_pending ON activities(user_approval_status, created_by);
CREATE INDEX IF NOT EXISTS idx_contributes_approval ON contributes(approval_status);

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
