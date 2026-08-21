from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from bot import database as db
from bot import texts
from bot.keyboards import main_menu_kb, back_to_main_kb

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await db.get_or_create_user(
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name or "",
    )
    await message.answer(texts.WELCOME, reply_markup=main_menu_kb())


@router.callback_query(F.data == "menu:main")
async def show_main_menu(call: CallbackQuery):
    await call.message.edit_text(texts.WELCOME, reply_markup=main_menu_kb())
    await call.answer()


@router.callback_query(F.data == "menu:profile")
async def show_profile(call: CallbackQuery):
    user_id = call.from_user.id
    balance = await db.get_balance(user_id)
    # لتبسيط المثال، عدد الطلبات هنا 0 -- ممكن تربطه لاحقًا مع جدول orders الفعلي
    text = texts.PROFILE_TEMPLATE.format(user_id=user_id, balance=balance, orders_count=0)
    await call.message.edit_text(text, reply_markup=back_to_main_kb())
    await call.answer()


@router.callback_query(F.data == "menu:policy")
async def show_policy(call: CallbackQuery):
    await call.message.edit_text(texts.POLICY_TEXT, reply_markup=back_to_main_kb())
    await call.answer()


@router.callback_query(F.data == "menu:help")
async def show_help(call: CallbackQuery):
    await call.message.edit_text(texts.HELP_TEXT, reply_markup=back_to_main_kb())
    await call.answer()


@router.callback_query(F.data == "menu:invites")
async def show_invites(call: CallbackQuery):
    await call.message.edit_text(texts.INVITES_TEXT, reply_markup=back_to_main_kb())
    await call.answer()
