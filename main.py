"""
main.py - TITAN Wave 1
Entry point only. No business logic here.
Starts the bot, runs migrations, handles graceful shutdown.
"""

import asyncio
import logging
import signal
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

Path("logs").mkdir(exist_ok=True)
Path("data").mkdir(exist_ok=True)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("titan")

async def main():
    logger.info("═══════════════════════════════════")
    logger.info("TITAN WAVE 1 STARTING")
    logger.info("═══════════════════════════════════")

    from db.migrations import run_migrations
    await run_migrations()
    logger.info("Database ready")

    token = os.getenv("BOT_TOKEN")
    if not token:
        logger.critical("BOT_TOKEN not set — cannot start")
        sys.exit(1)

    admin_id = os.getenv("ADMIN_TELEGRAM_ID")
    if not admin_id:
        logger.critical("ADMIN_TELEGRAM_ID not set — cannot start")
        sys.exit(1)

    pin_hash = os.getenv("ADMIN_PIN_HASH")
    if not pin_hash:
        logger.critical("ADMIN_PIN_HASH not set — cannot start")
        sys.exit(1)

    logger.info(f"Admin ID: {admin_id}")
    logger.info("All required environment variables present")

    from telegram.ext import ApplicationBuilder
    from bot.handlers.onboarding import register_onboarding
    from bot.handlers.admin import register_admin
    from bot.handlers.user import register_user

    app = ApplicationBuilder().token(token).build()

    register_onboarding(app)
    register_admin(app)
    register_user(app)

    logger.info("Bot handlers registered")

    stop_event = asyncio.Event()

    def handle_stop(signum, frame):
        logger.info(f"Signal {signum} received — stopping")
        stop_event.set()

    signal.signal(signal.SIGTERM, handle_stop)
    signal.signal(signal.SIGINT, handle_stop)

    await app.initialize()
    await app.start()
    await app.updater.start_polling(
        drop_pending_updates=True,
        allowed_updates=["message", "callback_query"]
    )

    logger.info("═══════════════════════════════════")
    logger.info("TITAN WAVE 1 ONLINE")
    logger.info("Bot is running and polling Telegram")
    logger.info("═══════════════════════════════════")

    await stop_event.wait()

    logger.info("TITAN WAVE 1 STOPPING — graceful shutdown")
    await app.updater.stop()
    await app.stop()
    await app.shutdown()
    logger.info("TITAN WAVE 1 STOPPED — goodbye")

if __name__ == "__main__":
    asyncio.run(main())
