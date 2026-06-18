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
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

async def execute_write(query, params=()):
    async with _lock:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(_executor, _sw, query, params)

def _sw(query, params):
    conn = _get_connection()
    try:
        conn.execute(query, params)
        conn.commit()
    finally:
        conn.close()

async def execute_read(query, params=()):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _sr, query, params)

def _sr(query, params):
    conn = _get_connection()
    try:
        return [dict(r) for r in conn.execute(query, params).fetchall()]
    finally:
        conn.close()

async def execute_read_one(query, params=()):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(_executor, _sro, query, params)

def _sro(query, params):
    conn = _get_connection()
    try:
        row = conn.execute(query, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()
