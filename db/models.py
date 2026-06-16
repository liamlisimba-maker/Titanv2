"""
models.py - TITAN Wave 1
Dataclass representations of database rows.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

@dataclass
class User:
    telegram_id: int
    username: Optional[str]
    full_name: Optional[str]
    state: str
    joined_at: str
    approved_at: Optional[str] = None
    approved_by: Optional[int] = None
    suspended_reason: Optional[str] = None
    api_configured: bool = False

@dataclass
class AuditEntry:
    actor_telegram_id: int
    action: str
    timestamp: str
    target_telegram_id: Optional[int] = None
    details: Optional[str] = None