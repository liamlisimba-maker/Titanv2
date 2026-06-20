"""
admin.py - TITAN Wave 1
Admin command handlers. All require valid 
admin session except /authorize.
"""
import logging
import uuid
import hashlib, hmac
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import (
    ContextTypes, CommandHandler, Application
)
from config.constants import (
    UserState, AuditAction,
    ADMIN_PIN_MAX_ATTEMPTS,
    ADMIN_PIN_LOCKOUT_SECONDS,
    ADMIN_SESSION_DURATION_HOURS,
    INVITE_TOKEN_EXPIRY_HOURS
)
from config.settings import (
    ADMIN_TELEGRAM_ID, ADMIN_PIN_HASH
)
from core.user_manager import (
    get_user, get_all_users,
    transition_state, UserNotFoundError
)
from core.health import get_health, format_uptime
from db.database import (
    execute_write, execute_read_one, execute_read
)
import core.audit as audit
import bot.responses as R
from bot.middleware import check_leak, check_rate_limit

logger = logging.getLogger(__name__)

async def is_admin_session_valid(telegram_id: int) -> bool:
    row = await execute_read_one(
        """SELECT * FROM admin_sessions
           WHERE telegram_id=? 
           AND is_active=TRUE 
           AND expires_at > ?""",
        (telegram_id, datetime.utcnow().isoformat())
    )
    return row is not None

async def is_admin_locked_out(telegram_id: int) -> bool:
    cutoff = (
        datetime.utcnow() - 
        timedelta(seconds=ADMIN_PIN_LOCKOUT_SECONDS)
    ).isoformat()
    row = await execute_read_one(
        """SELECT COUNT(*) as count 
           FROM admin_pin_attempts
           WHERE telegram_id=? 
           AND success=FALSE 
           AND attempted_at > ?""",
        (telegram_id, cutoff)
    )
    return row and row["count"] >= ADMIN_PIN_MAX_ATTEMPTS

async def require_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
) -> bool:
    user_id = update.effective_user.id
    if user_id != ADMIN_TELEGRAM_ID:
        await update.message.reply_text(R.UNAUTHORIZED)
        return False
    if not await is_admin_session_valid(user_id):
        await update.message.reply_text(
            R.ADMIN_SESSION_EXPIRED
        )
        return False
    return True

async def authorize(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user_id = update.effective_user.id
    if user_id != ADMIN_TELEGRAM_ID:
        await update.message.reply_text(R.UNAUTHORIZED)
        return
    try:
        await update.message.delete()
    except Exception:
        pass
    if not context.args:
        await update.effective_chat.send_message(
            "Usage: /authorize YOUR_PIN"
        )
        return
    if await is_admin_locked_out(user_id):
        await update.effective_chat.send_message(
            R.ADMIN_LOCKED_OUT
        )
        return
    pin = context.args[0]
    pin_hash = ADMIN_PIN_HASH if ADMIN_PIN_HASH else ""
    try:
        valid = (hashlib.sha256(pin.encode()).hexdigest() == pin_hash)
    except Exception:
        valid = False
    await execute_write(
        """INSERT INTO admin_pin_attempts 
           (telegram_id, success) VALUES (?, ?)""",
        (user_id, valid)
    )
    if not valid:
        await audit.log(
            user_id,
            AuditAction.ADMIN_LOGIN_FAILED.value
        )
        if await is_admin_locked_out(user_id):
            await audit.log(
                user_id,
                AuditAction.ADMIN_LOCKOUT.value
            )
            await update.effective_chat.send_message(
                R.ADMIN_LOCKED_OUT
            )
        else:
            await update.effective_chat.send_message(
                "❌ Incorrect PIN."
            )
        return
    expires_at = datetime.utcnow() + timedelta(
        hours=ADMIN_SESSION_DURATION_HOURS
    )
    token = str(uuid.uuid4())
    await execute_write(
        """INSERT INTO admin_sessions 
           (telegram_id, session_token, expires_at)
           VALUES (?, ?, ?)""",
        (user_id, token, expires_at.isoformat())
    )
    await audit.log(user_id, AuditAction.ADMIN_LOGIN.value)
    await update.effective_chat.send_message(
        R.ADMIN_LOGIN_SUCCESS
    )

async def dashboard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not await require_admin(update, context):
        return
    health = await get_health()
    db = health["components"].get("database", {})
    sys_info = health["components"].get("system", {})
    emoji = "🟢" if health["status"] == "healthy" else "🟡"
    await update.message.reply_text(
        f"*Titan Dashboard* {emoji}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Status: {health['status'].title()}\n"
        f"Uptime: {format_uptime(health['uptime_seconds'])}\n"
        f"Wave: 1 — Foundation\n\n"
        f"*Users*\n"
        f"  Total: {db.get('total_users', 0)} / 6\n"
        f"  Active: {db.get('active_users', 0)}\n"
        f"  Pending: {db.get('pending_users', 0)}\n\n"
        f"*System*\n"
        f"  Memory: {sys_info.get('memory_used_mb', '?')}MB\n"
        f"  CPU: {sys_info.get('cpu_percent', '?')}%\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"_Trading: NOT ENABLED (Wave 3)_",
        parse_mode="Markdown"
    )

async def users_list(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not await require_admin(update, context):
        return
    users = await get_all_users()
    if not users:
        await update.message.reply_text("No users found.")
        return
    lines = ["*All Users*\n━━━━━━━━━━━━━━━━━━━━"]
    for u in users:
        lines.append(
            f"• {u['full_name']} (@{u['username']})\n"
            f"  ID: `{u['telegram_id']}` | {u['state']}"
        )
    await update.message.reply_text(
        "\n".join(lines), parse_mode="Markdown"
    )

async def approve_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not await require_admin(update, context):
        return
    if not context.args:
        await update.message.reply_text(
            "Usage: /approve TELEGRAM_ID"
        )
        return
    try:
        target_id = int(context.args[0])
        await transition_state(
            target_id, UserState.ACTIVE, ADMIN_TELEGRAM_ID
        )
        await context.bot.send_message(
            chat_id=target_id,
            text=R.APPROVED,
            parse_mode="Markdown"
        )
        await update.message.reply_text(
            f"✅ User {target_id} approved."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def reject_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not await require_admin(update, context):
        return
    if not context.args:
        await update.message.reply_text(
            "Usage: /reject TELEGRAM_ID"
        )
        return
    try:
        target_id = int(context.args[0])
        await transition_state(
            target_id, UserState.REJECTED, ADMIN_TELEGRAM_ID
        )
        await context.bot.send_message(
            chat_id=target_id, text=R.REJECTED
        )
        await update.message.reply_text(
            f"❌ User {target_id} rejected."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def suspend_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not await require_admin(update, context):
        return
    if len(context.args) < 2:
        await update.message.reply_text(
            "Usage: /suspend TELEGRAM_ID REASON"
        )
        return
    try:
        target_id = int(context.args[0])
        reason = " ".join(context.args[1:])
        await transition_state(
            target_id, UserState.SUSPENDED,
            ADMIN_TELEGRAM_ID, reason
        )
        await context.bot.send_message(
            chat_id=target_id, text=R.SUSPENDED_MSG
        )
        await update.message.reply_text(
            f"🚫 User {target_id} suspended."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def resume_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not await require_admin(update, context):
        return
    if not context.args:
        await update.message.reply_text(
            "Usage: /resume TELEGRAM_ID"
        )
        return
    try:
        target_id = int(context.args[0])
        await transition_state(
            target_id, UserState.ACTIVE, ADMIN_TELEGRAM_ID
        )
        await context.bot.send_message(
            chat_id=target_id, text=R.RESUMED
        )
        await update.message.reply_text(
            f"✅ User {target_id} resumed."
        )
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def invite(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not await require_admin(update, context):
        return
    token = str(uuid.uuid4()).replace("-", "")[:16]
    expires_at = (
        datetime.utcnow() + 
        timedelta(hours=INVITE_TOKEN_EXPIRY_HOURS)
    ).isoformat()
    await execute_write(
        """INSERT INTO invite_tokens 
           (token, created_by, expires_at)
           VALUES (?, ?, ?)""",
        (token, ADMIN_TELEGRAM_ID, expires_at)
    )
    await audit.log(
        ADMIN_TELEGRAM_ID,
        AuditAction.INVITE_GENERATED.value,
        details={"token": token[:8]}
    )
    bot_me = await context.bot.get_me()
    link = f"https://t.me/{bot_me.username}?start=join_{token}"
    await update.message.reply_text(
        R.INVITE_GENERATED.format(invite_link=link),
        parse_mode="Markdown"
    )

async def broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not await require_admin(update, context):
        return
    if not context.args:
        await update.message.reply_text(
            "Usage: /broadcast YOUR MESSAGE"
        )
        return
    message = " ".join(context.args)
    users = await get_all_users()
    active = [
        u for u in users
        if u["state"] == UserState.ACTIVE.value
    ]
    count = 0
    for u in active:
        try:
            await context.bot.send_message(
                chat_id=u["telegram_id"],
                text=R.BROADCAST_MSG.format(message=message),
                parse_mode="Markdown"
            )
            count += 1
        except Exception as e:
            logger.warning(
                f"Broadcast failed for "
                f"{u['telegram_id']}: {e}"
            )
    await audit.log(
        ADMIN_TELEGRAM_ID,
        AuditAction.BROADCAST_SENT.value,
        details={"sent_to": count}
    )
    await update.message.reply_text(
        R.BROADCAST_SENT.format(count=count)
    )

async def logs_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not await require_admin(update, context):
        return
    limit = int(context.args[0]) if context.args else 20
    entries = await audit.get_recent(limit)
    if not entries:
        await update.message.reply_text(
            "No audit entries found."
        )
        return
    lines = [f"*Last {limit} Audit Entries*\n━━━━━━━━━━━━━━━━━━━━"]
    for e in entries:
        lines.append(
            f"• `{e['action']}`\n"
            f"  by `{e['actor_telegram_id']}`\n"
            f"  {e['timestamp']}"
        )
    text = "\n".join(lines)
    if len(text) > 4000:
        text = text[:3900] + "\n\n_...truncated_"
    await update.message.reply_text(
        text, parse_mode="Markdown"
    )

async def healthcheck(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not await require_admin(update, context):
        return
    health = await get_health()
    db = health["components"].get("database", {})
    sys_info = health["components"].get("system", {})
    emoji = "🟢" if health["status"] == "healthy" else "🔴"
    await update.message.reply_text(
        f"*Titan Health Check* {emoji}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Status: {health['status'].title()}\n"
        f"Uptime: {format_uptime(health['uptime_seconds'])}\n\n"
        f"*Database*: {db.get('status', 'unknown')}\n"
        f"*Memory*: {sys_info.get('memory_used_mb', '?')}MB\n"
        f"*CPU*: {sys_info.get('cpu_percent', '?')}%\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"_Wave 1 — Foundation Only_",
        parse_mode="Markdown"
    )

def register_admin(app: Application):
    app.add_handler(CommandHandler("authorize", authorize))
    app.add_handler(CommandHandler("dashboard", dashboard))
    app.add_handler(CommandHandler("users", users_list))
    app.add_handler(CommandHandler("approve", approve_user))
    app.add_handler(CommandHandler("reject", reject_user))
    app.add_handler(CommandHandler("suspend", suspend_user))
    app.add_handler(CommandHandler("resume", resume_user))
    app.add_handler(CommandHandler("invite", invite))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("logs", logs_command))
    app.add_handler(CommandHandler("healthcheck", healthcheck))