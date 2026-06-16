"""
audit.py — TITAN Wave 1
Append-only audit trail. Every important system event is logged here.
CRITICAL: This module exposes NO delete or update methods. Ever.
If you are reading this and considering adding a delete method: don't.
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
    """
    Append an entry to the audit log.
    This is the ONLY write method this module exposes.
    """
    details_json = json.dumps(details) if details else None
    try:
        await execute_write(
            """INSERT INTO audit_log 
               (actor_telegram_id, action, target_telegram_id, details)
               VALUES (?, ?, ?, ?)""",
            (actor_telegram_id, action, target_telegram_id, details_json)
        )
    except Exception as e:
        # Audit failures must be logged but must NEVER crash the system
        logger.critical(f"AUDIT LOG FAILURE: {e} | action={action}")

async def get_recent(limit: int = 20) -> list:
    """Return the most recent audit entries. Read-only."""
    limit = min(limit, 100)  # Hard cap at 100 entries per call
    return await execute_read(
        "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT ?",
        (limit,)
    )
