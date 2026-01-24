from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class WorkoutInput:
    """Ввод пользователя: /log_workout <тип> <мин>"""
    workout_type: str
    minutes: int

    @classmethod
    def parse_from_command(cls, text: str) -> "WorkoutInput":
        parts = text.split()
        if len(parts) < 3:
            raise ValueError("Формат: /log_workout <тип> <мин>")
        wtype = parts[1].strip().lower()
        if not wtype:
            raise ValueError("Пустой тип тренировки")

        try:
            minutes = int(parts[2])
        except Exception as e:
            raise ValueError("Минуты должны быть числом") from e
        if minutes <= 0 or minutes > 1000:
            raise ValueError("Минуты вне диапазона (0..1000]")

        return cls(workout_type=wtype, minutes=minutes)


@dataclass(frozen=True)
class WorkoutEntry:
    """Готовая запись тренировки (после расчёта ккал)."""
    workout_type: str
    minutes: int
    burned_kcal: int
    extra_water_ml: int = 0

    @classmethod
    def from_input(cls, inp: WorkoutInput, burned_kcal: int) -> "WorkoutEntry":
        extra_water = (inp.minutes // 30) * 200
        return cls(
            workout_type=inp.workout_type,
            minutes=inp.minutes,
            burned_kcal=int(burned_kcal),
            extra_water_ml=int(extra_water),
        )


def calc_extra_water_ml(minutes: int) -> int:
    return (minutes // 30) * 200
