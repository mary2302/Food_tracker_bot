from typing import Dict

from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router

from services.calories import search_food_kcal_per_100g
from states import FoodForm, PendingFood
from memory import ensure_user, ensure_day, today_key

from models.food_model import FoodQuery, FoodProduct, FoodIntakeInput, FoodEntry


router = Router()

pending_food: Dict[int, PendingFood] = {}


@router.message(Command("log_food"))
async def log_food(message: Message, state: FSMContext):
    user = ensure_user(message.from_user.id)
    if not user.get("calorie_goal"):
        return await message.answer("Сначала настройте профиль: /set_profile")

    try:
        fq = FoodQuery.parse_from_command(message.text)
    except ValueError as e:
        return await message.answer(str(e))

    found = await search_food_kcal_per_100g(fq.query)
    if not found:
        return await message.answer("Не могу определить калорийность этого продукта 😿. Попробуйте другое название.")

    name, kcal100 = found
    product = FoodProduct.validate(name=name, kcal_per_100g=kcal100)
    pending_food[message.from_user.id] = PendingFood(
        name=product.name,
        kcal_per_100g=product.kcal_per_100g
    )

    await state.set_state(FoodForm.grams)
    await message.answer(f"🍽 {name} — {kcal100:.0f} ккал на 100 г.\nСколько грамм вы съели?")


@router.message(FoodForm.grams)
async def log_food_grams(message: Message, state: FSMContext):
    user = ensure_user(message.from_user.id)
    pf = pending_food.get(message.from_user.id)
    if not pf:
        await state.clear()
        return await message.answer("Что-то пошло не так. Повторите /log_food <продукт>.")

    try:
        intake = FoodIntakeInput.parse_grams(message.text)
    except ValueError as e:
        return await message.answer(str(e))

    product = FoodProduct.validate(name=pf.name, kcal_per_100g=pf.kcal_per_100g)
    entry = FoodEntry.from_product_and_input(product, intake)

    # ✅ Новый учёт по дням (для графиков)
    day = ensure_day(user, today_key())
    day["eaten"] += entry.kcal

    # ✅ Для совместимости: если /check_progress пока читает logged_calories
    user["logged_calories"] = day["eaten"]

    # ✅ Завершаем FSM и чистим pending
    pending_food.pop(message.from_user.id, None)
    await state.clear()

    await message.answer(f"✅ Записано: {entry.grams:.0f} г = {entry.kcal} ккал.")
