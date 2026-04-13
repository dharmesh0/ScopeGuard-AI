CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role VARCHAR(16) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS engagements (
  id UUID PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  description TEXT NOT NULL DEFAULT '',
  scope JSONB NOT NULL DEFAULT '[]'::jsonb,
  approval_mode BOOLEAN NOT NULL DEFAULT TRUE,
  created_by UUID NOT NULL REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS approvals (
  id UUID PRIMARY KEY,
  engagement_id UUID NOT NULL REFERENCES engagements(id),
  target VARCHAR(512) NOT NULL,
  attestation TEXT NOT NULL,
  status VARCHAR(16) NOT NULL DEFAULT 'pending',
  reviewed_by UUID NULL REFERENCES users(id),
  reviewed_at TIMESTAMPTZ NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS scans (
  id UUID PRIMARY KEY,
  engagement_id UUID NOT NULL REFERENCES engagements(id),
  requested_by UUID NOT NULL REFERENCES users(id),
  target VARCHAR(512) NOT NULL,
  human_in_the_loop BOOLEAN NOT NULL DEFAULT TRUE,
  approval_status VARCHAR(16) NOT NULL DEFAULT 'pending',
  status VARCHAR(32) NOT NULL DEFAULT 'queued',
  policy_snapshot JSONB NOT NULL DEFAULT '{}'::jsonb,
  summary TEXT NOT NULL DEFAULT '',
  severity_counts JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  started_at TIMESTAMPTZ NULL,
  completed_at TIMESTAMPTZ NULL
);

CREATE TABLE IF NOT EXISTS scan_logs (
  id BIGSERIAL PRIMARY KEY,
  scan_id UUID NOT NULL REFERENCES scans(id),
  level VARCHAR(20) NOT NULL DEFAULT 'INFO',
  message TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS findings (
  id UUID PRIMARY KEY,
  scan_id UUID NOT NULL REFERENCES scans(id),
  plugin VARCHAR(128) NOT NULL,
  title VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  severity VARCHAR(16) NOT NULL DEFAULT 'info',
  evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
  remediation TEXT NOT NULL DEFAULT '',
  references JSONB NOT NULL DEFAULT '[]'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS memory_entries (
  id UUID PRIMARY KEY,
  scan_id UUID NOT NULL REFERENCES scans(id),
  target VARCHAR(512) NOT NULL,
  content TEXT NOT NULL,
  embedding vector(64),
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reports (
  id UUID PRIMARY KEY,
  scan_id UUID NOT NULL UNIQUE REFERENCES scans(id),
  markdown_path VARCHAR(1024) NOT NULL,
  pdf_path VARCHAR(1024) NOT NULL,
  checksum VARCHAR(128) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

