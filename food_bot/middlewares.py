import logging
from aiogram import BaseMiddleware
from aiogram.types import Message

logger = logging.getLogger("user_messages")

class LoggingMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message) and event.text:
            logger.info("Получено сообщение от %s: %s", event.from_user.id, event.text)
        return await handler(event, data)
