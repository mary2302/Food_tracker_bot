from datetime import date
from typing import Any, Dict

users: Dict[int, Dict[str, Any]] = {}


def today_key() -> str:
    return date.today().isoformat()


def ensure_user(user_id: int) -> Dict[str, Any]:

    if user_id not in users:
        users[user_id] = {
            "weight": None,
            "height": None,
            "age": None,
            "sex": "m",
            "activity": 0,
            "city": None,
            "water_goal": None,
            "calorie_goal": None,
            "logged_water": 0,
            "logged_calories": 0,
            "burned_calories": 0,
            "burned_water": 0,
            "days": {}, 
        }
    return users[user_id]


def ensure_day(user: dict, day: str) -> dict:
    user.setdefault("days", {})
    user["days"].setdefault(day, {"water": 0, "eaten": 0, "burned": 0})
    return user["days"][day]

