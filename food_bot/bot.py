import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN
from handlers import setup_routers
from middlewares import LoggingMiddleware
from commands import setup_bot_commands


async def main():
    bot = Bot(token=BOT_TOKEN)
    await setup_bot_commands(bot)

    dp = Dispatcher()
    dp.message.middleware(LoggingMiddleware())
    setup_routers(dp)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())