import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from json import load, dump
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")

logging.basicConfig(level=logging.INFO, stream=sys.stdout) 

TOKEN = os.getenv("BOT_TOKEN")
FILE_CONFIG = BASE_DIR / "config.json"

if not TOKEN:
    sys.exit("❌ Ошибка: Переменная BOT_TOKEN не найдена в файле .env!")

try:
    with open(FILE_CONFIG, "r", encoding="utf-8") as config:
        config_user = load(config)
except FileNotFoundError:
    config_user = {
        "id": -1,
        "channel_link": "",
        "settings": {"link_preview": True},
        "drafts": {}
    }

def save_config():
    with open(FILE_CONFIG, "w", encoding="utf-8") as config:
        dump(config_user, config, indent=4)

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()