"""
constants.py — TITAN Wave 1
Hard-coded system constants. These CANNOT be changed at runtime.
No Telegram command, no config file, no environment variable
can override these values. They are law.
"""

from enum import Enum

# ── Hard Locks ─────────────────────────────────────────────
INVITE_ONLY = True
ADMIN_APPROVAL_REQUIRED = True
MAX_TOTAL_USERS = 6          # Admin + 5 users absolute ceiling
AUDIT_IMMUTABLE = True
WAVE = 1

# ── Admin Security ──────────────────────────────────────────
ADMIN_PIN_LENGTH = 6
ADMIN_PIN_MAX_ATTEMPTS = 3
ADMIN_PIN_LOCKOUT_SECONDS = 1800    # 30 minutes
ADMIN_SESSION_DURATION_HOURS = 12

# ── Invite Tokens ───────────────────────────────────────────
INVITE_TOKEN_EXPIRY_HOURS = 48
INVITE_TOKEN_SINGLE_USE = True

# ── Rate Limiting ───────────────────────────────────────────
RATE_LIMIT_MESSAGES = 10
RATE_LIMIT_WINDOW_SECONDS = 10

# ── Leak Detection ──────────────────────────────────────────
LEAK_PROTECTED_TERMS = [
    "api key", "api secret", "private key", "seed phrase",
    "mnemonic", "secret key", "access key", "password"
]

# ── Telegram ────────────────────────────────────────────────
MAX_MESSAGE_LENGTH = 4000
HEARTBEAT_INTERVAL_SECONDS = 60

class UserState(str, Enum):
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    SUSPENDED = "SUSPENDED"
    REJECTED = "REJECTED"

class AuditAction(str, Enum):
    USER_JOINED = "USER_JOINED"
    USER_APPROVED = "USER_APPROVED"
    USER_REJECTED = "USER_REJECTED"
    USER_SUSPENDED = "USER_SUSPENDED"
    USER_RESUMED = "USER_RESUMED"
    USER_PAUSED = "USER_PAUSED"
    ADMIN_LOGIN = "ADMIN_LOGIN"
    ADMIN_LOGIN_FAILED = "ADMIN_LOGIN_FAILED"
    ADMIN_LOCKOUT = "ADMIN_LOCKOUT"
    CONFIG_CHANGED = "CONFIG_CHANGED"
    INVITE_GENERATED = "INVITE_GENERATED"
    INVITE_USED = "INVITE_USED"
    INVITE_EXPIRED = "INVITE_EXPIRED"
    LEAK_DETECTED = "LEAK_DETECTED"
    BROADCAST_SENT = "BROADCAST_SENT"
    SYSTEM_STARTED = "SYSTEM_STARTED"
    SYSTEM_STOPPED = "SYSTEM_STOPPED"
    USER_STATE_CHANGED = "USER_STATE_CHANGED"
