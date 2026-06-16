"""
user.py - TITAN Wave 1
User-facing commands. Requires ACTIVE state.
"""
import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, Application
from config.constants import UserState
from core.user_manager import get_user
import bot.responses as R
from bot.middleware import check_leak, check_rate_limit

logger = logging.getLogger(__name__)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_leak(update, context):
        return
    user_id = update.effective_user.id
    if not check_rate_limit(user_id):
        await update.message.reply_text(R.RATE_LIMITED)
        return
    user = await get_user(user_id)
    if not user or UserState(user["state"]) != UserState.ACTIVE:
        await update.message.reply_text(R.INACTIVE_ACCOUNT)
        return
    await update.message.reply_text(
        f"*Your Titan Account*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Name: {user['full_name']}\n"
        f"Username: @{user['username']}\n"
        f"Status: {user['state']}\n"
        f"Joined: {user['joined_at']}\n"
        f"━━━━━━━━━━━━━━━━━━━━",
        parse_mode="Markdown"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_leak(update, context):
        return
    user_id = update.effective_user.id
    if not check_rate_limit(user_id):
        await update.message.reply_text(R.RATE_LIMITED)
        return
    user = await get_user(user_id)
    if not user or UserState(user["state"]) != UserState.ACTIVE:
        await update.message.reply_text(R.INACTIVE_ACCOUNT)
        return
    await update.message.reply_text(R.HELP_USER, parse_mode="Markdown")

def register_user(app: Application):
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("help", help_command))