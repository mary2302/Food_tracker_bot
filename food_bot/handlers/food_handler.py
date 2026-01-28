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
    """
    ## /log_food

    Запускает добавление еды в дневник в 2 шага:
    1) пользователь вводит продукт, бот находит ккал/100г  
    2) бот спрашивает граммы и записывает итоговые ккал за день

    ### Формат команды
    `/log_food <название продукта>`

    Пример: `/log_food йогурт`

    ### Что делает обработчик
    1. Получает пользователя через `ensure_user`.
    2. Проверяет, что профиль настроен (есть `calorie_goal`), иначе просит `/set_profile`.
    3. Парсит команду в `FoodQuery` через `FoodQuery.parse_from_command(...)`.
       - Если формат неверный — отвечает текстом ошибки.
    4. Ищет калорийность продукта `search_food_kcal_per_100g(fq.query)`.
       Ожидаемый результат: `(name: str, kcal100: float)` или `None`.
    5. Валидирует результат через `FoodProduct.validate(...)`.
    6. Сохраняет найденный продукт во временное хранилище `pending_food[user_id]`,
       чтобы на следующем шаге (граммы) знать, какой продукт выбран.
    7. Переводит FSM в состояние `FoodForm.grams` и задаёт вопрос о граммах.

    ### Используемые структуры
    - `pending_food[user_id] = PendingFood(name, kcal_per_100g)` — временно хранит продукт между шагами.
    - FSM состояние: `FoodForm.grams` — ожидание ввода граммов.

    ### Ответ пользователю
    Пример:
    `🍽 Йогурт — 60 ккал на 100 г.
     Сколько грамм вы съели?`

    ### Ошибки
    - Если профиль не настроен → `/set_profile`
    - Если продукт не найден → просит попробовать другое название
    - Если формат команды неверный → возвращает сообщение из `ValueError`
    """
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
    """
    ## log_food_grams (шаг 2 FSM)

    Обрабатывает ввод граммов после команды `/log_food` и записывает калории в дневной лог.

    ### Когда вызывается
    Этот хендлер срабатывает **только** когда FSM находится в состоянии `FoodForm.grams`
    (то есть после успешного выполнения `/log_food ...`).

    ### Что делает обработчик
    1. Получает пользователя через `ensure_user`.
    2. Достаёт временно сохранённый продукт из `pending_food[user_id]`.
       - Если его нет (состояние рассинхронизировалось) — очищает FSM и просит повторить `/log_food`.
    3. Парсит граммы через `FoodIntakeInput.parse_grams(message.text)`.
       - Поддерживает ввод с запятой/точкой.
       - Валидирует диапазон.
    4. Собирает `FoodProduct` из данных `PendingFood` и создаёт запись:
       `entry = FoodEntry.from_product_and_input(product, intake)`.
    5. Обновляет дневной лог:
       - `day["eaten"] += entry.kcal`
       - синхронизирует быстрый счётчик `user["logged_calories"]`
    6. Очищает временные данные:
       - удаляет `pending_food[user_id]`
       - сбрасывает состояние FSM (`state.clear()`).
    7. Отправляет подтверждение пользователю.

    ### Используемые поля
    - `user["days"][today]["eaten"]` — дневная сумма съеденных ккал.
    - `user["logged_calories"]` — быстрый счётчик “съедено сегодня”.
    - `pending_food[user_id]` — временный продукт между шагами.

    ### Ответ пользователю
    Пример:
    `✅ Записано: 150 г = 90 ккал.`

    ### Ошибки/валидация
    - Нет `pending_food` → очищаем FSM и просим повторить `/log_food`.
    - Некорректные граммы → возвращаем сообщение из `ValueError`.
    """
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

    user["logged_calories"] += entry.kcal

    day = ensure_day(user, today_key())
    day["eaten"] = user["logged_calories"]

    pending_food.pop(message.from_user.id, None)
    await state.clear()

    await message.answer(f"✅ Записано: {entry.grams:.0f} г = {entry.kcal} ккал.")
