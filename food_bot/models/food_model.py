from dataclasses import dataclass


@dataclass(frozen=True)
class FoodQuery:
    """Ввод пользователя: /log_food <название>"""
    query: str

    @classmethod
    def parse_from_command(cls, text: str) -> "FoodQuery":
        parts = text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            raise ValueError("Формат: /log_food <название продукта>")
        return cls(query=parts[1].strip())


@dataclass(frozen=True)
class FoodProduct:
    """Результат поиска продукта (например, из OpenFoodFacts)."""
    name: str
    kcal_per_100g: float

    @classmethod
    def validate(cls, name: str, kcal_per_100g: float) -> "FoodProduct":
        if not name.strip():
            raise ValueError("Пустое имя продукта")
        if kcal_per_100g <= 0 or kcal_per_100g > 2000:
            raise ValueError("Некорректные ккал/100г")
        return cls(name=name.strip(), kcal_per_100g=float(kcal_per_100g))


@dataclass(frozen=True)
class FoodIntakeInput:
    """Ввод пользователя на втором шаге: граммы."""
    grams: float

    @classmethod
    def parse_grams(cls, text: str) -> "FoodIntakeInput":
        try:
            g = float(text.replace(",", "."))
        except Exception as e:
            raise ValueError("Граммы должны быть числом") from e
        if g <= 0 or g > 5000:
            raise ValueError("Граммы вне диапазона (0..5000]")
        return cls(grams=g)


@dataclass(frozen=True)
class FoodEntry:
    """Готовая запись еды (после выбора продукта + ввода граммов)."""
    product_name: str
    grams: float
    kcal: int  # округлённые

    @classmethod
    def from_product_and_input(cls, product: FoodProduct, intake: FoodIntakeInput) -> "FoodEntry":
        kcal_f = product.kcal_per_100g * intake.grams / 100.0
        return cls(
            product_name=product.name,
            grams=intake.grams,
            kcal=int(round(kcal_f)),
        )
