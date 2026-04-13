import httpx
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"

# Thresholds for danger detection
WIND_SPEED_DANGER_THRESHOLD = 15  # m/s (~54 km/h, strong gale)

SEVERE_WEATHER_CONDITIONS = [
    "Thunderstorm",
    "Tornado",
    "Squall",
    "Tropical Storm",
    "Hurricane",
    "Typhoon",
    "Cyclone",
    "Blizzard",
]


async def fetch_weather(lat: float, lng: float) -> dict | None:
    """
    Fetch current weather for a given lat/lng.
    Returns simplified dict with risk-relevant fields.
    """
    params = {
        "lat": lat,
        "lon": lng,
        "appid": OPENWEATHER_KEY,
        "units": "metric",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(WEATHER_URL, params=params)

    if response.status_code != 200:
        print(f"[OpenWeather Error] Status: {response.status_code} | {response.text}")
        return None

    data = response.json()

    weather_main = data["weather"][0]["main"]
    wind_speed = data["wind"]["speed"]

    is_severe_condition = weather_main in SEVERE_WEATHER_CONDITIONS
    is_high_wind = wind_speed >= WIND_SPEED_DANGER_THRESHOLD

    return {
        "city": data.get("name", "Unknown"),
        "weather_main": weather_main,
        "weather_description": data["weather"][0]["description"],
        "wind_speed_ms": wind_speed,
        "temperature_c": data["main"]["temp"],
        "humidity_percent": data["main"]["humidity"],
        "is_dangerous": is_severe_condition or is_high_wind,
        "danger_reason": (
            f"Severe condition: {weather_main}" if is_severe_condition
            else f"High wind speed: {wind_speed} m/s" if is_high_wind
            else "None"
        ),
    }


async def fetch_weather_for_route(origin: dict, destination: dict) -> dict:
    """
    Checks weather at both origin and destination simultaneously.
    origin/destination are dicts with 'lat' and 'lng' keys.
    """
    # Run both requests concurrently instead of one after the other
    origin_weather, destination_weather = await asyncio.gather(
        fetch_weather(origin["lat"], origin["lng"]),
        fetch_weather(destination["lat"], destination["lng"])
    )

    any_danger = (
        (origin_weather and origin_weather["is_dangerous"]) or
        (destination_weather and destination_weather["is_dangerous"])
    )

    danger_location = None
    if origin_weather and origin_weather["is_dangerous"]:
        danger_location = origin_weather["city"]
    elif destination_weather and destination_weather["is_dangerous"]:
        danger_location = destination_weather["city"]

    return {
        "origin": origin_weather,
        "destination": destination_weather,
        "any_danger": any_danger,
        "danger_location": danger_location,
    }


# ---- Manual test ----
if __name__ == "__main__":
    async def run_tests():
        test_locations = [
            {"name": "Tokyo Port",    "lat": 35.6895, "lng": 139.6917},
            {"name": "LA Port",       "lat": 33.7361, "lng": -118.2922},
            {"name": "Shanghai Port", "lat": 31.2304, "lng": 121.4737},
        ]

        print("=" * 60)
        print("TEST 1: Individual location weather")
        print("=" * 60)
        for loc in test_locations:
            print(f"\n--- {loc['name']} ---")
            weather = await fetch_weather(loc["lat"], loc["lng"])
            if weather:
                print(f"City:        {weather['city']}")
                print(f"Condition:   {weather['weather_main']} — {weather['weather_description']}")
                print(f"Wind Speed:  {weather['wind_speed_ms']} m/s")
                print(f"Temperature: {weather['temperature_c']}°C")
                print(f"Humidity:    {weather['humidity_percent']}%")
                print(f"DANGEROUS:   {weather['is_dangerous']}")
                print(f"Reason:      {weather['danger_reason']}")

        print("\n")
        print("=" * 60)
        print("TEST 2: Full route weather check (LA → Tokyo)")
        print("=" * 60)
        route = await fetch_weather_for_route(
            origin={"lat": 33.7361, "lng": -118.2922},
            destination={"lat": 35.6895, "lng": 139.6917}
        )
        print(f"\nOrigin ({route['origin']['city']}) dangerous:      {route['origin']['is_dangerous']}")
        print(f"Destination ({route['destination']['city']}) dangerous: {route['destination']['is_dangerous']}")
        print(f"Any danger on route:   {route['any_danger']}")
        print(f"Danger location:       {route['danger_location']}")

    asyncio.run(run_tests())