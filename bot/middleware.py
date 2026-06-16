"""
middleware.py - TITAN Wave 1
Leak detection, rate limiting, auth checks.
Runs before every handler.
"""
import logging
import time
from collections import defaultdict
from telegram import Update
from telegram.ext import ContextTypes
from config.constants import (
    LEAK_PROTECTED_TERMS, RATE_LIMIT_MESSAGES,
    RATE_LIMIT_WINDOW_SECONDS, AuditAction
)
from config.settings import ADMIN_TELEGRAM_ID
import core.audit as audit

logger = logging.getLogger(__name__)
_rate_limit_store = defaultdict(list)

async def check_leak(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.message or not update.message.text:
        return False
    text = update.message.text.lower()
    for term in LEAK_PROTECTED_TERMS:
        if term in text:
            try:
                await update.message.delete()
            except Exception as e:
                logger.warning(f"Could not delete leak message: {e}")
            try:
                await update.message.chat.send_message(
                    "⚠️ *Security Warning*\n\n"
                    "Sensitive information detected and deleted.\n\n"
                    "Never send API keys, passwords, or seed phrases via Telegram.",
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Could not warn user of leak: {e}")
            await audit.log(
                actor_telegram_id=update.effective_user.id,
                action=AuditAction.LEAK_DETECTED.value,
                details={
                    "username": update.effective_user.username,
                    "term_detected": term
                }
            )
            try:
                await context.bot.send_message(
                    chat_id=ADMIN_TELEGRAM_ID,
                    text=(
                        f"🚨 *Leak Detection Alert*\n"
                        f"User: @{update.effective_user.username}\n"
                        f"ID: `{update.effective_user.id}`\n"
                        f"Term matched: `{term}`\n"
                        f"Message was deleted."
                    ),
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Could not alert admin of leak: {e}")
            return True
    return False

def check_rate_limit(user_id: int) -> bool:
    now = time.time()
    window_start = now - RATE_LIMIT_WINDOW_SECONDS
    _rate_limit_store[user_id] = [
        t for t in _rate_limit_store[user_id] if t > window_start
    ]
    if len(_rate_limit_store[user_id]) >= RATE_LIMIT_MESSAGES:
        return False
    _rate_limit_store[user_id].append(now)
    return True