-- Warehouse schema for sports data platform.
-- This script defines two analytical tables requested in the project:
-- 1) articles_clean: cleaned/classified article-level data
-- 2) articles_stats: aggregate KPIs for dashboards

-- Create table for cleaned article records.
CREATE TABLE IF NOT EXISTS articles_clean (
    id BIGSERIAL PRIMARY KEY,
    source TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    published_at TIMESTAMP NOT NULL,
    scraped_at TIMESTAMP NOT NULL,
    language TEXT,
    category TEXT NOT NULL,
    inserted_at TIMESTAMP NOT NULL DEFAULT NOW(),

    -- Data governance constraints.
    CONSTRAINT uq_articles_clean_url UNIQUE (url),
    CONSTRAINT chk_articles_clean_category CHECK (category IN ('football', 'tennis', 'basketball', 'other')),
    CONSTRAINT chk_articles_clean_title_not_blank CHECK (length(trim(title)) > 0),
    CONSTRAINT chk_articles_clean_content_length CHECK (length(content) >= 100)
);

-- Create aggregate table used by BI dashboards.
CREATE TABLE IF NOT EXISTS articles_stats (
    id BIGSERIAL PRIMARY KEY,
    event_date DATE NOT NULL,
    source TEXT NOT NULL,
    category TEXT NOT NULL,
    article_count INTEGER NOT NULL,
    inserted_at TIMESTAMP NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_articles_stats_key UNIQUE (event_date, source, category),
    CONSTRAINT chk_articles_stats_count_non_negative CHECK (article_count >= 0),
    CONSTRAINT chk_articles_stats_category CHECK (category IN ('football', 'tennis', 'basketball', 'other'))
);

-- Indexes that improve dashboard filtering performance.
CREATE INDEX IF NOT EXISTS idx_articles_clean_published_at ON articles_clean (published_at);
CREATE INDEX IF NOT EXISTS idx_articles_clean_source ON articles_clean (source);
CREATE INDEX IF NOT EXISTS idx_articles_clean_category ON articles_clean (category);
CREATE INDEX IF NOT EXISTS idx_articles_stats_event_date ON articles_stats (event_date);
