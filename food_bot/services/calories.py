from typing import List, Optional, Tuple, Any
import math
import aiohttp


def parse_kcal_100g(nutr: dict) -> Optional[float]:
    # Получем ккал из nutriments
    # Безопасно приводим к float или возвращаем None, если значение некорректное
    if not nutr:
        return None

    raw = nutr.get("energy-kcal_100g")

    if raw is None:
        raw = nutr.get("energy-kcal")

    if raw is None:
        return None

    try:
        if isinstance(raw, str):
            raw = raw.strip().replace(",", ".")
            if raw == "":
                return None
        val = float(raw)
    except (TypeError, ValueError):
        return None

    if not math.isfinite(val) or val <= 0 or val > 2000:
        return None

    return val


async def search_food_kcal_per_100g(query: str) -> Optional[Tuple[str, float]]:
    #Асинхронный запрос в OpenFoodFacts на получение ккал по 'еде' от пользователя
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 10,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
    except Exception:
        return None

    for p in data.get("products", []) or []:
        nutr = p.get("nutriments", {}) or {}
        kcal = parse_kcal_100g(nutr)
        if kcal is None:
            continue

        name = p.get("product_name") or p.get("generic_name") or query
        name = str(name).strip() if name else query
        return (name, kcal)

    return None


async def search_food_candidates(query: str, limit: int = 5) -> List[Tuple[str, float]]:
    #Асинхронная функция для сбора кандидатов по названию продукта по минимальной калорийности (топ-5)
    #Получает информацию из OpenFoodFacts
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": query,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 25,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                if resp.status != 200:
                    return []
                data = await resp.json()
    except Exception:
        return []

    items: List[Tuple[str, float]] = []
    for p in data.get("products", []) or []:
        nutr = p.get("nutriments", {}) or {}
        kcal100 = parse_kcal_100g(nutr)
        if kcal100 is None:
            continue

        name = p.get("product_name") or p.get("generic_name") or query
        name = str(name).strip() if name else query

        items.append((name, kcal100))

    items.sort(key=lambda x: x[1])
    return items[:limit]
