"""
user_manager.py - TITAN Wave 1
All user lifecycle logic. Enforces valid state transitions.
"""
import logging
from typing import Optional
from datetime import datetime
from config.constants import UserState, AuditAction, MAX_TOTAL_USERS
from db.database import execute_write, execute_read_one, execute_read
import core.audit as audit

logger = logging.getLogger(__name__)

class InvalidStateTransitionError(Exception):
    pass

class UserLimitReachedError(Exception):
    pass

class UserNotFoundError(Exception):
    pass

VALID_TRANSITIONS = {
    UserState.PENDING_APPROVAL: [UserState.ACTIVE, UserState.REJECTED],
    UserState.ACTIVE: [UserState.PAUSED, UserState.SUSPENDED, UserState.REJECTED],
    UserState.PAUSED: [UserState.ACTIVE, UserState.SUSPENDED],
    UserState.SUSPENDED: [UserState.ACTIVE, UserState.REJECTED],
    UserState.REJECTED: [],
}

async def get_user(telegram_id: int) -> Optional[dict]:
    row = await execute_read_one(
        "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
    )
    return dict(row) if row else None

async def get_all_users() -> list:
    rows = await execute_read(
        "SELECT * FROM users ORDER BY joined_at DESC"
    )
    return [dict(r) for r in rows]

async def get_total_user_count() -> int:
    row = await execute_read_one(
        "SELECT COUNT(*) as count FROM users"
    )
    return row["count"] if row else 0

async def create_user(
    telegram_id: int,
    username: Optional[str],
    full_name: Optional[str],
    invited_by: Optional[str] = None
) -> dict:
    count = await get_total_user_count()
    if count >= MAX_TOTAL_USERS:
        raise UserLimitReachedError("System at user capacity")

    await execute_write(
        """INSERT INTO users
           (telegram_id, username, full_name, state, invited_by)
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
    user = await get_user(target_telegram_id)
    if not user:
        raise UserNotFoundError(f"User {target_telegram_id} not found")

    current_state = UserState(user["state"])
    allowed = VALID_TRANSITIONS.get(current_state, [])

    if new_state not in allowed:
        raise InvalidStateTransitionError(
            f"Cannot transition {current_state.value} to {new_state.value}"
        )

    approved_at = datetime.utcnow().isoformat() if new_state == UserState.ACTIVE else None
    approved_by = actor_telegram_id if new_state == UserState.ACTIVE else None
    suspended_at = datetime.utcnow().isoformat() if new_state == UserState.SUSPENDED else None

    await execute_write(
        """UPDATE users SET state=?, approved_at=?, approved_by=?,
           suspended_at=?, suspended_reason=? WHERE telegram_id=?""",
        (new_state.value, approved_at, approved_by,
         suspended_at, reason, target_telegram_id)
    )

    await audit.log(
        actor_telegram_id=actor_telegram_id,
        action=AuditAction.USER_STATE_CHANGED.value,
        target_telegram_id=target_telegram_id,
        details={"from": current_state.value, "to": new_state.value, "reason": reason}
    )

    return await get_user(target_telegram_id)