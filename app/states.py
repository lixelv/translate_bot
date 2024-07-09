from aiogram.fsm.state import State, StatesGroup


class Prime(StatesGroup):
    link = State()


class Target(StatesGroup):
    prime_id = State()
    link = State()
    lang = State()


class Forward(StatesGroup):
    time = State()
