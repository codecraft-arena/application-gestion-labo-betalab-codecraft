-- ============================================================================
-- MIGRATION: Add remaining approval workflow columns
-- ============================================================================
-- Questions table: already has visibility, reviewed_at, reviewed_by, created_at ✓
-- Suggestions table: needs to add approval columns
-- Activities table: needs to add approval columns
-- Contributes table: needs to add approval_status

-- ============================================================================
-- Add columns to suggestions table
-- ============================================================================
ALTER TABLE suggestions 
ADD COLUMN visibility VARCHAR(20) DEFAULT 'pending',
ADD COLUMN reviewed_at TIMESTAMP NULL,
ADD COLUMN reviewed_by VARCHAR(30) NULL,
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- ============================================================================
-- Add columns to activities table
-- ============================================================================
ALTER TABLE activities 
ADD COLUMN created_by VARCHAR(30) NULL,
ADD COLUMN user_approval_status VARCHAR(30) DEFAULT 'approved',
ADD COLUMN reviewed_at TIMESTAMP NULL,
ADD COLUMN reviewed_by VARCHAR(30) NULL;

-- ============================================================================
-- Add column to contributes table
-- ============================================================================
ALTER TABLE contributes 
ADD COLUMN approval_status VARCHAR(30) DEFAULT 'auto_approved';

-- ============================================================================
-- Create indices for performance
-- ============================================================================
CREATE INDEX idx_suggestions_visibility ON suggestions(visibility);
CREATE INDEX idx_activities_pending ON activities(user_approval_status);
CREATE INDEX idx_activities_created_by ON activities(created_by);
CREATE INDEX idx_contributes_approval ON contributes(approval_status);

-- ============================================================================
-- Migration complete
-- ============================================================================
SELECT 'All approval workflow columns added successfully!' as status;
