from aiogram import Router, F, Bot, types
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.bep20 import verify_user_payment
from bot import database as db
from bot import texts
from bot.config import settings
from bot.states import TopupFlow
from bot.keyboards import topup_methods_kb, back_to_main_kb

router = Router()


@router.callback_query(F.data == "menu:topup")
async def show_topup_methods(call: CallbackQuery):
    await call.message.edit_text(texts.TOPUP_METHODS_TEXT, reply_markup=topup_methods_kb())
    await call.answer()


@router.callback_query(F.data.startswith("topup:"))
async def choose_topup_method(call: CallbackQuery, state: FSMContext):
    method = call.data.split(":")[1]

    if method == "binance":
        text = (
            "🟡 **الدفع عبر Binance Pay**\n\n"
            "أرسل المبلغ الذي تريده إلى معرف الإدارة (Binance Pay ID):\n"
            f"`{settings.wallets.get('BEP20', '---')}`\n\n"
            "⚠️ بعد الدفع، أرسل هنا رقم الطلب (Order ID) من إيصال Binance Pay "
            "ليتم مراجعة عملية الشحن يدويًا من قبل الإدارة."
        )
        await state.set_state(TopupFlow.waiting_order_ref)
        await state.update_data(method=method)
        await call.message.edit_text(text, reply_markup=back_to_main_kb(), parse_mode="Markdown")

    elif method == "BEP20":
        address = settings.wallets.get("BEP20", "غير متوفر حاليًا")
        text = (
            "🔗 **الدفع عبر BEP20 (USDT)**\n\n"
            f"العنوان:\n`{address}`\n\n"
            "⚠️ تأكد من الإرسال عبر شبكة **BNB Smart Chain (BEP20)** فقط.\n\n"
            "بعد إتمام التحويل من محفظتك، اضغط على زر **فحص الدفع الآن** ليتم التحقق وإضافة الرصيد تلقائيًا."
        )
        
        # لوحة المفاتيح تشمل زر الفحص التلقائي وزر الرجوع
        kb = InlineKeyboardBuilder()
        kb.button(text="🔄 تم الدفع — فحص الآن", callback_data="check_pay_0.5")
        kb.button(text="رجوع ⬅️", callback_data="menu:topup")
        kb.adjust(1)

        await call.message.edit_text(text, reply_markup=kb.as_markup(), parse_mode="Markdown")

    else:
        address = settings.wallets.get(method, "غير متوفر حاليًا")
        text = (
            f"🔗 **الدفع عبر {method} (USDT)**\n\n"
            f"العنوان:\n`{address}`\n\n"
            "⚠️ تأكد من اختيار نفس الشبكة الموضحة تمامًا لتجنب فقدان الأموال.\n\n"
            "بعد إرسال التحويل، أرسل هنا هاش المعاملة (Transaction Hash) "
            "ليتم مراجعة عملية الشحن يدويًا."
        )
        await state.set_state(TopupFlow.waiting_order_ref)
        await state.update_data(method=method)
        await call.message.edit_text(text, reply_markup=back_to_main_kb(), parse_mode="Markdown")

    await call.answer()


@router.callback_query(F.data.startswith("check_pay_"))
async def on_check_payment_click(callback: CallbackQuery):
    # الحد الأدنى أو المبلغ المتوقع للفحص
    expected_amount = float(callback.data.split("check_pay_")[1])
    user_id = callback.from_user.id

    await callback.answer("⏳ جاري الفحص على البلوكشين...", show_alert=False)

    success, msg = await verify_user_payment(user_id, expected_amount)

    if success:
        await callback.message.edit_text(f"🎉 {msg}", reply_markup=back_to_main_kb(), parse_mode="Markdown")
    else:
        await callback.answer(msg, show_alert=True)


@router.message(TopupFlow.waiting_order_ref)
async def receive_topup_ref(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    method = data.get("method", "unknown")
    ref = message.text.strip() if message.text else ""

    if not ref:
        return await message.answer("الرجاء إرسال رقم الطلب أو هاش المعاملة كنص.")

    topup_id = await db.create_topup(message.from_user.id, method, ref)
    await state.clear()

    await message.answer(
        "✅ تم استلام طلب الشحن وهو الآن قيد المراجعة من الإدارة.\n"
        "سيتم إشعارك فور الموافقة وتحديث رصيدك.",
        reply_markup=back_to_main_kb(),
    )

    kb = InlineKeyboardBuilder()
    kb.button(text="✅ موافقة", callback_data=f"admtopup_approve:{topup_id}")
    kb.button(text="❌ رفض", callback_data=f"admtopup_reject:{topup_id}")
    kb.adjust(2)

    admin_text = (
        "🔔 طلب شحن رصيد جديد\n\n"
        f"👤 المستخدم: {message.from_user.id} (@{message.from_user.username})\n"
        f"💳 الطريقة: {method}\n"
        f"🧾 المرجع: {ref}\n\n"
        "بعد التحقق يدويًا من استلام التحويل الفعلي، اضغط موافقة لإدخال المبلغ."
    )

    for admin_id in settings.admin_ids:
        try:
            await bot.send_message(admin_id, admin_text, reply_markup=kb.as_markup())
        except Exception:
            pass
