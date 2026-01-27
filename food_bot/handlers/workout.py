from aiogram.filters import Command
from aiogram.types import Message
from aiogram import Router

from memory import ensure_user, ensure_day, today_key
from utils import estimate_workout_kcal

from models.workout import WorkoutInput, WorkoutEntry


router = Router()


@router.message(Command("log_workout"))
async def log_workout(message: Message):
    """
    ## /log_workout

    Логирует тренировку пользователя: считает сожжённые калории и обновляет дневные итоги.

    ### Формат команды
    `/log_workout <тип> <минуты>`

    Пример: `/log_workout бег 45`

    ### Что делает обработчик
    1. Получает пользователя через `ensure_user`.
    2. Проверяет, что профиль настроен (есть `calorie_goal`), иначе просит `/set_profile`.
    3. Парсит и валидирует команду через `WorkoutInput.parse_from_command`.
    4. Оценивает расход калорий `estimate_workout_kcal(...)` (учитывает тип, минуты и вес, если он задан).
    5. Создаёт запись тренировки `WorkoutEntry.from_input(...)`, где дополнительно считается вода:
       `extra_water_ml = (minutes // 30) * 200`.
    6. Обновляет дневной лог:
       - `day["burned"] += entry.burned_kcal`
       - синхронизирует быстрые счётчики `user["burned_calories"]` и `user["burned_water"]`
    7. Отправляет пользователю сообщение с результатом и советом по воде (если есть добавка).

    ### Используемые поля пользователя
    - `user["weight"]` — вес (может быть `None`).
    - `user["calorie_goal"]` — признак, что профиль настроен.
    - `user["burned_calories"]` — накопленные сожжённые ккал за сегодня.
    - `user["burned_water"]` — накопленная добавка воды за сегодня (мл).

    ### Ответ пользователю
    Пример:
    `🏋️ Бег 45 мин — ~320 ккал.
     Дополнительно: выпейте 200 мл воды.`

    ### Ошибки/валидация
    - Если формат команды неверный — возвращает текст ошибки из `ValueError`.
    - Если профиль не настроен — просит пользователя сначала выполнить `/set_profile`.
    """
    user = ensure_user(message.from_user.id)
    if not user.get("calorie_goal"):
        return await message.answer("Сначала настройте профиль: /set_profile")

    try:
        inp = WorkoutInput.parse_from_command(message.text)
    except ValueError as e:
        return await message.answer(str(e))

    burned = estimate_workout_kcal(inp.workout_type, inp.minutes, user.get("weight"))
    entry = WorkoutEntry.from_input(inp, burned)

    day = ensure_day(user, today_key())
    day["burned"] += entry.burned_kcal

    user["burned_calories"] = day["burned"]
    user["burned_water"] += entry.extra_water_ml

    tip = f"\nДополнительно: выпейте {entry.extra_water_ml} мл воды." if entry.extra_water_ml > 0 else ""
    await message.answer(
        f"🏋️ {entry.workout_type.capitalize()} {entry.minutes} мин — ~{entry.burned_kcal} ккал.{tip}"
    )
