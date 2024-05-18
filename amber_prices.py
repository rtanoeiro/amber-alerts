from datetime import tzinfo
import datetime
import os

import amberelectric
import numpy as np
import pandas as pd
from amberelectric.api import amber_api
from dotenv import load_dotenv


load_dotenv()

# TODO: Separate into multiple scripts

AMBER_KEY = os.getenv("AMBER_KEY")
CONFIGURATION = amberelectric.Configuration(access_token=AMBER_KEY)

# Create an API instance
api = amber_api.AmberApi.create(configuration=CONFIGURATION)

try:
    sites = api.get_sites()
    site_id = sites[0].id
except amberelectric.ApiException as e:
    print(f"Exception: {e}\n")

usage = api.get_usage(
    site_id=site_id,
    start_date=datetime.date(2024, 2, 26),
    end_date=datetime.date(2024, 4, 25),
)
price = api.get_prices(
    site_id=site_id,
    start_date=datetime.date(2024, 2, 26),
    end_date=datetime.date(2024, 4, 25),
)

energy_dict: dict[str, list] = {
    "start_time": [],
    "consumption": [],
    "price": [],
    "channel": [],
}

for usage_item, price_item in zip(usage, price):
    energy_dict["start_time"].append(usage_item.start_time)
    energy_dict["consumption"].append(usage_item.kwh)
    energy_dict["price"].append(price_item.per_kwh)
    energy_dict["channel"].append(usage_item.channelIdentifier)

energy_dataframe = pd.DataFrame(energy_dict)

energy_dataframe["ovo_price"] = np.where(
    energy_dataframe["channel"] == "E2",
    18.596,
    np.where(
        (energy_dataframe["start_time"].dt.hour == 15)
        | (energy_dataframe["start_time"].dt.hour == 16)
        | (energy_dataframe["start_time"].dt.hour == 17)
        | (energy_dataframe["start_time"].dt.hour == 18)
        | (energy_dataframe["start_time"].dt.hour == 19)
        | (energy_dataframe["start_time"].dt.hour == 20),
        28.991,
        17.902,
    ),
)

energy_dataframe["start_time"] = pd.to_datetime(energy_dataframe["start_time"])
energy_dataframe["start_time"] = energy_dataframe["start_time"].dt.tz_convert(
    "Australia/Melbourne"
) - datetime.timedelta(hours=1)
energy_dataframe["ovo_final_price"] = (
    energy_dataframe["consumption"] * energy_dataframe["ovo_price"]
)
energy_dataframe["amber_final_price"] = (
    energy_dataframe["consumption"] * energy_dataframe["price"]
)
energy_dataframe["difference"] = (
    energy_dataframe["amber_final_price"] - energy_dataframe["ovo_final_price"]
)
energy_dataframe.to_csv("energy_complete.csv", index=False)

days_difference = (
    energy_dataframe["start_time"].max() - energy_dataframe["start_time"].min()
)

energy_dataframe["date"] = energy_dataframe["start_time"].dt.date

energy_dataframe = (
    energy_dataframe.groupby("date")
    .agg(
        {
            "consumption": "sum",
            "ovo_final_price": "sum",
            "amber_final_price": "sum",
        }
    )
    .reset_index("date")
)
energy_dataframe["ovo_final_price"] = (
    energy_dataframe["ovo_final_price"] + 98.17
).round(2)
energy_dataframe["amber_final_price"] = (
    energy_dataframe["amber_final_price"] + 109.60
).round(2)
energy_dataframe["difference"] = (
    energy_dataframe["amber_final_price"] - energy_dataframe["ovo_final_price"]
).round(2)

summary_dataframe = energy_dataframe.copy()
summary_dataframe = {
    "consumption": energy_dataframe["consumption"].sum(),
    "ovo_final_price": energy_dataframe["ovo_final_price"].sum(),
    "amber_final_price": energy_dataframe["amber_final_price"].sum(),
    "difference": energy_dataframe["difference"].sum(),
}

with open("energy_daily.txt", "w") as f:
    f.write(
        f"Your average daily consumption is: {np.round(energy_dataframe['consumption'].mean(),2)}\n"
    )
    f.write(
        f"Your average price with Amber is: {np.round(energy_dataframe['amber_final_price'].mean(),2)} cents\n"
    )
    f.write(
        f"Your average price with OVO is: {np.round(energy_dataframe['ovo_final_price'].mean(),2)} cents\n"
    )

energy_dataframe = pd.concat(
    [energy_dataframe, pd.DataFrame(summary_dataframe, index=[0])]
)

energy_dataframe.to_csv("energy_daily.csv", index=False)
