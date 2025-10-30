Монолит на Render (бот + админка) — запуск одной службой
Start Command: python serve.py
Build Command: pip install -r requirements.txt && pip install -r web_admin/requirements.txt || true
Env: TELEGRAM_BOT_TOKEN, POST_CHANNEL_ID, FLASK_SECRET_KEY, ADMIN_NAME, JWT_SECRET, ENCRYPTION_KEY, ENVIRONMENT=production
Webhook off: https://api.telegram.org/bot<ТОКЕН>/setWebhook?url=
