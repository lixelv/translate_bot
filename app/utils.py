import json

from aiogram import Bot
from aiogram.enums import ChatMemberStatus


async def is_bot_admin(bot: Bot, chat_id: int) -> bool:
    try:
        chat_administrators = await bot.get_chat_administrators(chat_id)
        for admin in chat_administrators:
            if admin.user.id == bot.id and admin.status in [
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.CREATOR,
            ]:
                return True

    except Exception as e:
        if "chat not found" in str(e):
            raise ValueError(f"Chat {chat_id} not found")

    return False


class Lexicon:
    def __init__(self):
        with open("lexicon.json", "r", encoding="utf-8") as f:
            self.lexicon = json.load(f)

    def __getitem__(self, lang):
        return self.lexicon.get(lang) or self.lexicon.get("en")


lexer = Lexicon()

languages = [
    ("🇷🇺", "ru"),
    ("🇬🇧", "en"),
    ("🇩🇪", "de"),
    ("🇫🇷", "fr"),
    ("🇯🇵", "ja"),
    ("🇨🇳", "zh"),
    ("🇪🇸", "es"),
    ("🇮🇹", "it"),
    ("🇵🇱", "pl"),
    ("🇹🇷", "tr"),
    ("🇰🇷", "ko"),
    ("🇨🇿", "cs"),
    ("🇸🇪", "sv"),
    ("🇳🇱", "nl"),
    ("🇵🇹", "pt"),
    ("🇧🇬", "bg"),
    ("🇭🇺", "hu"),
    ("🇬🇷", "el"),
    ("🇷🇴", "ro"),
    ("🇸🇰", "sk"),
    ("🇸🇮", "sl"),
    ("🇱🇻", "lv"),
    ("🇱🇹", "lt"),
    ("🇩🇰", "da"),
    ("🇳🇴", "nb"),
    ("🇫🇮", "fi"),
    ("🇪🇪", "et"),
    ("🇺🇦", "uk"),
    ("🇸🇦", "ar"),
    ("🇮🇩", "id"),
]
