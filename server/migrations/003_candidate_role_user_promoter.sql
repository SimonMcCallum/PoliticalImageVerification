-- Migration 003: Add CANDIDATE role, per-user promoter statements, and Independent Candidates party
-- Run against the pivs-db PostgreSQL database

-- 1. Add 'candidate' value to the userrole enum
ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'candidate';

-- 2. Add per-user promoter statement columns to party_users
ALTER TABLE party_users ADD COLUMN IF NOT EXISTS promoter_statement TEXT;
ALTER TABLE party_users ADD COLUMN IF NOT EXISTS promoter_statement_updated_at TIMESTAMPTZ;

-- 3. Create the Independent Candidates party (if not already present)
INSERT INTO parties (id, name, short_name, status, created_at, updated_at)
SELECT gen_random_uuid(), 'Independent Candidates', 'Independent', 'ACTIVE', NOW(), NOW()
WHERE NOT EXISTS (
    SELECT 1 FROM parties WHERE short_name = 'Independent'
);
