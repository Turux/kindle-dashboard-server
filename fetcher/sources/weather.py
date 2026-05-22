# fetcher/sources/weather.py

import requests
from config import WEATHER_LAT, WEATHER_LON

def fetch_weather():
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={WEATHER_LAT}&longitude={WEATHER_LON}"
        f"&current=temperature_2m,weathercode,precipitation_probability"
        f"&timezone=Europe/London"
    )
    r    = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()

    current = data["current"]
    temp    = round(current["temperature_2m"])
    code    = current["weathercode"]
    rain    = current["precipitation_probability"]

    return {
        "temp": f"{temp}°",
        "desc": _weather_desc(code),
        "rain": f"Rain {rain}%" if rain > 20 else "",
    }

def _weather_desc(code):
    if code == 0:            return "Clear"
    elif code <= 2:          return "Partly cloudy"
    elif code <= 3:          return "Overcast"
    elif code <= 9:          return "Foggy"
    elif code <= 19:         return "Drizzle"
    elif code <= 29:         return "Rain"
    elif code <= 39:         return "Snow"
    elif code <= 49:         return "Freezing fog"
    elif code <= 59:         return "Drizzle"
    elif code <= 69:         return "Rain"
    elif code <= 79:         return "Snow"
    elif code <= 84:         return "Showers"
    elif code <= 94:         return "Thunderstorm"
    else:                    return "Storm"