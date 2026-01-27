import io
from datetime import date, timedelta
import matplotlib.pyplot as plt
from aiogram.types import BufferedInputFile
from typing import List


def last_n_days(n: int = 14) -> List[str]:
    if n < 2:
        n = 2
    d0 = date.today()
    return [(d0 - timedelta(days=i)).isoformat() for i in range(n - 1, -1, -1)]


def _save_fig_to_png_bytes() -> bytes:
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=160)
    plt.close()
    buf.seek(0)
    return buf.read()


def plot_water(days: List[str], water_ml: List[int]) -> bytes:
    plt.figure()
    plt.plot(days, water_ml)
    plt.xticks(rotation=45, ha="right")
    plt.title("Вода (мл) по дням")
    plt.tight_layout()
    return _save_fig_to_png_bytes()


def plot_calories(days: List[str], eaten: List[int], burned: List[int], balance: List[int]) -> bytes:
    plt.figure()
    plt.plot(days, eaten, label="Потреблено")
    plt.plot(days, burned, label="Сожжено")
    plt.plot(days, balance, label="Баланс")
    plt.xticks(rotation=45, ha="right")
    plt.title("Калории по дням")
    plt.legend()
    plt.tight_layout()
    return _save_fig_to_png_bytes()
