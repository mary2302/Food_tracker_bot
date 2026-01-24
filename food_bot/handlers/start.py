from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

from memory import ensure_user

router = Router()


@router.message(Command("start"))
async def start(message: Message):
    ensure_user(message.from_user.id)
    await message.answer(
        "👋 Привет! Я бот для воды/калорий/тренировок.\n\n"
        "📝 Команды:\n"
        "/help - доступные команды\n"
        "/set_profile — настроить профиль\n"
        "/profile - посмотреть профиль\n"
        "/log_water <мл>\n"
        "/log_food <продукт>\n"
        "/log_workout <тип> <мин>\n"
        "/check_progress — прогресс\n"
        "/recommend_food <продукт> — рекомендации по питанию\n"
        "/graph_water — статистика выпитой воды по дням\n"
        "/graph_calories — статистика учета калорий по дням\n"
        "/reset_today — обнулить дневные логи"
    )
