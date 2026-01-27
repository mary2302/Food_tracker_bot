from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

from memory import ensure_user, ensure_day, today_key

router = Router()


@router.message(Command("check_progress"))
async def check_progress(message: Message):
    """
    Выводим прогресс пользователя за день
    - сколько воды выпито и осталось
    - сколько ккал потреблено и осталось
    - результаты тренировок
    """
    user = ensure_user(message.from_user.id)
    if not user.get("calorie_goal") or not user.get("water_goal"):
        return await message.answer("Сначала настройте профиль: /set_profile")

    water_goal = user["water_goal"]
    w_drunk = user["logged_water"]
    w_burned = user["burned_water"]
    w_left = max(0, water_goal - w_drunk + w_burned)

    cal_goal = user["calorie_goal"]
    eaten = user["logged_calories"]
    burned = user["burned_calories"]
    balance = eaten - burned
    cal_left = cal_goal - balance

    await message.answer(
        "📊 Прогресс:\n\n"
        "Вода:\n"
        f"- Выпито: {w_drunk} мл из {water_goal + w_burned} мл.\n"
        f"- Осталось: {w_left} мл.\n\n"
        "Калории:\n"
        f"- Потреблено: {eaten} ккал.\n"
        f"- Сожжено: {burned} ккал.\n"
        f"- Осталось: {cal_left} ккал."
    )


@router.message(Command("reset_today"))
async def reset_today(message: Message):
    #Удаление всех данных за текущий день
    user = ensure_user(message.from_user.id)
    user["logged_water"] = 0
    user["logged_calories"] = 0
    user["burned_calories"] = 0
    user["burned_water"] = 0

    day = ensure_day(user, today_key())
    day["water"] = 0
    day["eaten"] = 0
    day["burned"] = 0
    await message.answer("♻️ Дневные логи сброшены: вода/еда/тренировки = 0.")
