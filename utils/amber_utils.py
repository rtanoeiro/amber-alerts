import logging
import os

from amberelectric.exceptions import ApiException
from dotenv import load_dotenv
from amberelectric.api.amber_api import AmberApi
from amberelectric.configuration import Configuration
from amberelectric.api_client import ApiClient

load_dotenv()

AMBER_KEY = os.getenv("AMBER_KEY")
SITE_ID = os.getenv("SITE_ID")


class AmberSummary:
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
