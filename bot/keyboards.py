from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🛒 المنتجات", callback_data="menu:products")
    kb.button(text="👤 ملفي", callback_data="menu:profile")
    kb.button(text="🎁 الدعوات", callback_data="menu:invites")
    kb.button(text="💰 شحن رصيد", callback_data="menu:topup")
    kb.button(text="💳 شحن بكود", callback_data="menu:redeem")
    kb.button(text="🛡 سياسة البوت", callback_data="menu:policy")
    kb.button(text="❓ المساعدة", callback_data="menu:help")
    kb.adjust(1, 2, 2, 2)
    return kb.as_markup()


def categories_kb(categories: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for c in categories:
        kb.button(text=f"{c['emoji']} {c['name']}".strip(), callback_data=f"cat:{c['id']}")
    kb.button(text="⬅️ رجوع", callback_data="menu:main")
    kb.adjust(2)
    return kb.as_markup()


def products_kb(products: list[dict], category_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for p in products:
        kb.button(text=f"{p['name']} — {p['price']} USD", callback_data=f"prod:{p['id']}")
    kb.button(text="⬅️ رجوع للفئات", callback_data="menu:products")
    kb.adjust(1)
    return kb.as_markup()


def product_detail_kb(product_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🛍 شراء", callback_data=f"buy:{product_id}")
    kb.button(text="⬅️ رجوع", callback_data="menu:products")
    kb.adjust(1)
    return kb.as_markup()


def quantity_kb(product_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for q in [1, 2, 3, 5, 10]:
        kb.button(text=str(q), callback_data=f"qty:{product_id}:{q}")
    kb.button(text="✏️ كمية أخرى", callback_data=f"qtycustom:{product_id}")
    kb.button(text="⬅️ رجوع", callback_data=f"prod:{product_id}")
    kb.button(text="❌ إلغاء", callback_data="menu:main")
    kb.adjust(4, 1, 2)
    return kb.as_markup()


def order_confirm_kb(order_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ تأكيد الشراء", callback_data=f"confirm:{order_id}")
    kb.button(text="❌ إلغاء", callback_data=f"cancelorder:{order_id}")
    kb.adjust(1)
    return kb.as_markup()


def insufficient_balance_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💰 شحن رصيد", callback_data="menu:topup")
    kb.button(text="⬅️ رجوع", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def topup_methods_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🟡 Binance Pay", callback_data="topup:binance")
    kb.button(text="🔗 BEP20 (USDT)", callback_data="topup:BEP20")
    kb.button(text="🔗 Polygon (USDT)", callback_data="topup:POLYGON")
    kb.button(text="🔗 TRC20 (USDT)", callback_data="topup:TRC20")
    kb.button(text="❌ إغلاق", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()


def back_to_main_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ رجوع للقائمة الرئيسية", callback_data="menu:main")
    kb.adjust(1)
    return kb.as_markup()
