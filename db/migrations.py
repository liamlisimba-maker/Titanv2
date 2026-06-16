"""
migrations.py — TITAN Wave 1
Database schema creation and versioning.
Run on every startup. Idempotent — safe to run multiple times.
Add new migrations at the bottom. Never modify existing ones.
"""

import logging
from db.database import execute_write, execute_read_one

logger = logging.getLogger(__name__)

SCHEMA_VERSION = 1

CREATE_USERS = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    full_name TEXT,
    state TEXT NOT NULL DEFAULT 'PENDING_APPROVAL',
    invited_by TEXT,
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP,
    approved_by INTEGER,
    suspended_at TIMESTAMP,
    suspended_reason TEXT,
    api_configured BOOLEAN DEFAULT FALSE
)
"""

CREATE_AUDIT_LOG = """
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    actor_telegram_id INTEGER NOT NULL,
    action TEXT NOT NULL,
    target_telegram_id INTEGER,
    details TEXT
)
"""

CREATE_CONFIG = """
CREATE TABLE IF NOT EXISTS config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER,
    is_hard_lock BOOLEAN DEFAULT FALSE
)
"""

CREATE_ADMIN_SESSIONS = """
CREATE TABLE IF NOT EXISTS admin_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    session_token TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE
)
"""

CREATE_ADMIN_PIN_ATTEMPTS = """
CREATE TABLE IF NOT EXISTS admin_pin_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL,
    attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL
)
"""

CREATE_INVITE_TOKENS = """
CREATE TABLE IF NOT EXISTS invite_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE NOT NULL,
    created_by INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_by INTEGER,
    used_at TIMESTAMP,
    is_used BOOLEAN DEFAULT FALSE
)
"""

CREATE_SCHEMA_VERSION = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

async def run_migrations():
    """Run all migrations. Called on startup. Safe to run multiple times."""
    logger.info("Running database migrations...")
    
    await execute_write(CREATE_SCHEMA_VERSION)
    await execute_write(CREATE_USERS)
    await execute_write(CREATE_AUDIT_LOG)
    await execute_write(CREATE_CONFIG)
    await execute_write(CREATE_ADMIN_SESSIONS)
    await execute_write(CREATE_ADMIN_PIN_ATTEMPTS)
    await execute_write(CREATE_INVITE_TOKENS)
    
    current = await execute_read_one(
        "SELECT version FROM schema_version ORDER BY version DESC LIMIT 1"
    )
    
    if not current or current["version"] < SCHEMA_VERSION:
        await execute_write(
            "INSERT OR REPLACE INTO schema_version (version) VALUES (?)",
            (SCHEMA_VERSION,)
        )
        logger.info(f"Schema updated to version {SCHEMA_VERSION}")
    else:
        logger.info(f"Schema already at version {SCHEMA_VERSION}")
