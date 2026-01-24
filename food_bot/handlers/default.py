from aiogram import Router
from aiogram.types import Message

router = Router()

@router.message()
async def default(message: Message):
    await message.answer(
        "Не знаю такую команду 🐣\n"
        "Используй /help или введи команду из меню."
    )
