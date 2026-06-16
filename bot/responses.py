"""
responses.py - TITAN Wave 1
Every string the bot sends lives here. No strings in handlers.
"""

WELCOME = (
    "*Welcome to Titan* 🤖\n\n"
    "Titan is an invite-only trading system.\n"
    "If you have an invite link, click it to request access."
)
INVITE_INVALID = "⚠️ This invite link is invalid or has expired."
INVITE_SYSTEM_FULL = "⚠️ Titan has reached maximum user capacity."
ALREADY_PENDING = "⏳ Your application is already pending review."
ALREADY_ACTIVE = "✅ You already have an active Titan account."
ALREADY_REJECTED = "❌ Your account is not eligible. Contact the administrator."
ALREADY_SUSPENDED = "🚫 Your account is suspended. Contact the administrator."
APPLICATION_RECEIVED = (
    "✅ *Application Received*\n\n"
    "The administrator will review your request shortly.\n"
    "You'll be notified once a decision is made."
)
APPROVED = (
    "✅ *Access Approved*\n\n"
    "Welcome to Titan. Your account is now active.\n"
    "Use /help to see available commands."
)
REJECTED = "❌ Your Titan access request was not approved."
SUSPENDED_MSG = "🚫 Your account has been suspended."
RESUMED = "✅ Your account has been reactivated. Welcome back."
HELP_USER = (
    "*Titan Commands* 📋\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "/status — Your account status\n"
    "/help — This message\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "_Trading features: Wave 3_"
)
ADMIN_REQUIRED = "🔒 Admin access required. Use /authorize first."
UNAUTHORIZED = "❌ You don't have permission to use this command."
RATE_LIMITED = "⚠️ Too many messages. Please slow down."
USER_NOT_FOUND = "❌ User not found."
INACTIVE_ACCOUNT = "⏸ Your account is not active."
LEAK_WARNING = (
    "⚠️ *Security Warning*\n\n"
    "Your message contained sensitive information and has been deleted.\n\n"
    "Never send API keys, passwords, or seed phrases via Telegram."
)
ADMIN_LOGIN_SUCCESS = "✅ Admin session started. Valid for 12 hours."
ADMIN_LOCKED_OUT = "🔒 Too many failed attempts. Locked for 30 minutes."
ADMIN_SESSION_EXPIRED = "⏰ Session expired. Use /authorize to login again."
BROADCAST_SENT = "📢 Broadcast sent to {count} active users."
BROADCAST_MSG = "📢 *Message from Titan*\n\n{message}"
INVITE_GENERATED = (
    "✅ *Invite Link Generated*\n"
    "━━━━━━━━━━━━━━━━━━━━\n"
    "{invite_link}\n\n"
    "⚠️ Single use. Expires in 48 hours.\n"
    "━━━━━━━━━━━━━━━━━━━━"
)