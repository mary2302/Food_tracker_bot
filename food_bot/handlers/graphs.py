from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile

from memory import ensure_user
from services.plots import last_n_days, plot_water, plot_calories

router = Router()


@router.message(Command("graph_water"))
async def graph_water(message: Message):
    user = ensure_user(message.from_user.id)
    days_dict = user.get("days", {})

    if not days_dict:
        return await message.answer("Пока нет данных для графика. Начните логировать воду 🙂")

    days = last_n_days(n=14)
    water_ml = [days_dict.get(d, {}).get("water", 0) for d in days]

    img_bytes = plot_water(days, water_ml)
    await message.answer_photo(BufferedInputFile(img_bytes, filename="water.png"))


@router.message(Command("graph_calories"))
async def graph_calories(message: Message):
    user = ensure_user(message.from_user.id)
    days_dict = user.get("days", {})

    if not days_dict:
        return await message.answer("Пока нет данных для графика. Начните логировать еду/тренировки 🙂")

    days = last_n_days(n=14)
    eaten = [days_dict.get(d, {}).get("eaten", 0) for d in days]
    burned = [days_dict.get(d, {}).get("burned", 0) for d in days]
    balance = [e - b for e, b in zip(eaten, burned)]

    img_bytes = plot_calories(days, eaten, burned, balance)
    await message.answer_photo(BufferedInputFile(img_bytes, filename="calories.png"))
