from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

from memory import ensure_user, ensure_day, today_key
from utils import estimate_workout_kcal

from models.workout import WorkoutInput, WorkoutEntry


router = Router()


@router.message(Command("log_workout"))
async def log_workout(message: Message):
    user = ensure_user(message.from_user.id)
    if not user.get("calorie_goal"):
        return await message.answer("Сначала настройте профиль: /set_profile")

    try:
        inp = WorkoutInput.parse_from_command(message.text)
    except ValueError as e:
        return await message.answer(str(e))

    burned = estimate_workout_kcal(inp.workout_type, inp.minutes, user.get("weight"))
    entry = WorkoutEntry.from_input(inp, burned)

    # ✅ Новый учёт по дням (для графиков)
    day = ensure_day(user, today_key())
    day["burned"] += entry.burned_kcal

    # ✅ Для совместимости: если /check_progress пока читает burned_calories
    user["burned_calories"] = day["burned"]
    user["burned_water"] += entry.extra_water_ml

    tip = f"\nДополнительно: выпейте {entry.extra_water_ml} мл воды." if entry.extra_water_ml > 0 else ""
    await message.answer(
        f"🏋️ {entry.workout_type.capitalize()} {entry.minutes} мин — ~{entry.burned_kcal} ккал.{tip}"
    )
