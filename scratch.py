# %%
import os
import json
from pathlib import Path

import requests
from dotenv import load_dotenv

# %%
load_dotenv()
LAT = os.environ["LAT"]
LON = os.environ["LON"]
API_KEY = os.environ["API_KEY"]

dir_data = Path(__file__).parent / "data"
# %%
url = f"https://api.openweathermap.org/data/2.5/weather?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"

response = requests.get(url)
response.raise_for_status()
response.json()

# %%
with open(dir_data / "output_current.json", "w") as f:
    json.dump(response.json(), f, indent=4)


# %%
# get forecast
url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"

response2 = requests.get(url)
response2.raise_for_status()
response2.json()
# %%
with open(dir_data / "output_forecast.json", "w") as f:
    json.dump(response2.json(), f, indent=4)


# %%
# read cached response
with open(dir_data / "output_current.json", "r") as f:
    res_current = json.load(f)
with open(dir_data / "output_forecast.json", "r") as f:
    res_forecast = json.load(f)

# %%
# extract relevant data
