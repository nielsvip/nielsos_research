CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TYPE job_status AS ENUM ('queued','leased','running','completed','failed','blocked','cancelled');
CREATE TYPE intervention_status AS ENUM ('open','answered','resolved','ignored');

CREATE TABLE IF NOT EXISTS features (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    asset_scope TEXT NOT NULL DEFAULT 'both',
    long_applicability SMALLINT,
    short_applicability SMALLINT,
    lifecycle TEXT NOT NULL DEFAULT 'idea',
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS universes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    asset_class TEXT NOT NULL,
    source TEXT NOT NULL,
    symbols JSONB NOT NULL DEFAULT '[]'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS experiments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_key TEXT NOT NULL UNIQUE,
    feature_id UUID REFERENCES features(id),
    hypothesis TEXT NOT NULL,
    manifest JSONB NOT NULL,
    pine_version TEXT,
    code_version TEXT,
    priority INTEGER NOT NULL DEFAULT 100,
    enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    experiment_id UUID NOT NULL REFERENCES experiments(id) ON DELETE CASCADE,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    status job_status NOT NULL DEFAULT 'queued',
    priority INTEGER NOT NULL DEFAULT 100,
    attempts INTEGER NOT NULL DEFAULT 0,
    max_attempts INTEGER NOT NULL DEFAULT 3,
    lease_owner TEXT,
    lease_expires_at TIMESTAMPTZ,
    checkpoint JSONB NOT NULL DEFAULT '{}'::jsonb,
    last_error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    UNIQUE (experiment_id, symbol, timeframe, parameters)
);
CREATE INDEX IF NOT EXISTS jobs_claim_idx ON jobs(status, priority DESC, created_at);
CREATE INDEX IF NOT EXISTS jobs_lease_idx ON jobs(lease_expires_at) WHERE status IN ('leased','running');

CREATE TABLE IF NOT EXISTS workers (
    worker_id TEXT PRIMARY KEY,
    hostname TEXT NOT NULL,
    browser_profile TEXT,
    status TEXT NOT NULL DEFAULT 'starting',
    current_job_id UUID REFERENCES jobs(id),
    heartbeat_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    result_version INTEGER NOT NULL DEFAULT 1,
    metrics JSONB NOT NULL,
    raw_payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    screenshot_path TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(job_id, result_version)
);

CREATE TABLE IF NOT EXISTS interventions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    worker_id TEXT REFERENCES workers(worker_id),
    kind TEXT NOT NULL,
    question TEXT NOT NULL,
    context JSONB NOT NULL DEFAULT '{}'::jsonb,
    screenshot_path TEXT,
    status intervention_status NOT NULL DEFAULT 'open',
    answer TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    answered_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS credibility (
    feature_id UUID NOT NULL REFERENCES features(id),
    asset_class TEXT NOT NULL,
    timeframe TEXT NOT NULL,
    direction TEXT NOT NULL,
    regime TEXT NOT NULL DEFAULT 'all',
    score NUMERIC(6,3),
    confidence NUMERIC(6,3),
    sample_size BIGINT NOT NULL DEFAULT 0,
    details JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY(feature_id, asset_class, timeframe, direction, regime)
);

CREATE TABLE IF NOT EXISTS research_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feature_id UUID REFERENCES features(id),
    note TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'human',
    tags JSONB NOT NULL DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO features(name, category, asset_scope, long_applicability, short_applicability, lifecycle, description)
VALUES
 ('wt_velocity','WaveTrend','both',5,5,'implemented','WaveTrend first derivative / momentum speed'),
 ('donchian_position','Donchian','both',5,5,'implemented','Position within the Donchian channel'),
 ('relative_volume','Volume','both',4,5,'implemented','Participation and conviction confirmation'),
 ('rsi','Momentum','both',3,5,'implemented','Preferred short-side momentum sensor when paired with volume'),
 ('mfi','Momentum','both',5,2,'implemented','Preferred long-side money-flow sensor; not symmetric for shorts')
ON CONFLICT (name) DO NOTHING;
