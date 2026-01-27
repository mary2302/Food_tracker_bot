from dataclasses import dataclass

from aiogram.fsm.state import State, StatesGroup


class ProfileForm(StatesGroup):
    #Стэйты для создания профиля
    weight = State()
    height = State()
    age = State()
    sex = State()
    activity = State()
    city = State()
    calorie_goal_manual = State()


class FoodForm(StatesGroup):
    #Стэйты для учета еды
    grams = State()

#Хранилище для введенной еды до получения граммовок
@dataclass
class PendingFood:
    name: str
    kcal_per_100g: float
