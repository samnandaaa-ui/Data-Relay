-- database/schema.sql
-- Skema database Setting Relay Proteksi GH United Power.

CREATE TABLE IF NOT EXISTS nodes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    node_key    TEXT NOT NULL,
    nama        TEXT NOT NULL,
    parent_id   INTEGER REFERENCES nodes(id) ON DELETE CASCADE,
    node_type   TEXT NOT NULL DEFAULT 'output',
    ct_ratio    TEXT,
    vt_ratio    TEXT,
    sumber_luar TEXT,
    sort_order  INTEGER NOT NULL DEFAULT 0,
    note        TEXT,
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (parent_id, node_key)
);

CREATE TABLE IF NOT EXISTS relay_settings (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    node_id            INTEGER NOT NULL REFERENCES nodes(id) ON DELETE CASCADE,
    relay_type         TEXT NOT NULL,
    enabled            INTEGER NOT NULL DEFAULT 0,
    pickup_xin         REAL,
    pickup_ampere      REAL,
    tms                REAL,
    curve              TEXT,
    delay              REAL,
    trip_time_minutes  REAL,
    alarm_percent      REAL,
    trip_percent       REAL,
    UNIQUE (node_id, relay_type)
);

CREATE TABLE IF NOT EXISTS relay_curve_types (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    curve_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS app_settings (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE INDEX IF NOT EXISTS idx_nodes_parent ON nodes(parent_id);
CREATE INDEX IF NOT EXISTS idx_relay_node ON relay_settings(node_id);
