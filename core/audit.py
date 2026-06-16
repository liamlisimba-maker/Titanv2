"""
audit.py - TITAN Wave 1
Append-only audit trail. NO delete or update methods exist here.
"""
import json
import logging
from typing import Optional
from db.database import execute_write, execute_read

logger = logging.getLogger(__name__)

async def log(
    actor_telegram_id: int,
    action: str,
    target_telegram_id: Optional[int] = None,
    details: Optional[dict] = None
) -> None:
    details_json = json.dumps(details) if details else None
    try:
        await execute_write(
            """INSERT INTO audit_log
               (actor_telegram_id, action, target_telegram_id, details)
               VALUES (?, ?, ?, ?)""",
            (actor_telegram_id, action, target_telegram_id, details_json)
        )
    except Exception as e:
        logger.critical(f"AUDIT LOG FAILURE: {e} | action={action}")

async def get_recent(limit: int = 20) -> list:
    limit = min(limit, 100)
    return await execute_read(
        "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )