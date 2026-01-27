from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from services.calories import search_food_candidates

router = Router()


@router.message(Command("recommend_food"))
async def recommend_food(message: Message):
    #Собираем топ-5 продуктов с низкой калорийностью по запросу пользователя
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer(
            "Формат: /recommend_food <что ищем>\n"
            "Пример: /recommend_food йогурт"
        )

    query = parts[1].strip()
    if len(query) < 2:
        return await message.answer("Запрос слишком короткий. Пример: /recommend_food йогурт")

    items = await search_food_candidates(query, limit=5)
    if not items:
        return await message.answer("Не нашёл подходящих вариантов 😕 Попробуйте другой запрос.")

    lines = ["🥗 Варианты с низкой калорийностью (ккал/100г):"]
    for name, kcal in items:
        lines.append(f"- {name} — {kcal:.0f}")

    await message.answer("\n".join(lines))
