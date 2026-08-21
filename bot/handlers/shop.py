from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot import database as db
from bot import texts
from bot.states import BuyFlow
from bot.keyboards import (
    categories_kb,
    products_kb,
    product_detail_kb,
    quantity_kb,
    order_confirm_kb,
    insufficient_balance_kb,
    back_to_main_kb,
)

router = Router()


@router.callback_query(F.data == "menu:products")
async def show_categories(call: CallbackQuery):
    categories = await db.list_categories()
    if not categories:
        await call.message.edit_text("لا توجد فئات منتجات حاليًا.", reply_markup=back_to_main_kb())
        return await call.answer()
    await call.message.edit_text(texts.CHOOSE_CATEGORY, reply_markup=categories_kb(categories))
    await call.answer()


@router.callback_query(F.data.startswith("cat:"))
async def show_products(call: CallbackQuery):
    category_id = int(call.data.split(":")[1])
    products = await db.list_products(category_id)
    if not products:
        await call.message.edit_text("لا توجد منتجات بهذه الفئة حاليًا.", reply_markup=back_to_main_kb())
        return await call.answer()
    await call.message.edit_text(
        texts.CHOOSE_SERVICE, reply_markup=products_kb(products, category_id)
    )
    await call.answer()


@router.callback_query(F.data.startswith("prod:"))
async def show_product_detail(call: CallbackQuery):
    product_id = int(call.data.split(":")[1])
    p = await db.get_product(product_id)
    if not p:
        return await call.answer("المنتج غير متوفر", show_alert=True)
    text = (
        f"📦 {p['name']}\n\n"
        f"{p['description'] or ''}\n\n"
        f"💵 السعر: {p['price']:.2f} USD / وحدة\n"
        f"📊 المتوفر: {p['stock']}\n"
    )
    await call.message.edit_text(text, reply_markup=product_detail_kb(product_id))
    await call.answer()


@router.callback_query(F.data.startswith("buy:"))
async def choose_quantity(call: CallbackQuery):
    product_id = int(call.data.split(":")[1])
    await call.message.edit_text(
        "كم وحدة تريد؟", reply_markup=quantity_kb(product_id)
    )
    await call.answer()


@router.callback_query(F.data.startswith("qtycustom:"))
async def ask_custom_qty(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.split(":")[1])
    await state.set_state(BuyFlow.waiting_custom_qty)
    await state.update_data(product_id=product_id)
    await call.message.edit_text(texts.CUSTOM_QTY_PROMPT, reply_markup=back_to_main_kb())
    await call.answer()


@router.message(BuyFlow.waiting_custom_qty)
async def receive_custom_qty(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        return await message.answer(texts.CUSTOM_QTY_INVALID)
    qty = int(message.text.strip())
    if qty <= 0:
        return await message.answer(texts.CUSTOM_QTY_INVALID)
    data = await state.get_data()
    product_id = data["product_id"]
    await state.clear()
    await create_order_flow(message.from_user.id, product_id, qty, message)


@router.callback_query(F.data.startswith("qty:"))
async def pick_quantity(call: CallbackQuery):
    _, product_id, qty = call.data.split(":")
    await create_order_flow(call.from_user.id, int(product_id), int(qty), call.message, call)


async def create_order_flow(user_id: int, product_id: int, qty: int, message: Message, call: CallbackQuery = None):
    p = await db.get_product(product_id)
    if not p or p["stock"] < qty:
        text = "❌ الكمية المطلوبة غير متوفرة حاليًا."
        if call:
            await call.message.edit_text(text, reply_markup=back_to_main_kb())
            return await call.answer()
        return await message.answer(text, reply_markup=back_to_main_kb())

    order_id = await db.create_order(user_id, product_id, qty, p["price"])
    total = p["price"] * qty
    text = texts.ORDER_SUMMARY.format(name=p["name"], qty=qty, unit_price=p["price"], total=total)

    if call:
        await call.message.edit_text(text, reply_markup=order_confirm_kb(order_id))
        await call.answer()
    else:
        await message.answer(text, reply_markup=order_confirm_kb(order_id))


@router.callback_query(F.data.startswith("cancelorder:"))
async def cancel_order(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])
    await db.set_order_status(order_id, "cancelled")
    await call.message.edit_text(texts.ORDER_CANCELLED, reply_markup=back_to_main_kb())
    await call.answer()


@router.callback_query(F.data.startswith("confirm:"))
async def confirm_order(call: CallbackQuery):
    order_id = int(call.data.split(":")[1])
    order = await db.get_order(order_id)
    if not order or order["status"] != "pending":
        return await call.answer("هذا الطلب لم يعد صالحًا.", show_alert=True)

    user_id = order["user_id"]
    balance = await db.get_balance(user_id)
    total = order["total_price"]

    if balance < total:
        text = texts.INSUFFICIENT_BALANCE.format(price=total, balance=balance)
        await call.message.edit_text(text, reply_markup=insufficient_balance_kb())
        return await call.answer()

    product = await db.get_product(order["product_id"])
    if not product or product["stock"] < order["quantity"]:
        await call.message.edit_text("❌ نفدت الكمية قبل إتمام الطلب.", reply_markup=back_to_main_kb())
        return await call.answer()

    # خصم الرصيد وتحديث المخزون وحالة الطلب
    await db.adjust_balance(user_id, -total)
    await db.decrement_stock(order["product_id"], order["quantity"])
    await db.set_order_status(order_id, "completed")

    delivery = product["delivery_content"] or "سيتم تسليم طلبك يدويًا من قبل الدعم قريبًا."
    text = texts.ORDER_SUCCESS.format(name=product["name"], qty=order["quantity"], delivery=delivery)
    await call.message.edit_text(text, reply_markup=back_to_main_kb())
    await call.answer("تم الشراء بنجاح ✅")
