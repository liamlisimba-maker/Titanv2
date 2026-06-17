"""
database.py - TITAN Wave 1
SQLite connection manager. WAL mode. Thread-safe async writes via run_in_executor.
All reads return dicts not Row objects.
"""
import sqlite3
import asyncio
import logging
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)
_lock = asyncio.Lock()
_executor = ThreadPoolExecutor(max_workers=1)
DB_PATH = os.getenv("DB_PATH", "./data/titan.db")

def _get_connection():
    """Synchronous connection factory with WAL mode."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.row_factory = sqlite3.Row
    return conn

async def execute_write(query: str, params: tuple = ()):
    """Execute write operation asynchronously."""
    async with _lock:
        loop = asyncio.get_event_loop()
        try:
            def _write():
                conn = _get_connection()
                try:
                    conn.execute(query, params)
                    conn.commit()
                finally:
                    conn.close()
            await loop.run_in_executor(_executor, _write)
        except sqlite3.OperationalError as e:
            logger.error(f"DB write failed: {e}")
            raise

async def execute_read(query: str, params: tuple = ()):
    """Execute read query and return list of dicts."""
    loop = asyncio.get_event_loop()
    try:
        def _read():
            conn = _get_connection()
            try:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
            finally:
                conn.close()
        return await loop.run_in_executor(_executor, _read)
    except sqlite3.OperationalError as e:
        logger.error(f"DB read failed: {e}")
        raise

async def execute_read_one(query: str, params: tuple = ()):
    """Execute read query and return single dict or None."""
    loop = asyncio.get_event_loop()
    try:
        def _read_one():
            conn = _get_connection()
            try:
                cursor = conn.execute(query, params)
                row = cursor.fetchone()
                return dict(row) if row else None
            finally:
                conn.close()
        return await loop.run_in_executor(_executor, _read_one)
    except sqlite3.OperationalError as e:
        logger.error(f"DB read_one failed: {e}")
        raise
