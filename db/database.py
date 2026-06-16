"""
database.py — TITAN Wave 1
SQLite connection manager.
WAL mode enabled. Thread-safe via asyncio lock.
Single source of truth for all database connections.
This module does NOT contain business logic.
"""

import aiosqlite
import asyncio
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DB_PATH", "./data/titan.db")
_lock = asyncio.Lock()

async def get_connection() -> aiosqlite.Connection:
    """Return a configured aiosqlite connection with WAL mode enabled."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA foreign_keys=ON")
    await conn.execute("PRAGMA busy_timeout=30000")
    return conn

async def execute_write(query: str, params: tuple = ()) -> None:
    """Thread-safe write operation. All writes MUST use this method."""
    async with _lock:
        async with await get_connection() as conn:
            try:
                await conn.execute(query, params)
                await conn.commit()
            except aiosqlite.OperationalError as e:
                logger.error(f"DB write failed: {e} | Query: {query[:80]}")
                raise

async def execute_read(query: str, params: tuple = ()) -> list:
    """Read operation. Returns list of Row objects."""
    async with await get_connection() as conn:
        try:
            cursor = await conn.execute(query, params)
            return await cursor.fetchall()
        except aiosqlite.OperationalError as e:
            logger.error(f"DB read failed: {e} | Query: {query[:80]}")
            raise

async def execute_read_one(query: str, params: tuple = ()):
    """Read single row. Returns Row or None."""
    async with await get_connection() as conn:
        try:
            cursor = await conn.execute(query, params)
            return await cursor.fetchone()
        except aiosqlite.OperationalError as e:
            logger.error(f"DB read_one failed: {e} | Query: {query[:80]}")
            raise
