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
-- 1. CREATE NEW TABLE: profile_modification_request
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
    KEY idx_created_at (created_at),
    CONSTRAINT unique_pending_field UNIQUE KEY (user_email, field_name, created_at) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ============================================================================
-- 2. CREATE NEW TABLE: activity_modification_request
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
ALTER TABLE questions 
ADD COLUMN visibility VARCHAR(20) DEFAULT 'pending' COMMENT 'pending, approved, rejected',
ADD COLUMN reviewed_at TIMESTAMP NULL,
ADD COLUMN reviewed_by VARCHAR(30) NULL,
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE questions
ADD FOREIGN KEY IF NOT EXISTS fk_questions_reviewed_by (reviewed_by) REFERENCES users(email) ON DELETE SET NULL,
ADD KEY IF NOT EXISTS idx_visibility (visibility),
ADD KEY IF NOT EXISTS idx_created_at (created_at);

-- ============================================================================
-- 4. MODIFY TABLE: suggestions - Add approval/visibility columns
-- ============================================================================
ALTER TABLE suggestions 
ADD COLUMN visibility VARCHAR(20) DEFAULT 'pending' COMMENT 'pending, approved, rejected',
ADD COLUMN reviewed_at TIMESTAMP NULL,
ADD COLUMN reviewed_by VARCHAR(30) NULL,
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

ALTER TABLE suggestions
ADD FOREIGN KEY IF NOT EXISTS fk_suggestions_reviewed_by (reviewed_by) REFERENCES users(email) ON DELETE SET NULL,
ADD KEY IF NOT EXISTS idx_visibility (visibility),
ADD KEY IF NOT EXISTS idx_created_at (created_at);

-- ============================================================================
-- 5. MODIFY TABLE: activities - Add user creation tracking & approval status
-- ============================================================================
ALTER TABLE activities 
ADD COLUMN created_by VARCHAR(30) NULL COMMENT 'User email who created this activity',
ADD COLUMN user_approval_status VARCHAR(30) DEFAULT 'approved' COMMENT 'pending_submission, approved, rejected',
ADD COLUMN reviewed_at TIMESTAMP NULL,
ADD COLUMN reviewed_by VARCHAR(30) NULL;

ALTER TABLE activities
ADD FOREIGN KEY IF NOT EXISTS fk_activities_created_by (created_by) REFERENCES users(email) ON DELETE SET NULL,
ADD FOREIGN KEY IF NOT EXISTS fk_activities_reviewed_by (reviewed_by) REFERENCES users(email) ON DELETE SET NULL,
ADD KEY IF NOT EXISTS idx_user_approval_status (user_approval_status),
ADD KEY IF NOT EXISTS idx_created_by (created_by);

-- ============================================================================
-- 6. MODIFY TABLE: contributes - Add admin approval status
-- ============================================================================
-- This table tracks user participation in activities
ALTER TABLE contributes 
ADD COLUMN approval_status VARCHAR(30) DEFAULT 'auto_approved' COMMENT 'auto_approved, pending_admin_approval, approved, rejected';

-- ============================================================================
-- 7. UPDATE EXISTING: Initialize activity creation info for existing records
-- ============================================================================
-- Set created_by to first admin (for existing activities, assume admin created them)
-- Note: This is a best-guess; you may need to adjust based on your data
UPDATE activities 
SET user_approval_status = 'approved', created_by = NULL 
WHERE user_approval_status IS NULL OR user_approval_status = '';

-- ============================================================================
-- 8. CREATE INDEX for better query performance on new approval workflow
-- ============================================================================
CREATE INDEX IF NOT EXISTS idx_profile_mod_pending ON profile_modification_request(user_email, request_status);
CREATE INDEX IF NOT EXISTS idx_activity_mod_pending ON activity_modification_request(activity_id, request_status);
CREATE INDEX IF NOT EXISTS idx_questions_pending ON questions(visibility);
CREATE INDEX IF NOT EXISTS idx_suggestions_pending ON suggestions(visibility);
CREATE INDEX IF NOT EXISTS idx_activities_pending ON activities(user_approval_status, created_by);
CREATE INDEX IF NOT EXISTS idx_contributes_approval ON contributes(approval_status);

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- Tables created:
--   - profile_modification_request (NEW)
--   - activity_modification_request (NEW)
--
-- Tables modified:
--   - question (added visibility, reviewed_at, reviewed_by, created_at)
--   - sugestion (added visibility, reviewed_at, reviewed_by, created_at)
--   - activity (added created_by, user_approval_status, reviewed_at, reviewed_by)
--   - contribute (added approval_status)
--
-- Indices added for performance optimization
-- ============================================================================
