from dataclasses import dataclass


@dataclass(frozen=True)
class FoodQuery:
    query: str
    """
    ## FoodQuery

    Модель запроса на лог еды от пользователя.

    ### Поля
    - `query: str` — текст запроса (название продукта/блюда), очищенный от пробелов по краям.

    ### Методы
    - `parse_from_command(text: str) -> FoodQuery` — извлекает запрос из команды вида
      `"/log_food <название продукта>"` и валидирует, что он не пустой.

    ### Пример
    `/log_food йогурт` → `FoodQuery(query="йогурт")`
    """
    @classmethod
    def parse_from_command(cls, text: str) -> "FoodQuery":
        parts = text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            raise ValueError("Формат: /log_food <название продукта>")
        return cls(query=parts[1].strip())


@dataclass(frozen=True)
class FoodProduct:
    name: str
    kcal_per_100g: float
    """
    ## FoodProduct

    Модель продукта с известной калорийностью на 100 г.

    ### Поля
    - `name: str` — отображаемое название продукта.
    - `kcal_per_100g: float` — калорийность на 100 грамм.

    ### Методы
    - `validate(name: str, kcal_per_100g: float) -> FoodProduct` —
      валидирует входные данные и возвращает корректный объект.

    ### Ограничения
    - `name` не пустое.
    - `kcal_per_100g` в диапазоне `(0..2000]`.
    """
    @classmethod
    def validate(cls, name: str, kcal_per_100g: float) -> "FoodProduct":
        if not name.strip():
            raise ValueError("Пустое имя продукта")
        if kcal_per_100g <= 0 or kcal_per_100g > 2000:
            raise ValueError("Некорректные ккал/100г")
        return cls(name=name.strip(), kcal_per_100g=float(kcal_per_100g))


@dataclass(frozen=True)
class FoodIntakeInput:
    grams: float
    """
    ## FoodIntakeInput

    Модель порции (сколько грамм пользователь съел).

    ### Поля
    - `grams: float` — граммы порции.

    ### Методы
    - `parse_grams(text: str) -> FoodIntakeInput` — парсит число грамм из текста.
      Поддерживает запятую и точку как разделитель (`"150,5"` → `150.5`).

    ### Ограничения
    - `grams` в диапазоне `(0..5000]` — защита от ошибок ввода.
    """
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
    product_name: str
    grams: float
    kcal: int
    """
    ## FoodEntry

    Модель финальной записи о съеденном продукте:
    хранит название, граммы и рассчитанные калории.

    ### Поля
    - `product_name: str` — название продукта (как в `FoodProduct.name`).
    - `grams: float` — сколько грамм съедено.
    - `kcal: int` — итоговые калории порции (округлённое целое).

    ### Методы
    - `from_product_and_input(product: FoodProduct, intake: FoodIntakeInput) -> FoodEntry` —
      считает калории по формуле и создаёт объект записи.

    ### Формула
    `kcal = round(kcal_per_100g * grams / 100)`
    """   

    @classmethod
    def from_product_and_input(cls, product: FoodProduct, intake: FoodIntakeInput) -> "FoodEntry":
        kcal_f = product.kcal_per_100g * intake.grams / 100.0
        return cls(
            product_name=product.name,
            grams=intake.grams,
            kcal=int(round(kcal_f)),
        )
