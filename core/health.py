"""
health.py - TITAN Wave 1
System health monitoring. Never raises - always returns a dict.
"""
import psutil
import logging
import time
from datetime import datetime
from db.database import execute_read_one

logger = logging.getLogger(__name__)
_start_time = time.time()

async def get_health() -> dict:
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": int(time.time() - _start_time),
        "wave": 1,
        "components": {}
    }

    try:
        row = await execute_read_one(
            "SELECT COUNT(*) as count FROM users"
        )
        active_row = await execute_read_one(
            "SELECT COUNT(*) as count FROM users WHERE state='ACTIVE'"
        )
        pending_row = await execute_read_one(
            "SELECT COUNT(*) as count FROM users WHERE state='PENDING_APPROVAL'"
        )
        health["components"]["database"] = {
            "status": "ok",
            "total_users": row["count"] if row else 0,
            "active_users": active_row["count"] if active_row else 0,
            "pending_users": pending_row["count"] if pending_row else 0
        }
    except Exception as e:
        health["components"]["database"] = {
            "status": "error", "detail": str(e)
        }
        health["status"] = "degraded"

    try:
        mem = psutil.virtual_memory()
        health["components"]["system"] = {
            "status": "ok",
            "memory_used_mb": round(mem.used / 1024 / 1024),
            "memory_total_mb": round(mem.total / 1024 / 1024),
            "cpu_percent": psutil.cpu_percent(interval=0.1)
        }
    except Exception as e:
        health["components"]["system"] = {
            "status": "error", "detail": str(e)
        }

    return health

def format_uptime(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"