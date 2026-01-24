from typing import Optional


WORKOUT_MET = {
    "бег": 10,
    "ходьба": 4,
    "велосипед": 8,
    "силовая": 7,
    "йога": 3,
    "плавание": 9,
}

def calc_water_goal_ml(weight_kg: float, activity_min: int, temp_c: Optional[float]) -> int:
    base = weight_kg * 30.0
    add_activity = (activity_min // 30) * 500
    add_heat = 0
    if temp_c is not None and temp_c > 25:
        add_heat = 750
    return int(round(base + add_activity + add_heat))


def calc_bmr_mifflin(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    s = 5 if sex == "m" else -161
    return 10 * weight_kg + 6.25 * height_cm - 5 * age + s


def calc_activity_cal_bonus(activity_min: int) -> int:
    if activity_min >= 90:
        return 450
    if activity_min >= 60:
        return 350
    if activity_min >= 30:
        return 200
    return 0


def calc_calorie_goal(weight_kg: float, height_cm: float, age: int, sex: str, activity_min: int) -> int:
    bmr = calc_bmr_mifflin(weight_kg, height_cm, age, sex)
    bonus = calc_activity_cal_bonus(activity_min)
    return int(round(bmr + bonus))


def estimate_workout_kcal(workout_type: str, minutes: int, weight_kg: Optional[float]) -> int:
    base_per_min = WORKOUT_MET.get(workout_type.lower(), 6)
    if weight_kg:
        base_per_min *= (weight_kg / 75.0)
    return int(round(base_per_min * minutes))
