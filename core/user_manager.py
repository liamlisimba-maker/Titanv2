"""
user_manager.py — TITAN Wave 1
All user lifecycle logic. Single source of truth for user state.
Enforces valid state transitions. Raises on invalid moves.
Does NOT handle Telegram communication — that belongs in bot/handlers.
"""

import logging
from typing import Optional
from datetime import datetime
from config.constants import UserState, AuditAction, MAX_TOTAL_USERS
from db.database import execute_write, execute_read_one, execute_read
import core.audit as audit

logger = logging.getLogger(__name__)

class InvalidStateTransitionError(Exception):
    """Raised when an invalid user state transition is attempted."""
    pass

class UserLimitReachedError(Exception):
    """Raised when MAX_TOTAL_USERS would be exceeded."""
    pass

class UserNotFoundError(Exception):
    """Raised when a user lookup returns no result."""
    pass

# Valid transitions: {from_state: [allowed_to_states]}
VALID_TRANSITIONS = {
    UserState.PENDING_APPROVAL: [UserState.ACTIVE, UserState.REJECTED],
    UserState.ACTIVE: [UserState.PAUSED, UserState.SUSPENDED, UserState.REJECTED],
    UserState.PAUSED: [UserState.ACTIVE, UserState.SUSPENDED],
    UserState.SUSPENDED: [UserState.ACTIVE, UserState.REJECTED],
    UserState.REJECTED: [],
}

async def get_user(telegram_id: int) -> Optional[dict]:
    """Fetch a user by telegram_id. Returns dict or None."""
    row = await execute_read_one(
        "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
    )
    return dict(row) if row else None

async def get_all_users() -> list:
    """Return all users."""
    rows = await execute_read("SELECT * FROM users ORDER BY joined_at DESC")
    return [dict(r) for r in rows]

async def get_active_user_count() -> int:
    """Return total user count regardless of state."""
    row = await execute_read_one("SELECT COUNT(*) as count FROM users")
    return row["count"] if row else 0

async def create_user(
    telegram_id: int,
    username: Optional[str],
    full_name: Optional[str],
    invited_by: Optional[str] = None
) -> dict:
    """
    Create a new user in PENDING_APPROVAL state.
    Raises UserLimitReachedError if MAX_TOTAL_USERS would be exceeded.
    """
    count = await get_active_user_count()
    if count >= MAX_TOTAL_USERS:
        raise UserLimitReachedError(
            f"Cannot create user: system at capacity ({MAX_TOTAL_USERS} users)"
        )
    
    await execute_write(
        """INSERT INTO users (telegram_id, username, full_name, state, invited_by)
           VALUES (?, ?, ?, ?, ?)""",
        (telegram_id, username, full_name, 
         UserState.PENDING_APPROVAL.value, invited_by)
    )
    
    await audit.log(
        actor_telegram_id=telegram_id,
        action=AuditAction.USER_JOINED.value,
        target_telegram_id=telegram_id,
        details={"username": username, "full_name": full_name}
    )
    
    return await get_user(telegram_id)

async def transition_state(
    target_telegram_id: int,
    new_state: UserState,
    actor_telegram_id: int,
    reason: Optional[str] = None
) -> dict:
    """
    Move a user to a new state.
    Enforces valid transition rules.
    Raises InvalidStateTransitionError on invalid moves.
    """
    user = await get_user(target_telegram_id)
    if not user:
        raise UserNotFoundError(f"User {target_telegram_id} not found")
    
    current_state = UserState(user["state"])
    allowed = VALID_TRANSITIONS.get(current_state, [])
    
    if new_state not in allowed:
        raise InvalidStateTransitionError(
            f"Cannot transition {current_state.value} → {new_state.value}"
        )
    
    updates = {"state": new_state.value}
    if new_state == UserState.ACTIVE:
        updates["approved_at"] = datetime.utcnow().isoformat()
        updates["approved_by"] = actor_telegram_id
    if new_state == UserState.SUSPENDED:
        updates["suspended_at"] = datetime.utcnow().isoformat()
        updates["suspended_reason"] = reason
    
    await execute_write(
        "UPDATE users SET state=?, approved_at=?, approved_by=?, "
        "suspended_at=?, suspended_reason=? WHERE telegram_id=?",
        (
            updates.get("state"),
            updates.get("approved_at"),
            updates.get("approved_by"),
            updates.get("suspended_at"),
            updates.get("suspended_reason"),
            target_telegram_id
        )
    )
    
    await audit.log(
        actor_telegram_id=actor_telegram_id,
        action=AuditAction.USER_STATE_CHANGED.value,
        target_telegram_id=target_telegram_id,
        details={
            "from": current_state.value,
            "to": new_state.value,
            "reason": reason
        }
    )
    
    logger.info(
        f"State transition: {target_telegram_id} "
        f"{current_state.value} → {new_state.value} "
        f"by {actor_telegram_id}"
    )
    
    return await get_user(target_telegram_id)
