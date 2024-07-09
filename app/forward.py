import asyncio
import re
import mtranslate

from aiogram import types, Bot
from aiogram.enums import ParseMode
from aiogram.types import (
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaDocument,
    ContentType as ct,
)

CONSTANT = 10
media_groups = {}
media_group_timers = {}


async def translate_text(text: str, dest="en"):
    i = 0
    code = []

    # Шаг 1: Найти и выделить секции кода в тегах <code>
    while True:
        code_match = re.findall(r"\<code[^\>]*\>([^\<]+)\<\/code\>", text)

        if not code_match:
            break

        code.append(code_match[0])
        text = re.sub(
            r"\<code[^\>]*\>([^\<]+)\<\/code\>",
            f"845687638756987236875687468736875{i}",
            text,
            1,
        )
        i += 1

    # Шаг 2: Перевести текст без секций кода
    translated = mtranslate.translate(text, dest)

    # Шаг 3: Восстановить секции кода в переведенном тексте
    for i, j in enumerate(code):
        translated = translated.replace(
            f"845687638756987236875687468736875{i}", f"<code>{j}</code>"
        )

    return translated


async def send_media_group(bot: Bot, media_group_id, target):
    if media_group_id in media_groups:
        media_group = sorted(media_groups[media_group_id], key=lambda x: x["order"])
        media = [item["media"] for item in media_group]

        del media_groups[media_group_id]
        del media_group_timers[media_group_id]

        return [
            i.message_id
            for i in (await bot.send_media_group(chat_id=target, media=media))
        ]


async def forward_message_with_translation(
    bot: Bot,
    message: types.Message,
    target: str | int,
    dest_lang: str = "en",
) -> list:
    if message.content_type == ct.TEXT:
        translated_text = await translate_text(message.html_text, dest_lang)
        await asyncio.sleep(CONSTANT)
        return [
            (
                await bot.send_message(
                    target, translated_text, parse_mode=ParseMode.HTML
                )
            ).message_id
        ]

    elif message.content_type in [ct.PHOTO, ct.VIDEO, ct.DOCUMENT]:
        media_group_id = message.media_group_id
        media_group_id = (target, media_group_id)

        caption = message.caption or ""
        translated_caption = (
            await translate_text(message.html_text, dest_lang) if caption else ""
        )

        if media_group_id[1]:
            if media_group_id not in media_groups:
                media_groups[media_group_id] = []

            if message.photo:
                media_groups[media_group_id].append(
                    {
                        "media": InputMediaPhoto(
                            media=message.photo[-1].file_id,
                            caption=translated_caption,
                            parse_mode=ParseMode.HTML if caption else None,
                        ),
                        "order": message.message_id,
                    }
                )

            elif message.video:
                media_groups[media_group_id].append(
                    {
                        "media": InputMediaVideo(
                            media=message.video.file_id,
                            caption=translated_caption,
                            parse_mode=ParseMode.HTML if caption else None,
                        ),
                        "order": message.message_id,
                    }
                )

            elif message.document:
                media_groups[media_group_id].append(
                    {
                        "media": InputMediaDocument(
                            media=message.document.file_id,
                            caption=translated_caption,
                            parse_mode=ParseMode.HTML if caption else None,
                        ),
                        "order": message.message_id,
                    }
                )

            # Устанавливаем таймер для отправки медиа-группы через 1 секунду после последнего сообщения
            if media_group_id in media_group_timers:
                media_group_timers[media_group_id].cancel()
            media_group_timers[media_group_id] = asyncio.get_event_loop().call_later(
                CONSTANT,
                lambda: asyncio.create_task(
                    send_media_group(bot, media_group_id, target)
                ),
            )
            return []

        else:
            if message.photo:
                await asyncio.sleep(CONSTANT)
                return [
                    (
                        await bot.send_photo(
                            chat_id=target,
                            photo=message.photo[-1].file_id,
                            caption=translated_caption if caption else None,
                            parse_mode=ParseMode.HTML if caption else None,
                        )
                    ).message_id
                ]
            elif message.video:
                await asyncio.sleep(CONSTANT)
                return [
                    (
                        await bot.send_video(
                            chat_id=target,
                            video=message.video.file_id,
                            caption=translated_caption if caption else None,
                            parse_mode=ParseMode.HTML if caption else None,
                        )
                    ).message_id
                ]
            elif message.document:
                await asyncio.sleep(CONSTANT)
                return [
                    (
                        await bot.send_document(
                            chat_id=target,
                            document=message.document.file_id,
                            caption=translated_caption if caption else None,
                            parse_mode=ParseMode.HTML if caption else None,
                        )
                    ).message_id
                ]

    else:
        await asyncio.sleep(CONSTANT)
        return [
            (
                await bot.copy_message(
                    chat_id=target,
                    from_chat_id=message.chat.id,
                    message_id=message.message_id,
                )
            ).message_id
        ]


# print(
#     asyncio.run(
#         translate_text(
print(
    len(
        '<b>simplify python</b> #2\n\nСледующая тема: <b>функции</b>. В python вы будете использовать их очень часто, сейчас я вам расскажу о некоторых деталях для аргументов. Например у вас такая ситуация, что вы хотите добавить необязательный аргумент для функции, например у вас есть функция для перевода чисел в разные системы исчисления. Необязательным аргументом тут будет то, заглавными ли будут буквы на выходе, вот как это выглядит:\n\n<pre><code class="language-py">def convert_to(number, base, upper=False):\n    digits = \'0123456789abcdefghijklmnopqrstuvwxyz\'\n    if base &gt; len(digits): return None\n    result = \'\'\n    while number &gt; 0:\n        result = digits[number % base] + result\n        number //= base\n    return result.upper() if upper else result\n</code></pre>Аргумент upper отвечает за то, будет ли строка выведена с заглавными буквами, по умолчанию буквы маленькие. Тоесть при вызове кода:\n\n<pre><code class="language-py">print(conver_to(15, 16)) # -&gt; f\nprint(conver_to(15, 16, upper=True)) # -&gt; F\n</code></pre>Также все аргументы функции можно обобщить с помощью записи *args, тоесть функция сможет принимать неограниченное количество аргументов, например вот функция для нахождения наибольшего аргумента:\n\n<pre><code class="language-py">def Max(*args):\n    lst = [*args]\n    m = lst[0]\n    for i in lst:\n        if i &gt; m:\n            m = i\n    return m\n</code></pre>Этот код будет работать как при Max(1, 2) так и при Max(4, -10, 0, 16). В целом по функциям все.'
    )
)  # ,
#             "ja",
#         )
#     )
# )
