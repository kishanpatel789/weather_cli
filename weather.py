from datetime import datetime, timezone, timedelta
from pathlib import Path

import requests
import yaml


def load_config(config_path=None):
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    required_keys = [
        "lat",
        "lon",
        "api_key",
    ]
    for key in required_keys:
        if key not in config["weather"]:
            raise ValueError(f"Missing required config key: {key}")

    return config["weather"]


config = load_config()
LAT = config["lat"]
LON = config["lon"]
API_KEY = config["api_key"]
UNITS = config.get("units", "metric")
NUM_DAYS = int(config.get("num_days", 3))
BASE_URL = config.get("base_url", "https://api.openweathermap.org/data/2.5")

# get current weather
url = f"{BASE_URL}/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}"
response = requests.get(url)
response.raise_for_status()
current_weather = response.json()

# get forecast
url = f"{BASE_URL}/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units={UNITS}&cnt={NUM_DAYS*8}"
response2 = requests.get(url)
response2.raise_for_status()
forecast_weather = response2.json()


# extract relevant data
def process_datetime(data_dt: int, data_tz: int) -> datetime:
    datetime_utc = datetime.fromtimestamp(data_dt, timezone.utc)
    datetime_local = datetime_utc.astimezone(timezone(timedelta(seconds=data_tz)))

    return datetime_local


def process_wind(wind: dict) -> str:
    speed_kmh = wind["speed"] / 1000 * 60 * 60  # convert m/s to km/hr
    speed_deg = wind["deg"]

    return f"{round(speed_kmh):,} km/h from {speed_deg} deg"


def format_temp(temp: float) -> str:
    return f"{round(temp)}\u00b0C"


def generate_current_weather_output(w: dict) -> str:
    line_items = [
        process_datetime(w["dt"], w["timezone"]).strftime("%Y-%m-%d %H:%M"),  # datetime
        f"{w['weather'][0]['main']} - {w['weather'][0]['description']}",  # condition
        format_temp(w["main"]["temp"]),  # temp
        process_wind(w["wind"]),  # wind
        f"{w['clouds']['all']}% cloudy",  # cloud coverage
    ]
    if "rain" in w:
        line_items.append(f"{w['rain']['1h']} mm/h rain")  # rain amt
    if "snow" in w:
        line_items.append(f"{w['snow']['1h']} mm/h snow")  # snow amt

    return "\n".join(line_items)


def generate_hour_line_content(rec: dict, rec_datetime: datetime) -> str:
    hour_content = [
        rec_datetime.strftime("%H:%M"),  # hour
        f"{format_temp(rec['main']['temp']):>4}",  # temp
        f"{rec['weather'][0]['main']} ({round(rec['pop']*100)}%)",  # weather with prep. prob.
    ]
    return " ".join(hour_content)


def generate_forecast_weather_output(w: dict) -> str:
    line_items = [""]
    track_date = None

    for rec in w["list"]:
        rec_datetime = process_datetime(rec["dt"], w["city"]["timezone"])
        if rec_datetime.date() != track_date:
            track_date = rec_datetime.date()
            line_item = (
                track_date.strftime("%a %m.%d")
                + " " * 2
                + generate_hour_line_content(rec, rec_datetime)
            )
        else:
            line_item = " " * 11 + generate_hour_line_content(rec, rec_datetime)
        line_items.append(line_item)

    return "\n".join(line_items)


if __name__ == "__main__":
    print(generate_current_weather_output(current_weather))
    print(generate_forecast_weather_output(forecast_weather))
