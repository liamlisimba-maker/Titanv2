"""
responses.py — TITAN Wave 1
Every single string the bot sends lives here.
No hardcoded strings anywhere else in the codebase.
Edit this file to change bot language/tone.
"""

WELCOME = """
*Welcome to Titan* 🤖

Titan is an invite-only trading system.

If you have an invite link, use it to request access.
If you don't have one, contact the administrator.
"""

INVITE_INVALID = "⚠️ This invite link is invalid or has expired."

INVITE_SYSTEM_FULL = (
    "⚠️ Titan has reached its maximum user capacity. "
    "Please contact the administrator."
)

ALREADY_PENDING = (
    "⏳ Your application is already pending review. "
    "You'll be notified once the administrator makes a decision."
)

ALREADY_ACTIVE = "✅ You already have an active Titan account."

ALREADY_REJECTED = (
    "❌ Your account is not eligible. "
    "Please contact the administrator if you believe this is an error."
)

ALREADY_SUSPENDED = (
    "🚫 Your account has been suspended. "
    "Please contact the administrator."
)

APPLICATION_RECEIVED = """
✅ *Application Received*

Your request to join Titan has been submitted.
The administrator will review it shortly.
You'll receive a notification once a decision is made.
"""

APPROVED = """
✅ *Access Approved*

Welcome to Titan. Your account is now active.
Use /help to see available commands.
"""

REJECTED = (
    "❌ Your Titan access request has not been approved. "
    "Contact the administrator for more information."
)

SUSPENDED = "🚫 Your account has been suspended. Contact the administrator."

RESUMED = "✅ Your account has been reactivated. Welcome back."

HELP_USER = """
*Titan Commands* 📋
━━━━━━━━━━━━━━━━━━━━
/status — Your account status
/help — This message

━━━━━━━━━━━━━━━━━━━━
_Trading features coming in Wave 3_
"""
