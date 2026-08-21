from aiogram.fsm.state import State, StatesGroup


class BuyFlow(StatesGroup):
    waiting_custom_qty = State()


class TopupFlow(StatesGroup):
    waiting_order_ref = State()


class RedeemFlow(StatesGroup):
    waiting_code = State()
