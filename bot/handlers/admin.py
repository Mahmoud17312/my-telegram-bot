from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot import database as db
from bot.config import settings

router = Router()


class AdminTopup(StatesGroup):
    waiting_amount = State()


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


@router.callback_query(F.data.startswith("admtopup_approve:"))
async def admin_approve_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return await call.answer("غير مصرح", show_alert=True)
    topup_id = int(call.data.split(":")[1])
    await state.set_state(AdminTopup.waiting_amount)
    await state.update_data(topup_id=topup_id)
    await call.message.answer(f"أدخل المبلغ بالدولار لاعتماده لطلب الشحن #{topup_id}:")
    await call.answer()


@router.message(AdminTopup.waiting_amount)
async def admin_approve_amount(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    try:
        amount = float(message.text.strip())
        assert amount > 0
    except Exception:
        return await message.answer("قيمة غير صحيحة، أدخل رقم أكبر من صفر.")

    data = await state.get_data()
    topup_id = data["topup_id"]
    await state.clear()

    row = await db.approve_topup(topup_id, amount)
    if not row:
        return await message.answer("هذا الطلب تمت معالجته مسبقًا أو غير موجود.")

    await message.answer(f"✅ تم اعتماد {amount:.2f} USD للمستخدم {row['user_id']}.")
    try:
        await bot.send_message(
            row["user_id"],
            f"✅ تم شحن رصيدك بمبلغ {amount:.2f} USD بنجاح.",
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("admtopup_reject:"))
async def admin_reject(call: CallbackQuery, bot: Bot):
    if not is_admin(call.from_user.id):
        return await call.answer("غير مصرح", show_alert=True)
    topup_id = int(call.data.split(":")[1])
    row = await db.reject_topup(topup_id)
    if not row:
        await call.message.answer(f"طلب الشحن #{topup_id} تمت معالجته مسبقًا أو غير موجود.")
        return await call.answer()

    await call.message.answer(f"❌ تم رفض طلب الشحن #{topup_id}.")
    try:
        await bot.send_message(row["user_id"], "❌ تم رفض طلب شحن رصيدك. تواصل مع الدعم لمزيد من التفاصيل.")
    except Exception:
        pass
    await call.answer()
