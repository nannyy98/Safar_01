"""Интеграция веб‑админ панели с Telegram ботом (универсальная версия для Render).
Размещай этот файл как: project/web_admin/bot_integration.py
"""
from __future__ import annotations

import os
import sys
import json
import time
import logging
import urllib.request
import urllib.parse
from pathlib import Path

# --- Определяем корень проекта надёжно (работает и из web_admin/, и из корня) ---
HERE = Path(__file__).resolve()
CANDIDATES = [HERE.parent, HERE.parent.parent, HERE.parent.parent.parent]
REPO_ROOT = None
for d in CANDIDATES:
    if (d / "main.py").exists() or (d / "web_admin").exists() or (d / "project").exists():
        REPO_ROOT = d
        break
if REPO_ROOT is None:
    REPO_ROOT = HERE.parent  # запасной вариант

# Чтобы можно было импортировать config / database
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Импорты конфигурации (с защитой)
try:
    from config import BOT_TOKEN, POST_CHANNEL_ID
except Exception:
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
    POST_CHANNEL_ID = os.getenv("POST_CHANNEL_ID", "-1000000000000")

class TelegramBotIntegration:
    def __init__(self) -> None:
        self.token = BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.channel_id = POST_CHANNEL_ID

    # --- Сигнал боту обновить данные (бот читает файл data_update_flag.txt) ---
    def trigger_bot_data_reload(self) -> bool:
        try:
            flag = REPO_ROOT / "data_update_flag.txt"
            flag.write_text(str(time.time()), encoding="utf-8")
            logging.info("[bot_integration] data_update_flag.txt written at %s", flag)
            return True
        except Exception as e:
            logging.error("[bot_integration] cannot write flag: %s", e)
            return False

    # --- Отправка сообщений ---
    def send_message(self, chat_id, text, reply_markup=None):
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML",
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        try:
            body = urllib.parse.urlencode(data).encode("utf-8")
            req = urllib.request.Request(url, data=body, method="POST")
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logging.warning("[bot_integration] send_message error: %s", e)
            return None

    def send_photo(self, chat_id, photo_url, caption="", reply_markup=None):
        url = f"{self.base_url}/sendPhoto"
        data = {
            "chat_id": chat_id,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": "HTML",
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        try:
            body = urllib.parse.urlencode(data).encode("utf-8")
            req = urllib.request.Request(url, data=body, method="POST")
            with urllib.request.urlopen(req) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            logging.warning("[bot_integration] send_photo error: %s", e)
            return None

    def send_to_channel(self, message: str):
        return self.send_message(self.channel_id, message, None)

    def send_photo_to_channel(self, photo_url: str, caption: str = "", reply_markup=None):
        return self.send_photo(self.channel_id, photo_url, caption, reply_markup)

    def send_broadcast(self, message, user_list):
        ok, bad = 0, 0
        for user in user_list:
            telegram_id = user[0] if isinstance(user, (list, tuple)) else user.get("telegram_id")
            r = self.send_message(telegram_id, message)
            if r and r.get("ok"):
                ok += 1
            else:
                bad += 1
        return ok, bad

    def notify_admins(self, message: str):
        try:
            from database import DatabaseManager
            db = DatabaseManager()
            admins = db.execute_query("SELECT telegram_id FROM users WHERE is_admin = 1")
            for a in admins:
                self.send_message(a[0], message)
        except Exception as e:
            logging.warning("[bot_integration] notify_admins error: %s", e)

    def test_connection(self) -> bool:
        try:
            with urllib.request.urlopen(f"{self.base_url}/getMe") as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return bool(data.get("ok"))
        except Exception as e:
            logging.warning("[bot_integration] test_connection error: %s", e)
            return False

# Глобальный экземпляр (совместим с импортом `from bot_integration import telegram_bot`)
telegram_bot = TelegramBotIntegration()
