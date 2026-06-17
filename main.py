import logging, os, sys, asyncio
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
Path("data").mkdir(exist_ok=True)
logging.basicConfig(level="INFO", format="%(asctime)s %(name)s: %(message)s", handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("titan")

async def main():
    logger.info("TITAN WAVE 1 STARTING")
    token = os.getenv("BOT_TOKEN")
    if not token:
        sys.exit("BOT_TOKEN not set")
    from db.migrations import run_migrations
    await run_migrations()
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
    async with app:
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True)
        await asyncio.Event().wait()

asyncio.run(main())