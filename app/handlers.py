import logging
import asyncio

from aiogram import Bot, Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.database import db
from app.filters import ForwardFilter
from app.states import Prime, Target, Forward
from app.forward import forward_message_with_translation
from app.keyboards import create_inline_keyboard
from app.utils import lexer, languages, is_bot_admin

router = Router()
queue = asyncio.Queue()


async def message_processor(bot: Bot):
    while True:
        await asyncio.sleep(0.5)
        message, target, dest_lang = await queue.get()
        try:
            await forward_message_with_translation(bot, message, target, dest_lang)
        except Exception as e:
            logging.error(e)

        queue.task_done()


# region commands


@router.message(Command("start"))
async def start(message: types.Message):
    lang = await db.get_lang(message.from_user.id)
    await message.answer(lexer[lang]["start"])


@router.message(Command("stop"))
async def stop(message: types.Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    await state.clear()
    await message.answer(lexer[lang]["stop"])


@router.message(Command("help"))
async def help(message: types.Message):
    lang = await db.get_lang(message.from_user.id)
    await message.answer(lexer[lang]["help"])


@router.message(Command("about"))
async def about(message: types.Message):
    lang = await db.get_lang(message.from_user.id)
    await message.answer(lexer[lang]["about"])


@router.message(Command("select_language"))
async def select_language(message: types.Message):
    lang = await db.get_lang(message.from_user.id)
    await message.answer(
        lexer[lang]["select_language"],
        reply_markup=create_inline_keyboard(
            [languages[-4]] + languages[:5],
            prefix="change_lang",
        ),
    )


# endregion
# region prime


@router.message(Command("add_prime"))
async def add_prime_channel_1(message: types.Message, state: FSMContext):
    await state.set_state(Prime.link)
    lang = await db.get_lang(message.from_user.id)
    await message.answer(lexer[lang]["enter_link"])


@router.message(Prime.link)
async def add_prime_channel_2(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text)
    lang = await db.get_lang(message.from_user.id)
    link = (await state.get_data())["link"]

    try:
        if await is_bot_admin(message.bot, link):
            await db.add_prime(
                (await message.bot.get_chat(link)).id, link, message.from_user.id
            )

            await message.answer(lexer[lang]["registration_ended"])

            await state.clear()
        else:
            await message.answer(lexer[lang]["make_bot_admin"])

    except Exception as e:
        await message.answer(lexer[lang]["chat_not_found"])
        print(e)


@router.message(Command("show_primes"))
async def show_primes(message: types.Message):
    lang = await db.get_lang(message.from_user.id)
    data = await db.get_primes(message.from_user.id)

    if not data:
        await message.answer(lexer[lang]["no_primes"])
        return

    await message.answer(
        lexer[lang]["primes"],
        reply_markup=create_inline_keyboard(data, prefix="none"),
    )


@router.message(Command("remove_prime"))
async def remove_prime_1(message: types.Message):
    lang = await db.get_lang(message.from_user.id)
    data = await db.get_primes(message.from_user.id)

    if not data:
        await message.answer(lexer[lang]["no_primes"])
        return

    await message.answer(
        lexer[lang]["delete_prime"],
        reply_markup=create_inline_keyboard(data, prefix="delete_prime"),
    )


@router.callback_query(F.data.startswith("delete_prime:"))
async def remove_prime_2(callback: types.CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    prime_id = int(callback.data.split(":")[1])

    await db.del_prime(prime_id)

    data = await db.get_primes(callback.from_user.id)

    await callback.message.edit_text(
        callback.message.text,
        reply_markup=create_inline_keyboard(data, prefix="delete_prime"),
    )


# endregion
# region target


@router.message(Command("add_target"))
async def add_target_channel_1(message: types.Message, state: FSMContext):
    await state.set_state(Target.prime_id)
    lang = await db.get_lang(message.from_user.id)
    data = await db.get_primes(message.from_user.id)

    if not data:
        await message.answer(lexer[lang]["no_primes"])
        await state.clear()
        return

    await message.answer(
        lexer[lang]["select_prime"],
        reply_markup=create_inline_keyboard(data, prefix="select_prime"),
    )


@router.callback_query(Target.prime_id, F.data.startswith("select_prime:"))
async def add_target_channel_2(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(prime_id=int(callback.data.split(":")[1]))
    await state.set_state(Target.link)

    lang = await db.get_lang(callback.from_user.id)

    await callback.message.edit_text(lexer[lang]["prime_selected"], reply_markup=None)
    await callback.message.answer(lexer[lang]["enter_link"])


@router.message(Target.link)
async def add_target_channel_3(message: types.Message, state: FSMContext):
    lang = await db.get_lang(message.from_user.id)
    link = message.text

    try:
        if await is_bot_admin(message.bot, link):
            await state.update_data(link=link)
            await state.set_state(Target.lang)
            await message.answer(
                lexer[lang]["select_language"],
                reply_markup=create_inline_keyboard(
                    languages, prefix="select_language"
                ),
            )
        else:
            await message.answer(lexer[lang]["make_bot_admin"])

    except Exception as e:
        await message.answer(lexer[lang]["chat_not_found"])
        print(e)


@router.callback_query(Target.lang, F.data.startswith("select_language:"))
async def add_target_channel_4(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(lang=callback.data.split(":")[1])
    lang = await db.get_lang(callback.from_user.id)
    data = await state.get_data()

    link = data["link"]
    lng = data["lang"]
    prime_id = data["prime_id"]

    await db.add_target(
        (await callback.message.bot.get_chat(link)).id,
        link,
        lng,
        prime_id,
        callback.from_user.id,
    )

    await callback.message.edit_text(
        lexer[lang]["language_selected"], reply_markup=None
    )

    await callback.message.answer(lexer[lang]["registration_ended"])

    await state.clear()


@router.message(Command("show_targets"))
async def show_targets(message: types.Message):
    lang = await db.get_lang(message.from_user.id)
    data = await db.get_user_targets(message.from_user.id)

    if not data:
        await message.answer(lexer[lang]["no_targets"])
        return

    await message.answer(
        lexer[lang]["targets"],
        reply_markup=create_inline_keyboard(data, prefix="none"),
    )


@router.message(Command("remove_target"))
async def remove_target_1(message: types.Message):
    lang = await db.get_lang(message.from_user.id)
    data = await db.get_user_targets(message.from_user.id)

    if not data:
        await message.answer(lexer[lang]["no_targets"])
        return

    await message.answer(
        lexer[lang]["delete_target"],
        reply_markup=create_inline_keyboard(data, prefix="delete_target"),
    )


@router.callback_query(F.data.startswith("delete_target:"))
async def remove_target_2(callback: types.CallbackQuery):
    lang = await db.get_lang(callback.from_user.id)
    target_id = int(callback.data.split(":")[1])

    await db.del_target(target_id)

    data = await db.get_user_targets(callback.from_user.id)

    if len(data) == 0:
        await callback.message.edit_text(lexer[lang]["no_targets"])

    await callback.message.edit_text(
        callback.message.text,
        reply_markup=create_inline_keyboard(data, prefix="delete_target"),
    )


# endregion
# region callback
@router.callback_query(F.data.startswith("exit:"))
async def exit_from_keyboard(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await state.clear()


@router.callback_query(F.data.startswith("change_lang:"))
async def change_lang_callback_handler(callback: types.CallbackQuery):
    lang = callback.data.split(":")[1]
    await callback.message.edit_text(lexer[lang]["lang_changed"], reply_markup=None)

    await db.change_lang(callback.from_user.id, lang)
    await callback.answer(lexer[lang]["lang_changed"])


# endregion
# region posts
@router.channel_post()
async def handle_message(message: types.Message):
    if await db.in_prime(message.chat.id):
        for lang, target in await db.get_targets(message.chat.id):
            await forward_message_with_translation(
                message.bot, message, target, dest_lang=lang
            )
    elif await db.in_target(message.chat.id):
        pass
    else:
        await message.bot.leave_chat(message.chat.id)
        lang = await db.get_lang(await db.get_user_on_prime(message.chat.id))
        await message.bot.send_message(
            await db.get_user_id(message.chat.id), lexer[lang]["not_in_prime"]
        )


@router.message(ForwardFilter())
async def handle_forward(message: types.Message, state: FSMContext):
    if await db.in_prime(message.forward_from_chat.id):
        targets = await db.get_targets(message.forward_from_chat.id)
        for lang, target in targets:
            await queue.put((message, target, lang))


# endregion


# @router.error()
# async def error(event: types.ErrorEvent, message: types.Message):
#     print(str(event))
#     lang = await db.get_lang(message.from_user.id)
#     await message.answer(lexer[lang]["error"])
