import os
import asyncio
import logging
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.database import init_db
from bot.handlers import get_root_router

logging.basicConfig(level=logging.INFO)

# --- سيرفر وهمي لإرضاء Render ---
async def handle(request):
    return web.Response(text="Bot is active and running!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render يمرر البورت تلقائياً عبر متغير البيئة PORT
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"Web server started on port {port}")

# --- الدالة الرئيسية ---
async def main():
    if settings.bot_token == "8367891612:AAHMpr1y5SKH-W2OYbteVl_yY2D31t26VUw":
        raise RuntimeError(
            "لازم تحط توكن البوت الحقيقي بملف .env تحت اسم BOT_TOKEN قبل التشغيل."
        )

    await init_db()

    # تشغيل السيرفر الوهمي في الخلفية
    await start_web_server()

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(get_root_router())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
