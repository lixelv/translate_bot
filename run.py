import logging
import asyncio
import tracemalloc

from aiogram import Bot, Dispatcher

from config import environment
from app.handlers import router, message_processor
from app.middleware import UserCheckMiddleware, ThrottleMiddleware, message_processor_2
from app.database import db

tracemalloc.start()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Инициализируем бота и диспетчер
bot = Bot(token=environment["TELEGRAM"])
dp = Dispatcher()

queue = asyncio.Queue()

router.message.middleware(UserCheckMiddleware(db, logging))
router.message.middleware(ThrottleMiddleware(0.05, queue))

dp.include_router(router)


async def main():
    asyncio.create_task(message_processor(bot))
    asyncio.create_task(message_processor_2(bot, queue, 0.1))
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
