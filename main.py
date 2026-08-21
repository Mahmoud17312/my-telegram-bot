import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings
from bot.database import init_db
from bot.handlers import get_root_router


logging.basicConfig(level=logging.INFO)


async def main():
    if settings.bot_token == "8367891612:AAHMpr1y5SKH-W2OYbteVl_yY2D31t26VUw":
        raise RuntimeError(
            "لازم تحط توكن البوت الحقيقي بملف .env تحت اسم BOT_TOKEN قبل التشغيل."
        )

    await init_db()

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(get_root_router())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
