"""
settings.py - TITAN Wave 1
Loads environment variables. Single place for all config access.
"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))
WAR_ROOM_CHAT_ID = os.getenv("WAR_ROOM_CHAT_ID")
ADMIN_PIN_HASH = os.getenv("ADMIN_PIN_HASH")
DB_PATH = os.getenv("DB_PATH", "./data/titan.db")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")