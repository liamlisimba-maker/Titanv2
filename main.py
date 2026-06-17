"""
main.py - TITAN Wave 1
Entry point. Fixed for Railway deployment.
"""
import asyncio
import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

Path("logs").mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("titan")

def main():
    logger.info("TITAN WAVE 1 STARTING")

    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.critical("BOT_TOKEN not set")
        sys.exit(1)

    if not os.getenv("ADMIN_TELEGRAM_ID"):
        logger.critical("ADMIN_TELEGRAM_ID not set")
        sys.exit(1)

    if not os.getenv("ADMIN_PIN_HASH"):
        logger.critical("ADMIN_PIN_HASH not set")
        sys.exit(1)

    from db.migrations import run_migrations
    import asyncio as aio
    aio.run(run_migrations())
    logger.info("Database ready")

    from telegram.ext import ApplicationBuilder
    from bot.handlers.onboarding import register_onboarding
    from bot.handlers.admin import register_admin
    from bot.handlers.user import register_user

    app = ApplicationBuilder().token(token).build()

    register_onboarding(app)
    register_admin(app)
    register_user(app)

    logger.info("TITAN WAVE 1 ONLINE")
    logger.info("Bot is polling Telegram")

    app.run_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )

    logger.info("TITAN WAVE 1 STOPPED")

if __name__ == "__main__":
    main()