from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router
from aiogram.utils.text_decorations import html_decoration as hd

from services.weather import get_city_temp_c
from memory import ensure_user
from states import ProfileForm
from utils import calc_water_goal_ml, calc_calorie_goal



router = Router()


@router.message(Command("set_profile"))
async def set_profile(message: Message, state: FSMContext):
    ensure_user(message.from_user.id)
    await state.clear()
    await state.set_state(ProfileForm.weight)
    await message.answer("Введите ваш вес (в кг), например 80:")

@router.message(Command("profile"))
async def cmd_profile(message: Message):
    user = ensure_user(message.from_user.id)

    # Если профиль ещё не заполнен
    required = ("weight", "height", "age", "sex", "activity", "city", "water_goal", "calorie_goal")
    if not all(user.get(k) is not None for k in required):
        return await message.answer(
            "Профиль ещё не настроен.\n"
            "Заполни его командой /set_profile"
        )

    sex = "жен" if user.get("sex") == "f" else "муж"

    # Текущие прогрессы (если они есть)
    logged_water = user.get("logged_water", 0)
    logged_calories = user.get("logged_calories", 0)
    burned_calories = user.get("burned_calories", 0)

    net_calories = logged_calories - burned_calories
    water_left = max(0, int(user["water_goal"] - logged_water))
    cal_left = int(user["calorie_goal"] - net_calories)

    city = hd.quote(str(user["city"]))
    sex_safe = hd.quote(str(sex))

    text = (
        "👤 <b>Твой профиль:</b>\n"
        f"• Вес: <b>{user['weight']}</b> кг\n"
        f"• Рост: <b>{user['height']}</b> см\n"
        f"• Возраст: <b>{user['age']}</b>\n"
        f"• Пол: <b>{sex_safe}</b>\n"
        f"• Активность: <b>{user['activity']}</b> мин/день\n"
        f"• Город: <b>{city}</b>\n\n"
        "🎯 <b>Цели:</b>\n"
        f"• Вода: <b>{user['water_goal']}</b> мл/день\n"
        f"• Калории: <b>{user['calorie_goal']}</b> ккал/день\n\n"
        "📊 <b>Сегодня:</b>\n"
        f"• Выпито воды: <b>{logged_water}</b> мл (осталось <b>{water_left}</b> мл)\n"
        f"• Съедено: <b>{logged_calories}</b> ккал\n"
        f"• Сожжено тренировками: <b>{burned_calories}</b> ккал\n"
        f"• Баланс: <b>{net_calories}</b> ккал (осталось <b>{cal_left}</b> ккал)\n\n"
        "⚙️ Обновить профиль: /set_profile"
    )

    await message.answer(text, parse_mode="HTML")


@router.message(ProfileForm.weight)
async def profile_weight(message: Message, state: FSMContext):
    try:
        w = float(message.text.replace(",", "."))
        if w <= 0 or w > 400:
            raise ValueError
    except Exception:
        return await message.answer("Не понял вес. Введите число, например 80:")

    await state.update_data(weight=w)
    await state.set_state(ProfileForm.height)
    await message.answer("Введите ваш рост (в см), например 184:")


@router.message(ProfileForm.height)
async def profile_height(message: Message, state: FSMContext):
    try:
        h = float(message.text.replace(",", "."))
        if h <= 0 or h > 260:
            raise ValueError
    except Exception:
        return await message.answer("Не понял рост. Введите число, например 184:")

    await state.update_data(height=h)
    await state.set_state(ProfileForm.age)
    await message.answer("Введите ваш возраст (лет), например 26:")


@router.message(ProfileForm.age)
async def profile_age(message: Message, state: FSMContext):
    try:
        a = int(message.text)
        if a <= 0 or a > 120:
            raise ValueError
    except Exception:
        return await message.answer("Не понял возраст. Введите целое число, например 26:")

    await state.update_data(age=a)
    await state.set_state(ProfileForm.sex)
    await message.answer("Укажите пол: m (муж) или f (жен):")


@router.message(ProfileForm.sex)
async def profile_sex(message: Message, state: FSMContext):
    s = message.text.strip().lower()
    if s not in ("m", "f"):
        return await message.answer("Введите ровно m или f:")
    await state.update_data(sex=s)
    await state.set_state(ProfileForm.activity)
    await message.answer("Сколько минут активности в день (в среднем)? Например 45:")


@router.message(ProfileForm.activity)
async def profile_activity(message: Message, state: FSMContext):
    try:
        act = int(message.text)
        if act < 0 or act > 1000:
            raise ValueError
    except Exception:
        return await message.answer("Не понял. Введите целое число минут, например 45:")

    await state.update_data(activity=act)
    await state.set_state(ProfileForm.city)
    await message.answer("В каком городе вы находитесь? (для температуры) Например: Moscow")


@router.message(ProfileForm.city)
async def profile_city(message: Message, state: FSMContext):
    city = message.text.strip()
    if len(city) < 2:
        return await message.answer("Город слишком короткий. Введите ещё раз:")

    data = await state.get_data()
    weight = data["weight"]
    height = data["height"]
    age = data["age"]
    sex = data["sex"]
    activity = data["activity"]

    temp_c = await get_city_temp_c(city)
    water_goal = calc_water_goal_ml(weight, activity, temp_c)
    auto_cal_goal = calc_calorie_goal(weight, height, age, sex, activity)

    await state.update_data(city=city, water_goal=water_goal, auto_cal_goal=auto_cal_goal, temp_c=temp_c)
    await state.set_state(ProfileForm.calorie_goal_manual)

    temp_text = f"{temp_c:.1f}°C" if temp_c is not None else "не удалось определить"
    await message.answer(
        f"Температура в городе: {temp_text}\n"
        f"Рассчитанная норма воды: {water_goal} мл/день\n"
        f"Рассчитанная цель калорий: {auto_cal_goal} ккал/день\n\n"
        "Хотите задать калории вручную?\n"
        "Введите число (например 2500) или напишите 'нет'."
    )


@router.message(ProfileForm.calorie_goal_manual)
async def profile_finish(message: Message, state: FSMContext):
    user = ensure_user(message.from_user.id)
    data = await state.get_data()

    text = message.text.strip().lower()
    manual_goal = None
    if text not in ("нет", "no", "не", "n"):
        try:
            manual_goal = int(text)
            if manual_goal < 800 or manual_goal > 8000:
                raise ValueError
        except Exception:
            return await message.answer("Введите число калорий (например 2500) или 'нет'.")

    user["weight"] = data["weight"]
    user["height"] = data["height"]
    user["age"] = data["age"]
    user["sex"] = data["sex"]
    user["activity"] = data["activity"]
    user["city"] = data["city"]
    user["water_goal"] = data["water_goal"]
    user["calorie_goal"] = manual_goal if manual_goal is not None else data["auto_cal_goal"]

    user["logged_water"] = 0
    user["logged_calories"] = 0
    user["burned_calories"] = 0

    await state.clear()

    await message.answer(
        "✅ Профиль сохранён!\n"
        f"Вода: {user['water_goal']} мл/день\n"
        f"Калории: {user['calorie_goal']} ккал/день\n\n"
        "Теперь можно:\n"
        "/log_water 250\n"
        "/log_food банан\n"
        "/log_workout бег 30\n"
        "/check_progress\n"
        "/graph_water\n"
        "/graph_calories"
    )
