import logging
import os
import datetime
from datetime import timedelta
from typing import TypedDict

import amberelectric  # type: ignore
import numpy as np
import pandas as pd
from amberelectric.api import amber_api  # type: ignore
from dotenv import load_dotenv

load_dotenv()


class EnergyDict(TypedDict):
    start_time: list
    consumption: list
    amber_price: list
    channel: list


AMBER_KEY = os.getenv("AMBER_KEY")


class AmberSummary:

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename="AmberAlerts.log", level=logging.INFO)
        self.amber_key = AMBER_KEY
        self.configuration = amberelectric.Configuration(access_token=self.amber_key)
        self.api = amber_api.AmberApi.create(configuration=self.configuration)
        self.site_id = self.fetch_site_id()
        self.end_date = datetime.datetime.today() - timedelta(days=1)
        self.start_date = self.end_date - timedelta(days=90)

    def fetch_site_id(self):

        try:
            sites = self.api.get_sites()
            site_id = sites[0].id
        except amberelectric.ApiException as e:
            print(f"Exception: {e}\n")

        return site_id

    def get_usage(self):
        usage = self.api.get_usage(
            site_id=self.site_id,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        return usage

    def get_prices(self):

        price = self.api.get_prices(
            site_id=self.site_id,
            start_date=self.start_date,
            end_date=self.end_date,
        )

        return price

    def create_energy_dataframe(self) -> pd.DataFrame:

        usage = self.get_usage()
        prices = self.get_prices()
        energy_dict: EnergyDict = {
            "start_time": [],
            "consumption": [],
            "amber_price": [],
            "channel": [],
        }

        for usage_item, price_item in zip(usage, prices):
            energy_dict["start_time"].append(usage_item.start_time)
            energy_dict["consumption"].append(usage_item.kwh)
            energy_dict["amber_price"].append(price_item.per_kwh)
            energy_dict["channel"].append(usage_item.channelIdentifier)

        return pd.DataFrame(energy_dict)

    def basic_formatting(self, energy_dataframe: pd.DataFrame) -> pd.DataFrame:

        energy_dataframe["ovo_price"] = np.where(
            energy_dataframe["channel"] == "E2",
            17.71,
            np.where(
                (energy_dataframe["start_time"].dt.hour == 15)
                | (energy_dataframe["start_time"].dt.hour == 16)
                | (energy_dataframe["start_time"].dt.hour == 17)
                | (energy_dataframe["start_time"].dt.hour == 18)
                | (energy_dataframe["start_time"].dt.hour == 19)
                | (energy_dataframe["start_time"].dt.hour == 20),
                27.61,
                17.05,
            ),
        )
        energy_dataframe["start_time"] = pd.to_datetime(energy_dataframe["start_time"])
        energy_dataframe["start_time"] = energy_dataframe["start_time"].dt.tz_convert(
            "Australia/Melbourne"
        )
        energy_dataframe["ovo_final_price"] = (
            energy_dataframe["consumption"] * energy_dataframe["ovo_price"]
        )
        energy_dataframe["amber_final_price"] = (
            energy_dataframe["consumption"] * energy_dataframe["amber_price"]
        )
        energy_dataframe["difference"] = (
            energy_dataframe["amber_final_price"] - energy_dataframe["ovo_final_price"]
        )
        energy_dataframe["day"] = energy_dataframe["start_time"].dt.date
        energy_dataframe["_month"] = energy_dataframe["start_time"].dt.month
        energy_dataframe["_year"] = energy_dataframe["start_time"].dt.year
        energy_dataframe["month"] = energy_dataframe.apply(
            lambda x: f"{x['_month']}-{x['_year']}", axis=1
        )
        energy_dataframe["year"] = energy_dataframe["start_time"].dt.year

        return energy_dataframe

    def summarize_energy(self, summary_level: str, energy_dataframe: pd.DataFrame):

        if summary_level not in ["day", "month", "year"]:
            raise ValueError(
                "Invalid summary level. Please use 'day', 'month', or 'year'."
            )

        energy_dataframe = (
            energy_dataframe.groupby(summary_level, as_index=True)
            .agg(
                {
                    "consumption": "sum",
                    "ovo_final_price": "sum",
                    "amber_final_price": "sum",
                    "difference": "sum",
                }
            )
            .reset_index()
        )
        energy_dataframe.sort_values(by=summary_level, inplace=True)

        energy_dataframe.to_csv(f"summary_energy_{summary_level}.csv", index=False)

    def send_email_summary(
        self, email_text: str, summary_level: str, energy_dataframe: pd.DataFrame
    ):

        from utils.email_api import Email, EMAIL

        email = Email(to_address=[EMAIL], subject="Energy Summary")
        energy_dataframe_month = self.summarize_energy(
            summary_level="month", energy_dataframe=energy_dataframe
        )
        energy_dataframe_day = self.summarize_energy(
            summary_level="day", energy_dataframe=energy_dataframe
        )

        avg_consumption = energy_dataframe["consumption"].mean()
        avg_ovo_price = energy_dataframe["ovo_final_price"].mean()
        avg_amber_price = energy_dataframe["amber_final_price"].mean()
        price_difference = energy_dataframe["difference"].sum()
        date_difference = (
            energy_dataframe["start_time"].max() - energy_dataframe["start_time"].min()
        )
        n_months = energy_dataframe["_month"].max() - energy_dataframe["_month"].min()

        email_text = f"""
        In the last {date_difference} days, the average consumption was {avg_consumption} kWh.

        The average OVO price for that period would be ${avg_ovo_price}.
        The average Amber price was ${avg_amber_price}.
        
        In total the raw difference in price (amber - ovo) was ${price_difference}.

        But considering that the summary contains {n_months} months. And for each month you have a $25 credit, you would have saved ${price_difference - (n_months * 25)} with Amber.
        """

        return email_text

    def trigger_job(self):
        energy_dataframe = self.create_energy_dataframe()
        energy_dataframe = self.basic_formatting(energy_dataframe=energy_dataframe)
        self.send_email_summary(
            email_text="Energy Summary",
            summary_level="month",
            energy_dataframe=energy_dataframe,
        )
