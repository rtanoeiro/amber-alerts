import logging
import os
from typing import TypedDict

from datetime import datetime, timedelta
from amberelectric.exceptions import ApiException
from amberelectric.models.usage import Usage
from dotenv import load_dotenv
from amberelectric.api.amber_api import AmberApi
from amberelectric.configuration import Configuration
from amberelectric.api_client import ApiClient

load_dotenv()

AMBER_KEY = os.getenv("AMBER_KEY")
SITE_ID = os.getenv("SITE_ID")


class EnergyUsage(TypedDict):
    energy_type: list[str]
    duration: list[int]
    spot_per_kwh: list[float]
    per_kwh: list[float]
    date: list[datetime]
    nem_time: list[datetime]
    start_time: list[datetime]
    end_time: list[datetime]
    renewables: list[float]
    channel_type: list[str]
    spike_status: list[str]
    descriptor: list[float]
    channel_identifier: list[str]
    kwh: list[float]
    quality: list[str]
    energy_cost: list[float]


class Amber:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            format="%(asctime)s - %(message)s",
            filename="AmberAlerts.log",
            level=logging.DEBUG,
        )
        self.logger.info("Initializing AmberSummary")
        self.amber_key = AMBER_KEY
        self.configuration = Configuration(access_token=AMBER_KEY)
        self.api = AmberApi(api_client=ApiClient(configuration=self.configuration))
        self.site_id = self.fetch_site_id()
        self.default_start_date = datetime.today() - timedelta(days=2)
        self.default_end_date = datetime.today() - timedelta(days=1, hours=22)
        self.energy_dict: EnergyUsage = self.create_energy_dict()

    def create_energy_dict(self) -> dict[EnergyUsage]:
        keys = EnergyUsage.__annotations__.keys()
        dict_to_create = {}
        for key in keys:
            dict_to_create[key] = []

        return dict_to_create

    def fetch_site_id(self):
        if SITE_ID:
            self.logger.info("Site ID found in environment variables")
            return SITE_ID
        else:
            self.logger.info("Fetching site ID...")
            try:
                sites = self.api.get_sites()
                site_id = sites[0].id
            except ApiException as e:
                self.logger.error(f"Exception: {e}\n")
            return site_id

    def get_usage(self):
        results = self.api.get_usage(
            self.site_id,
            start_date=self.default_start_date,
            end_date=self.default_end_date,
        )

        return results

    def unwrap_usage(self, usage: list[Usage]):
        energy_dict = self.energy_dict.copy()
        for item in usage:
            # append values to the list of values in each dict key
            energy_dict["energy_type"].append(item.type)
            energy_dict["duration"].append(item.duration)
            energy_dict["spot_per_kwh"].append(item.spot_per_kwh)
            energy_dict["per_kwh"].append(item.per_kwh)
            energy_dict["date"].append(item.var_date)
            energy_dict["nem_time"].append(item.nem_time)
            energy_dict["start_time"].append(item.start_time)
            energy_dict["end_time"].append(item.end_time)
            energy_dict["renewables"].append(item.renewables)
            energy_dict["channel_type"].append(item.channel_type.value)
            energy_dict["spike_status"].append(item.spike_status.value)
            energy_dict["descriptor"].append(item.descriptor.value)
            energy_dict["channel_identifier"].append(item.channel_identifier)
            energy_dict["kwh"].append(item.kwh)
            energy_dict["quality"].append(item.quality)
            energy_dict["energy_cost"].append(item.cost)
        return energy_dict
