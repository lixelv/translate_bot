from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_inline_keyboard(button_tuples, prefix, width=3):
    builder = InlineKeyboardBuilder()

    for button, callback_data in button_tuples:
        builder.button(text=str(button), callback_data=f"{prefix}:{callback_data}")

    builder.row()
    builder.button(text="X", callback_data="exit:")

    return builder.adjust(width).as_markup()
