-- ============================================================================
-- MIGRATION: Admin Approval Workflow System - Simplified
-- ============================================================================
-- This migration implements approval system tables and columns
-- Tables already created:
-- - profile_modification_request ✓
-- - activity_modification_request ✓

-- ============================================================================
-- 3. MODIFY TABLE: questions
-- ============================================================================
ALTER TABLE questions 
ADD COLUMN visibility VARCHAR(20) DEFAULT 'pending',
ADD COLUMN reviewed_at TIMESTAMP NULL,
ADD COLUMN reviewed_by VARCHAR(30) NULL,
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- ============================================================================
-- 4. MODIFY TABLE: suggestions
-- ============================================================================
ALTER TABLE suggestions 
ADD COLUMN visibility VARCHAR(20) DEFAULT 'pending',
ADD COLUMN reviewed_at TIMESTAMP NULL,
ADD COLUMN reviewed_by VARCHAR(30) NULL,
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- ============================================================================
-- 5. MODIFY TABLE: activities
-- ============================================================================
ALTER TABLE activities 
ADD COLUMN created_by VARCHAR(30) NULL,
ADD COLUMN user_approval_status VARCHAR(30) DEFAULT 'approved',
ADD COLUMN reviewed_at TIMESTAMP NULL,
ADD COLUMN reviewed_by VARCHAR(30) NULL;

-- ============================================================================
-- 6. MODIFY TABLE: contributes
-- ============================================================================
ALTER TABLE contributes 
ADD COLUMN approval_status VARCHAR(30) DEFAULT 'auto_approved';

-- ============================================================================
-- 7. CREATE INDICES
-- ============================================================================
CREATE INDEX idx_questions_visibility ON questions(visibility);
CREATE INDEX idx_suggestions_visibility ON suggestions(visibility);
CREATE INDEX idx_activities_pending ON activities(user_approval_status);
CREATE INDEX idx_activities_created_by ON activities(created_by);
CREATE INDEX idx_contributes_approval ON contributes(approval_status);

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
SELECT 'Migration completed successfully!' as status;
