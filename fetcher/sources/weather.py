# fetcher/sources/weather.py

import requests
import json
import os
from config import WEATHER_LAT, WEATHER_LON

DEVICE_CONFIG = "/data/cache/device_config.json"

def fetch_weather():
    # use device-provided coordinates if available, fall back to config
    lat, lon = WEATHER_LAT, WEATHER_LON
    try:
        if os.path.exists(DEVICE_CONFIG):
            with open(DEVICE_CONFIG) as f:
                cfg = json.load(f)
            lat = cfg.get("lat", lat)
            lon = cfg.get("lon", lon)
    except:
        pass

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,weathercode,precipitation_probability"
        f"&timezone=auto"
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