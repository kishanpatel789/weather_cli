# %%
import os
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

import requests
from dotenv import load_dotenv

# %%
load_dotenv()
LAT = os.environ["LAT"]
LON = os.environ["LON"]
API_KEY = os.environ["API_KEY"]
BASE_URL = "https://api.openweathermap.org/data/2.5"

dir_data = Path(__file__).parent / "data"
# %%
# get current weather
url = f"{BASE_URL}/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"

response = requests.get(url)
response.raise_for_status()
current_weather = response.json()

# %%
with open(dir_data / "output_current.json", "w") as f:
    json.dump(current_weather, f, indent=4)


# %%
# get forecast
url = f"{BASE_URL}/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"

response2 = requests.get(url)
response2.raise_for_status()
forecast_weather = response2.json()
# %%
with open(dir_data / "output_forecast.json", "w") as f:
    json.dump(forecast_weather, f, indent=4)


# %%
# read cached response
with open(dir_data / "output_current.json", "r") as f:
    current_weather = json.load(f)
with open(dir_data / "output_forecast.json", "r") as f:
    forecast_weather = json.load(f)

# %%
# extract relevant data
def process_datetime(data_dt: int, data_tz: int) -> str:
    datetime_utc = datetime.fromtimestamp(data_dt, timezone.utc)
    datetime_local = datetime_utc.astimezone(timezone(timedelta(seconds=data_tz)))
    
    return datetime_local.strftime("%Y-%m-%d %H:%M:%S %Z")

def process_wind(wind: dict) -> str:
    speed_kmh = wind["speed"] / 1000 * 60 * 60 # convert m/s to km/hr
    speed_deg = wind["deg"]

    return f"{round(speed_kmh):,} km/h at {speed_deg} deg"

current_weather_output = f"""
{process_datetime(current_weather["dt"], current_weather["timezone"])}
{current_weather["weather"][0]["main"]} - {current_weather["weather"][0]["description"]}
{current_weather["main"]["temp"]} C
{process_wind(current_weather["wind"])}
{current_weather["clouds"]["all"]}% cloudy
#rain and snow"""

print(current_weather_output)

# print(
#     process_datetime(current_weather["dt"], current_weather["timezone"]),
#     current_weather["weather"][0]["main"],  # weather condition
#     current_weather["main"]["temp"],  # temperature
#     current_weather["main"]["humidity"],  # humidity
#     # wind
#     # cloud coverage
# )

#%%
datetime.fromtimestamp(
)

datetime.utcoffset
# %%
# test city search
url = f"https://api.openweathermap.org/data/2.5/weather?q=Valley+Ranch,TX,US&appid={API_KEY}&units=metric"
response = requests.get(url)
response.raise_for_status()
response.json()

# %%
