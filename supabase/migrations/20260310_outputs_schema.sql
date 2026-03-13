-- =============================================================
-- OUTPUTS SCHEMA — Agencia Migracao Digital
-- Migra todos os outputs de arquivo local para Supabase.
-- Data: 2026-03-10
-- =============================================================

-- ============================================================
-- output_runs: uma linha por sessao/run de squad
-- ============================================================
CREATE TABLE IF NOT EXISTS output_runs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brand       TEXT NOT NULL,
    squad       TEXT NOT NULL CHECK (squad IN ('ugc', 'ci', 'cm', 'ecom', 'traf')),
    slug        TEXT,
    run_date    DATE NOT NULL DEFAULT CURRENT_DATE,
    status      TEXT NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft', 'approved', 'rejected', 'published')),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata    JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS output_runs_brand_idx    ON output_runs(brand);
CREATE INDEX IF NOT EXISTS output_runs_squad_idx    ON output_runs(squad);
CREATE INDEX IF NOT EXISTS output_runs_run_date_idx ON output_runs(run_date DESC);

-- Trigger para atualizar updated_at automaticamente
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$;

DROP TRIGGER IF EXISTS output_runs_updated_at ON output_runs;
CREATE TRIGGER output_runs_updated_at
    BEFORE UPDATE ON output_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ============================================================
-- output_artifacts: cada arquivo/artefato gerado por um agente
-- Suporta texto (markdown, JSON como texto) e binarios (URL no Storage)
-- ============================================================
CREATE TABLE IF NOT EXISTS output_artifacts (
    id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id         UUID NOT NULL REFERENCES output_runs(id) ON DELETE CASCADE,
    artifact_type  TEXT NOT NULL,
    -- tipos: hooks, script, direction, caption, ad_copy, carousel, stories,
    --        strategy, reference_report, veo3_payload, theme_change,
    --        import_report, sales_analysis, performance_report,
    --        recommendations, daily_report, weekly_report, publication_log,
    --        financial_report, product_data
    agent          TEXT NOT NULL,
    content        TEXT,           -- conteudo markdown/texto
    content_json   JSONB,          -- conteudo JSON estruturado
    storage_url    TEXT,           -- URL no Supabase Storage (imagens/videos)
    file_format    TEXT NOT NULL DEFAULT 'md'
                       CHECK (file_format IN ('md', 'json', 'png', 'jpg', 'mp4', 'txt')),
    scene_number   INTEGER,        -- cenas do UGC (1, 2, 3...)
    variant_number INTEGER,        -- variantes de copy (1, 2, 3)
    status         TEXT NOT NULL DEFAULT 'draft'
                       CHECK (status IN ('draft', 'approved', 'rejected', 'published')),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata       JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS output_artifacts_run_id_idx    ON output_artifacts(run_id);
CREATE INDEX IF NOT EXISTS output_artifacts_type_idx      ON output_artifacts(artifact_type);
CREATE INDEX IF NOT EXISTS output_artifacts_agent_idx     ON output_artifacts(agent);
CREATE INDEX IF NOT EXISTS output_artifacts_created_at_idx ON output_artifacts(created_at DESC);

-- ============================================================
-- cm_products: analise de produto do Squad Social Media CM
-- ============================================================
CREATE TABLE IF NOT EXISTS cm_products (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id               UUID REFERENCES output_runs(id) ON DELETE SET NULL,
    brand                TEXT NOT NULL DEFAULT 'confeccoes-mauricio',
    product_name         TEXT NOT NULL,
    product_url          TEXT,
    category             TEXT,
    product_type         TEXT,
    color_data           JSONB,          -- {primary, secondary, pattern}
    material_appearance  TEXT,
    texture              TEXT,
    fit                  TEXT,
    length               TEXT,
    neckline             TEXT,
    sleeves              TEXT,
    details              JSONB,          -- array de detalhes
    accessories_visible  JSONB,          -- array de acessorios
    confidence_notes     TEXT,
    nano_banana_prompts  JSONB,          -- array de 6 prompts em ingles
    instagram_caption    TEXT,
    image_urls           JSONB,          -- array de URLs no Storage
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS cm_products_run_id_idx ON cm_products(run_id);
CREATE INDEX IF NOT EXISTS cm_products_brand_idx  ON cm_products(brand);

-- ============================================================
-- traf_metrics: metricas Meta Ads por anuncio/dia
-- (substitui/complementa a tabela metrics_daily existente)
-- ============================================================
CREATE TABLE IF NOT EXISTS traf_metrics (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id              UUID REFERENCES output_runs(id) ON DELETE SET NULL,
    brand               TEXT NOT NULL,
    metric_date         DATE NOT NULL,
    account_id          TEXT,
    campaign_id         TEXT,
    campaign_name       TEXT,
    adset_id            TEXT,
    adset_name          TEXT,
    ad_id               TEXT,
    ad_name             TEXT,
    impressions         BIGINT DEFAULT 0,
    reach               BIGINT DEFAULT 0,
    frequency           NUMERIC(10, 4) DEFAULT 0,
    clicks              BIGINT DEFAULT 0,
    inline_link_clicks  BIGINT DEFAULT 0,
    outbound_clicks     BIGINT DEFAULT 0,
    link_clicks         BIGINT DEFAULT 0,
    landing_page_views  BIGINT DEFAULT 0,
    spend               NUMERIC(12, 2) DEFAULT 0,
    cpc                 NUMERIC(10, 4) DEFAULT 0,
    cpm                 NUMERIC(10, 4) DEFAULT 0,
    ctr                 NUMERIC(10, 6) DEFAULT 0,
    roas                NUMERIC(10, 4) DEFAULT 0,
    purchases           BIGINT DEFAULT 0,
    leads               BIGINT DEFAULT 0,
    add_to_cart         BIGINT DEFAULT 0,
    initiate_checkout   BIGINT DEFAULT 0,
    cost_per_purchase   NUMERIC(10, 4) DEFAULT 0,
    cost_per_lead       NUMERIC(10, 4) DEFAULT 0,
    whatsapp_clicks     BIGINT DEFAULT 0,
    video_views_3s      BIGINT DEFAULT 0,
    video_avg_watch_time BIGINT DEFAULT 0,
    post_engagements    BIGINT DEFAULT 0,
    post_reactions      BIGINT DEFAULT 0,
    comments            BIGINT DEFAULT 0,
    shares              BIGINT DEFAULT 0,
    raw_data            JSONB,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(brand, metric_date, ad_id)
);

CREATE INDEX IF NOT EXISTS traf_metrics_brand_date_idx ON traf_metrics(brand, metric_date DESC);
CREATE INDEX IF NOT EXISTS traf_metrics_ad_id_idx      ON traf_metrics(ad_id);
CREATE INDEX IF NOT EXISTS traf_metrics_run_id_idx     ON traf_metrics(run_id);

-- ============================================================
-- traf_publications: publicacoes de anuncios no Meta
-- ============================================================
CREATE TABLE IF NOT EXISTS traf_publications (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id              UUID REFERENCES output_runs(id) ON DELETE SET NULL,
    brand               TEXT NOT NULL,
    meta_ad_id          TEXT,           -- ID do anuncio criado no Meta
    account_id          TEXT,
    campaign_id         TEXT,
    adset_id            TEXT,
    creative_storage_url TEXT,          -- URL do criativo no Storage
    copy_headline       TEXT,
    copy_primary_text   TEXT,
    copy_description    TEXT,
    pub_status          TEXT NOT NULL DEFAULT 'draft'
                            CHECK (pub_status IN ('draft', 'submitted', 'active', 'rejected', 'paused')),
    published_at        TIMESTAMPTZ,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS traf_publications_brand_idx  ON traf_publications(brand);
CREATE INDEX IF NOT EXISTS traf_publications_run_id_idx ON traf_publications(run_id);

-- ============================================================
-- ecom_catalog_ops: operacoes de catalogo E-commerce
-- ============================================================
CREATE TABLE IF NOT EXISTS ecom_catalog_ops (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id          UUID REFERENCES output_runs(id) ON DELETE SET NULL,
    brand           TEXT NOT NULL,
    operation_type  TEXT NOT NULL CHECK (operation_type IN ('import', 'update', 'delete')),
    product_id      TEXT,
    product_name    TEXT,
    sku             TEXT,
    price           NUMERIC(10, 2),
    stock           INTEGER,
    categories      JSONB,
    data            JSONB,             -- dados completos do produto
    op_status       TEXT NOT NULL DEFAULT 'pending'
                        CHECK (op_status IN ('pending', 'completed', 'error')),
    error_message   TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ecom_catalog_ops_brand_idx  ON ecom_catalog_ops(brand);
CREATE INDEX IF NOT EXISTS ecom_catalog_ops_run_id_idx ON ecom_catalog_ops(run_id);

-- ============================================================
-- ci_references: anuncios coletados da Meta Ads Library
-- ============================================================
CREATE TABLE IF NOT EXISTS ci_references (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id               UUID REFERENCES output_runs(id) ON DELETE SET NULL,
    brand                TEXT NOT NULL,
    collected_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    search_terms         JSONB,          -- array de termos usados
    country              TEXT DEFAULT 'BR',
    ad_id                TEXT,
    page_name            TEXT,
    ad_status            TEXT,
    platforms            JSONB,
    start_date           TEXT,
    format               TEXT,          -- video, imagem, carrossel
    ad_url               TEXT,
    ad_text              TEXT,
    cta_type             TEXT,
    destination_url      TEXT,
    video_url            TEXT,
    video_transcription  TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ci_references_run_id_idx ON ci_references(run_id);
CREATE INDEX IF NOT EXISTS ci_references_brand_idx  ON ci_references(brand);

-- ============================================================
-- RLS: Row Level Security — desabilitado por padrao (uso interno)
-- Habilitar se/quando expor via API publica
-- ============================================================
ALTER TABLE output_runs        DISABLE ROW LEVEL SECURITY;
ALTER TABLE output_artifacts   DISABLE ROW LEVEL SECURITY;
ALTER TABLE cm_products        DISABLE ROW LEVEL SECURITY;
ALTER TABLE traf_metrics       DISABLE ROW LEVEL SECURITY;
ALTER TABLE traf_publications  DISABLE ROW LEVEL SECURITY;
ALTER TABLE ecom_catalog_ops   DISABLE ROW LEVEL SECURITY;
ALTER TABLE ci_references      DISABLE ROW LEVEL SECURITY;
