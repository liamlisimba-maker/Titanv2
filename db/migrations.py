"""
migrations.py - TITAN Wave 1
Schema creation. Idempotent - safe to run on every startup.
"""
import logging
from db.database import execute_write, execute_read_one

logger = logging.getLogger(__name__)

async def run_migrations():
    logger.info("Running database migrations...")

    await execute_write("""
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
    """)

    await execute_write("""
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
            actor_telegram_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            target_telegram_id INTEGER,
            details TEXT
        )
    """)

    await execute_write("""
        CREATE TABLE IF NOT EXISTS config (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_by INTEGER,
            is_hard_lock BOOLEAN DEFAULT FALSE
        )
    """)

    await execute_write("""
        CREATE TABLE IF NOT EXISTS admin_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            session_token TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            is_active BOOLEAN DEFAULT TRUE
        )
    """)

    await execute_write("""
        CREATE TABLE IF NOT EXISTS admin_pin_attempts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER NOT NULL,
            attempted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            success BOOLEAN NOT NULL
        )
    """)

    await execute_write("""
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
    """)

    logger.info("Migrations complete")