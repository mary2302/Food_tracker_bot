from typing import Optional

import aiohttp

from config import OPENWEATHER_API_KEY as key


async def get_city_temp_c(city: str) -> Optional[float]:
    if not key:
        return None

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={key}&units=metric"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                return float(data["main"]["temp"])
    except Exception:
        return None
