from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

from memory import ensure_user, ensure_day, today_key

router = Router()


@router.message(Command("log_water"))
async def log_water(message: Message):
    user = ensure_user(message.from_user.id)
    if not user.get("water_goal"):
        return await message.answer("Сначала настройте профиль: /set_profile")

    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return await message.answer("Формат: /log_water <мл>  (например /log_water 250)")

    try:
        ml = int(parts[1])
        if ml <= 0 or ml > 5000:
            raise ValueError
    except Exception:
        return await message.answer("Введите количество мл числом, например /log_water 250")

    # ✅ Новый учёт по дням (для графиков)
    day = ensure_day(user, today_key())
    day["water"] += ml

    # ✅ Для совместимости: если ты ещё используешь logged_water в /check_progress
    user["logged_water"] = day["water"]

    left = max(0, user["water_goal"] - day["water"] + user["burned_water"])
    await message.answer(f"💧 Записано: {ml} мл.\nОсталось до нормы: {left} мл.")
