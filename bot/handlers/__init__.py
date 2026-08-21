from aiogram import Router

from bot.handlers.menu import router as menu_router
from bot.handlers.shop import router as shop_router
from bot.handlers.topup import router as topup_router
from bot.handlers.admin import router as admin_router


def get_root_router() -> Router:
    root = Router()
    root.include_router(admin_router)   # الأدمن أولًا عشان أزراره ما تتعارض
    root.include_router(menu_router)
    root.include_router(shop_router)
    root.include_router(topup_router)
    return root
