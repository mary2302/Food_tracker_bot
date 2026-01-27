from typing import Optional

#Словарь известных тренировок
WORKOUT_MET = {
    "бег": 10,
    "ходьба": 4,
    "велосипед": 8,
    "силовая": 7,
    "йога": 3,
    "плавание": 9,
}

from typing import Optional

def calc_water_goal_ml(weight_kg: float, activity_min: int, temp_c: Optional[float]) -> int:
    #Норма воды - 30мл/кг массы тела
    norm = weight_kg * 30.0

    #+500 мл за каждые 30 минут тренировки
    sport = (activity_min // 30) * 500

    heat = 0

    # Если известна температура и она выше 25°C => +750 мл
    if temp_c is not None and temp_c > 25:
        add_heat = 750

    return int(round(norm + sport + heat))


def calc_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    # BMR = 10*вес(кг) + 6.25*рост(см) - 5*возраст + s
    s = 5 if sex == "m" else -161
    return 10 * weight_kg + 6.25 * height_cm - 5 * age + s


def calc_activity_kcal(activity_min: int) -> int:
    #Компенсация ккал по тренировкам:
    # 90+ минут -> +450 ккал
    if activity_min >= 90:
        return 450
    # 60–89 минут -> +350 ккал
    if activity_min >= 60:
        return 350
    # 30–59 минут -> +200 ккал
    if activity_min >= 30:
        return 200
    return 0


def calc_calorie_goal(weight_kg: float, height_cm: float, age: int, sex: str, activity_min: int) -> int:
    #Считаем базовый обмен (BMR)
    bmr = calc_bmr(weight_kg, height_cm, age, sex)

    #Получаем добавку к калориям за активность
    sport = calc_activity_kcal(activity_min)

    return int(round(bmr + sport))


def estimate_workout_kcal(workout_type: str, minutes: int, weight_kg: Optional[float]) -> int:
    #Берём “базовый расход ккал/мин” по типу тренировки из словаря WORKOUT_MET (дефолт 6ккал/мин)
    base_per_min = WORKOUT_MET.get(workout_type.lower(), 6)

    # Масштабируем расход относительно “эталона” 75 кг
    if weight_kg:
        base_per_min *= (weight_kg / 75.0)

    return int(round(base_per_min * minutes))

