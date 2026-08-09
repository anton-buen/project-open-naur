-- Migration: Add session_id to allow multi-tenant public access

-- Master table to track isolated user workspaces
CREATE TABLE IF NOT EXISTS active_sessions (
    session_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- The chat history, strictly isolated by session
CREATE TABLE IF NOT EXISTS chat_ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES active_sessions(session_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS domain_constraints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    domain TEXT NOT NULL,
    business_impact TEXT NOT NULL,
    deep_dive TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(session_id) REFERENCES active_sessions(session_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS project_dictionary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    term TEXT NOT NULL,
    FOREIGN KEY(session_id) REFERENCES active_sessions(session_id) ON DELETE CASCADE
);