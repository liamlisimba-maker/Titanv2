"""
onboarding.py - TITAN Wave 1
/start handler and invite-based join flow.
"""
import logging
import uuid
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ContextTypes, CommandHandler, CallbackQueryHandler, Application
)
from config.constants import UserState, AuditAction, INVITE_TOKEN_EXPIRY_HOURS
from config.settings import ADMIN_TELEGRAM_ID
from core.user_manager import (
    get_user, create_user, UserLimitReachedError, transition_state
)
from db.database import execute_write, execute_read_one
import bot.responses as R
import core.audit as audit
from bot.middleware import check_leak, check_rate_limit

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if await check_leak(update, context):
        return
    if not check_rate_limit(user_id):
        await update.message.reply_text(R.RATE_LIMITED)
        return
    args = context.args
    if not args or not args[0].startswith("join_"):
        await update.message.reply_text(R.WELCOME, parse_mode="Markdown")
        return
    token = args[0][5:]
    await handle_join(update, context, token)

async def handle_join(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    token: str
):
    user = update.effective_user
    existing = await get_user(user.id)

    if existing:
        state = UserState(existing["state"])
        state_messages = {
            UserState.PENDING_APPROVAL: R.ALREADY_PENDING,
            UserState.ACTIVE: R.ALREADY_ACTIVE,
            UserState.REJECTED: R.ALREADY_REJECTED,
            UserState.SUSPENDED: R.ALREADY_SUSPENDED,
            UserState.PAUSED: R.ALREADY_ACTIVE,
        }
        await update.message.reply_text(
            state_messages.get(state, R.UNAUTHORIZED)
        )
        return

    token_row = await execute_read_one(
        "SELECT * FROM invite_tokens WHERE token=? AND is_used=FALSE",
        (token,)
    )

    if not token_row:
        await update.message.reply_text(R.INVITE_INVALID)
        return

    expires_at = datetime.fromisoformat(token_row["expires_at"])
    if datetime.utcnow() > expires_at:
        await update.message.reply_text(R.INVITE_INVALID)
        await audit.log(
            actor_telegram_id=user.id,
            action=AuditAction.INVITE_USED.value,
            details={"result": "expired", "token": token[:8]}
        )
        return

    try:
        await create_user(
            telegram_id=user.id,
            username=user.username,
            full_name=user.full_name,
            invited_by=token
        )
    except UserLimitReachedError:
        await update.message.reply_text(R.INVITE_SYSTEM_FULL)
        return

    await execute_write(
        """UPDATE invite_tokens
           SET is_used=TRUE, used_by=?, used_at=?
           WHERE token=?""",
        (user.id, datetime.utcnow().isoformat(), token)
    )

    await audit.log(
        actor_telegram_id=user.id,
        action=AuditAction.INVITE_USED.value,
        details={"result": "success", "token": token[:8]}
    )

    await update.message.reply_text(
        R.APPLICATION_RECEIVED, parse_mode="Markdown"
    )

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Approve", callback_data=f"approve_{user.id}"
            ),
            InlineKeyboardButton(
                "❌ Reject", callback_data=f"reject_{user.id}"
            )
        ]
    ])

    await context.bot.send_message(
        chat_id=ADMIN_TELEGRAM_ID,
        text=(
            f"🔔 *New Access Request*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Name: {user.full_name}\n"
            f"Username: @{user.username}\n"
            f"Telegram ID: `{user.id}`\n"
            f"Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n"
            f"━━━━━━━━━━━━━━━━━━━━"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )

async def approval_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_TELEGRAM_ID:
        await query.edit_message_text("❌ Unauthorized.")
        return

    data = query.data
    action, target_id_str = data.split("_", 1)
    target_id = int(target_id_str)

    if action == "approve":
        try:
            await transition_state(
                target_id, UserState.ACTIVE, ADMIN_TELEGRAM_ID
            )
            await context.bot.send_message(
                chat_id=target_id,
                text=R.APPROVED,
                parse_mode="Markdown"
            )
            await query.edit_message_text(
                f"✅ User {target_id} approved and notified."
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Approval failed: {e}")

    elif action == "reject":
        try:
            await transition_state(
                target_id, UserState.REJECTED, ADMIN_TELEGRAM_ID
            )
            await context.bot.send_message(
                chat_id=target_id, text=R.REJECTED
            )
            await query.edit_message_text(
                f"❌ User {target_id} rejected and notified."
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Rejection failed: {e}")

def register_onboarding(app: Application):
    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        CallbackQueryHandler(
            approval_callback,
            pattern="^(approve|reject)_"
        )
    )