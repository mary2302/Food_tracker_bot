from dataclasses import dataclass

@dataclass(frozen=True)
class WorkoutInput:
    workout_type: str
    minutes: int
    """
    ## WorkoutInput

    Модель для входных данных тренировки от пользователя.

    ### Поля
    - `workout_type: str` — тип тренировки (строка, приводится к нижнему регистру).
    - `minutes: int` — длительность тренировки в минутах.

    ### Пример команды
    `/log_workout бег 45`

    ### Методы
    - `parse_from_command(text: str) -> WorkoutInput` — парсит текст команды и валидирует ввод.
      Бросает `ValueError` с понятным сообщением, если формат неверный.
    """
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
    workout_type: str
    minutes: int
    burned_kcal: int
    extra_water_ml: int = 0
    """
    ## WorkoutEntry

    Модель для сохранённой записи тренировки: содержит исходные данные + рассчитанные значения.

    ### Поля
    - `workout_type: str` — тип тренировки.
    - `minutes: int` — длительность тренировки.
    - `burned_kcal: int` — сожжённые калории (готовое число, рассчитанное снаружи).
    - `extra_water_ml: int = 0` — дополнительная вода к цели (мл), по умолчанию 0.

    ### Логика воды
    Добавочная вода: `+200 мл` за каждые полные `30 минут` тренировки.

    ### Методы
    - `from_input(inp: WorkoutInput, burned_kcal: int) -> WorkoutEntry` —
      создаёт запись из `WorkoutInput`, добавляя:
      - `burned_kcal`
      - `extra_water_ml` по формуле.
    """
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
