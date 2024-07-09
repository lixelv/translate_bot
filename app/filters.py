from aiogram.filters import BaseFilter
from aiogram.types import Message


class ForwardFilter(BaseFilter):
    async def __call__(self, message: Message):
        return bool(message.forward_from or message.forward_from_chat)
