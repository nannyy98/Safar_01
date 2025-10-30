import os, threading
from web_admin.app import app
import importlib

def run_bot():
    try:
        m=importlib.import_module('main')
        if hasattr(m,'run_bot'): m.run_bot()
        elif hasattr(m,'main'): m.main()
    except Exception as e:
        print('[serve] bot thread error:', e)

if __name__=='__main__':
    t=threading.Thread(target=run_bot, daemon=True); t.start()
    port=int(os.getenv('PORT','10000'))
    app.run(host='0.0.0.0', port=port)
