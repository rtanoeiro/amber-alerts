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
    channel: str
    cost: float
    descriptor: str
    duration: int
    nem_time: datetime
    kwh: float
    per_kwh: float
    quality: str
    renewables: float


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
        self.default_end_date = datetime.today() - timedelta(days=1)
        self.energy_dict: EnergyUsage = {}

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
        for item in usage:
            self.energy_dict["channel"] = item.channel_type
            self.energy_dict["cost"] = item.cost
            self.energy_dict["descriptor"] = item.descriptor
            self.energy_dict["duration"] = item.duration
            self.energy_dict["nem_time"] = item.nem_time
            self.energy_dict["kwh"] = item.kwh
            self.energy_dict["per_kwh"] = item.per_kwh
            self.energy_dict["quality"] = item.quality
            self.energy_dict["renewable"] = item.renewables
