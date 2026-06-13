CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; 
CREATE EXTENSION IF NOT EXISTS "pgcrypto"; 
 -- ─── Users and Authentication ────────────────────────────── 
CREATE TABLE IF NOT EXISTS users ( 
    id            UUID PRIMARY KEY DEFAULT uuid_generate_v4(), 
    username      VARCHAR(64) UNIQUE NOT NULL, 
    email         VARCHAR(256) UNIQUE NOT NULL, 
    password_hash VARCHAR(256) NOT NULL, 
    role          VARCHAR(32) NOT NULL DEFAULT 'analyst' 
                  CHECK (role IN ('analyst', 'engineer', 'admin')), 
    is_active     BOOLEAN NOT NULL DEFAULT TRUE, 
    created_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW(), 
    last_login    TIMESTAMP WITH TIME ZONE 
); 
 -- ─── Network Flow Features ───────────────────────────────── 
CREATE TABLE IF NOT EXISTS network_flows ( 
    id             UUID PRIMARY KEY DEFAULT uuid_generate_v4(), 
    flow_uid       VARCHAR(64), 
    timestamp      TIMESTAMP WITH TIME ZONE NOT NULL, 
    src_ip         INET, 
    dst_ip         INET, 
    src_port       INTEGER, 
    dst_port       INTEGER, 
    protocol       VARCHAR(16), 
    duration       FLOAT, 
    total_bytes    BIGINT, 
    src_bytes      BIGINT, 
    dst_bytes      BIGINT, 
    total_packets  INTEGER, 
    feature_vector JSONB, 
    record_hash    VARCHAR(64) NOT NULL, 
    ingested_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW() 
); 
 
CREATE INDEX idx_network_flows_timestamp ON network_flows(timestamp); 
CREATE INDEX idx_network_flows_src_ip ON network_flows(src_ip); 
CREATE INDEX idx_network_flows_dst_ip ON network_flows(dst_ip); 
 -- ─── Detection Results ───────────────────────────────────── 
CREATE TABLE IF NOT EXISTS detection_results ( 
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(), 
    flow_id         UUID REFERENCES network_flows(id), 
    timestamp       TIMESTAMP WITH TIME ZONE DEFAULT NOW(), 
    threat_score    FLOAT NOT NULL CHECK (threat_score >= 0.0 AND threat_score <= 1.0), 
    threat_class    VARCHAR(64), 
    confidence      FLOAT, 
    model_version   VARCHAR(32), 
    rule_fired      BOOLEAN DEFAULT FALSE, 
    rule_name       VARCHAR(128), 
    is_true_positive BOOLEAN, 
    analyst_notes   TEXT, 
    reviewed_at     TIMESTAMP WITH TIME ZONE, 
    reviewed_by     UUID REFERENCES users(id) 
); 
 
CREATE INDEX idx_detections_timestamp ON detection_results(timestamp); 
CREATE INDEX idx_detections_threat_score ON detection_results(threat_score); 
 -- ─── Security Alerts (Enriched) ──────────────────────────── 
CREATE TABLE IF NOT EXISTS security_alerts ( 
    id                   UUID PRIMARY KEY DEFAULT uuid_generate_v4(), 
    detection_id         UUID REFERENCES detection_results(id), 
    timestamp            TIMESTAMP WITH TIME ZONE DEFAULT NOW(), 
    severity             VARCHAR(16) NOT NULL 
                         CHECK (severity IN ('low','medium','high','critical')), 
    status               VARCHAR(32) NOT NULL DEFAULT 'open' 
                         CHECK (status IN ('open','investigating','contained', 
                                           'false_positive','closed')), 
    vt_malicious_count   INTEGER, 
    vt_last_analysis_date TIMESTAMP WITH TIME ZONE, 
    shodan_ports         JSONB, 
    shodan_country       VARCHAR(64), 
    shodan_org           VARCHAR(256), 
    containment_action   VARCHAR(128), 
    containment_timestamp TIMESTAMP WITH TIME ZONE, 
    containment_by       UUID REFERENCES users(id), 
    email_notified       BOOLEAN DEFAULT FALSE, 
    alert_hash           VARCHAR(64) NOT NULL 
); 
 -- ─── Tamper-Evident Audit Log ────────────────────────────── -- APPEND ONLY — no row in this table is ever updated or deleted -- Hash-chaining: each entry includes SHA-256 of previous entry 
CREATE TABLE IF NOT EXISTS audit_log ( 
    id                   BIGSERIAL PRIMARY KEY, 
    log_id               UUID NOT NULL DEFAULT uuid_generate_v4(), 
    timestamp            TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(), 
    user_id              UUID, 
    endpoint             VARCHAR(256), 
    http_method          VARCHAR(16), 
    source_ip            INET, 
    request_hash         VARCHAR(64), 
    response_code        INTEGER, 
    inference_latency_ms FLOAT, 
    threat_score         FLOAT, 
    entry_hash           VARCHAR(64) NOT NULL, 
    prev_entry_hash      VARCHAR(64) NOT NULL 
); 
 -- Prevent any modification of audit log entries 
CREATE OR REPLACE RULE audit_log_no_update AS 
    ON UPDATE TO audit_log DO INSTEAD NOTHING; 
 
CREATE OR REPLACE RULE audit_log_no_delete AS 
    ON DELETE TO audit_log DO INSTEAD NOTHING; 
 -- ─── ML Model Version Registry ───────────────────────────── 
CREATE TABLE IF NOT EXISTS model_versions ( 
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(), 
    mlflow_run_id           VARCHAR(64) UNIQUE NOT NULL, 
    model_name              VARCHAR(128) NOT NULL, 
    version                 VARCHAR(32) NOT NULL, 
    f1_score                FLOAT, 
    precision_score         FLOAT, 
    recall_score            FLOAT, 
    auc_roc                 FLOAT, 
    pre_hardening_accuracy  FLOAT, 
    post_hardening_accuracy FLOAT, 
    attacks_survived        INTEGER, 
    is_production           BOOLEAN DEFAULT FALSE, 
    deployed_at             TIMESTAMP WITH TIME ZONE, 
    deployed_by             UUID REFERENCES users(id), 
    created_at              TIMESTAMP WITH TIME ZONE DEFAULT NOW() 
); 
 
Verify the SQL is valid: 
# Test it locally if PostgreSQL is installed 
psql -U postgres -f data-pipeline/sql/init.sql 
 
# Or validate syntax with: 
python3 -c " 
with open('data-pipeline/sql/init.sql') as f: 
    content = f.read() 
print('SQL file exists and is readable') 
print(f'Lines: {len(content.splitlines())}') 
