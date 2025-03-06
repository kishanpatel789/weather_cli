# %%
import os
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

import requests
from dotenv import load_dotenv
import textwrap

# %%
load_dotenv()
LAT = os.environ["LAT"]
LON = os.environ["LON"]
API_KEY = os.environ["API_KEY"]
UNITS = os.environ.get("UNITS", "metric")
NUM_DAYS = int(os.environ.get("NUM_DAYS", 3))
BASE_URL = "https://api.openweathermap.org/data/2.5"

dir_data = Path(__file__).parent / "data"
# %%
# get current weather
url = f"{BASE_URL}/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}"

response = requests.get(url)
response.raise_for_status()
current_weather = response.json()

# %%
with open(dir_data / "output_current.json", "w") as f:
    json.dump(current_weather, f, indent=4)


# %%
# get forecast
url = f"{BASE_URL}/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}&cnt={NUM_DAYS*8}"

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
def process_datetime(data_dt: int, data_tz: int) -> datetime:
    datetime_utc = datetime.fromtimestamp(data_dt, timezone.utc)
    datetime_local = datetime_utc.astimezone(timezone(timedelta(seconds=data_tz)))
    
    return datetime_local

def process_wind(wind: dict) -> str:
    speed_kmh = wind["speed"] / 1000 * 60 * 60 # convert m/s to km/hr
    speed_deg = wind["deg"]

    return f"{round(speed_kmh):,} km/h from {speed_deg} deg"

def generate_current_weather_output(w: dict) -> str:
    output = f"""\
        {process_datetime(w["dt"], w["timezone"])}
        {w["weather"][0]["main"]} - {w["weather"][0]["description"]}
        {round(w["main"]["temp"])}\u00B0C
        {process_wind(w["wind"])}
        {w["clouds"]["all"]}% cloudy"""
    
    if "rain" in w:
        output += f"\n{w['rain']['1h']} mm/h rain"
    if "snow" in w:
        output += f"\n{w['snow']['1h']} mm/h snow"

    return textwrap.dedent(output)

print(generate_current_weather_output(current_weather))

def generate_forecast_weather_output(w: dict) -> str:
    output = ""
    track_date = None

    for rec in w["list"]:
        rec_datetime = process_datetime(rec["dt"], w["city"]["timezone"])
        if rec_datetime.date() != track_date:
            track_date = rec_datetime.date()
            output += "\n" + track_date.strftime("%a %m.%d")

        line_items = [
            rec_datetime.strftime("%H:%M"), # hour
            f"{round(rec['main']['temp'])}\u00B0C", # temp
            f"{rec['weather'][0]['main']} ({round(rec['pop']*100)}%)", # weather with prep. prob.
        ]
        output += "\n" + textwrap.indent(" ".join(line_items), " "*4)

    return textwrap.dedent(output)

print(generate_forecast_weather_output(forecast_weather))

# %%
# test city search
url = f"https://api.openweathermap.org/data/2.5/weather?q=Valley+Ranch,TX,US&appid={API_KEY}&units=metric"
response = requests.get(url)
response.raise_for_status()
response.json()

# %%
