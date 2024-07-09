import asyncio

from aiogram import BaseMiddleware, Bot
from aiogram.enums import ChatType
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable

from app.database import AsyncDB


class ThrottleMiddleware(BaseMiddleware):
    def __init__(self, delay: float, queue: asyncio.Queue):
        self.delay = delay
        self.queue = queue
        super().__init__()

    async def __call__(self, handler, event: Message, data: dict):
        await self.queue.put((handler, event, data))


async def message_processor_2(bot: Bot, queue: asyncio.Queue, delay: float):
    while True:
        await asyncio.sleep(delay)
        handler, event, data = await queue.get()
        await handler(event, data)
        queue.task_done()


class UserCheckMiddleware(BaseMiddleware):
    def __init__(self, db: AsyncDB, logging):
        super().__init__()
        self.db = db
        self.logging = logging

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if event.chat.type != ChatType.PRIVATE:
            return await handler(event, data)

        self.logging.info(f"Message from user {event.from_user.id}")

        if not await self.db.user_exists(event.from_user.id):
            await self.db.add_user(
                event.from_user.id,
                event.from_user.username,
                event.from_user.language_code,
                event.date,
            )
            self.logging.info(f"User {event.from_user.id} added")

        result = await handler(event, data)

        self.logging.info(f"Message from user {event.from_user.id} processed")

        return result
