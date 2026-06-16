"""
database.py - TITAN Wave 1
SQLite connection manager. WAL mode. Thread-safe async writes.
"""
import aiosqlite
import asyncio
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)
_lock = asyncio.Lock()
DB_PATH = os.getenv("DB_PATH", "./data/titan.db")

async def get_connection():
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    await conn.execute("PRAGMA journal_mode=WAL")
    await conn.execute("PRAGMA foreign_keys=ON")
    await conn.execute("PRAGMA busy_timeout=30000")
    return conn

async def execute_write(query: str, params: tuple = ()):
    async with _lock:
        async with await get_connection() as conn:
            try:
                await conn.execute(query, params)
                await conn.commit()
            except aiosqlite.OperationalError as e:
                logger.error(f"DB write failed: {e}")
                raise

async def execute_read(query: str, params: tuple = ()):
    async with await get_connection() as conn:
        try:
            cursor = await conn.execute(query, params)
            return await cursor.fetchall()
        except aiosqlite.OperationalError as e:
            logger.error(f"DB read failed: {e}")
            raise

async def execute_read_one(query: str, params: tuple = ()):
    async with await get_connection() as conn:
        try:
            cursor = await conn.execute(query, params)
            return await cursor.fetchone()
        except aiosqlite.OperationalError as e:
            logger.error(f"DB read_one failed: {e}")
            raise