from dataclasses import dataclass

from aiogram.fsm.state import State, StatesGroup


class ProfileForm(StatesGroup):
    weight = State()
    height = State()
    age = State()
    sex = State()
    activity = State()
    city = State()
    calorie_goal_manual = State()


class FoodForm(StatesGroup):
    grams = State()


@dataclass
class PendingFood:
    name: str
    kcal_per_100g: float
