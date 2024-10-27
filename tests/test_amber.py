from dotenv import load_dotenv
import os
from amberelectric.models.usage import Usage
from amberelectric.models.channel_type import ChannelType
from amberelectric.models.spike_status import SpikeStatus
from amberelectric.models.price_descriptor import PriceDescriptor
from utils.amber_utils import Amber
import pytest
import datetime

load_dotenv()

test_site_id = os.getenv("SITE_ID")
amber_key = os.getenv("AMBER_KEY")


@pytest.fixture
def amber_obj() -> Amber:
    return Amber()


def test_str_site_id():
    assert isinstance(test_site_id, str)


def test_str_amber_key():
    assert isinstance(amber_key, str)


def test_unwrap_usage(amber_obj: Amber):
    data = [
        Usage(
            type="Usage",
            duration=30,
            spot_per_kwh=10.82936,
            per_kwh=21.95831,
            var_date=datetime.date(2024, 10, 25),
            nem_time=datetime.datetime(2024, 10, 25, 0, 30),
            start_time=datetime.datetime(
                2024, 10, 24, 14, 0, 1, tzinfo=datetime.timezone.utc
            ),
            end_time=datetime.datetime(
                2024, 10, 24, 14, 30, tzinfo=datetime.timezone.utc
            ),
            renewables=31.671,
            channel_type=ChannelType.GENERAL,
            spike_status=SpikeStatus.NONE,
            descriptor=PriceDescriptor.VERYLOW,
            channel_identifier="E1",
            kwh=0.069,
            quality="billable",
            cost=1.5151,
        )
    ]
    energy_dict = amber_obj.unwrap_usage(data)
    assert energy_dict == {
        "energy_type": ["Usage"],
        "duration": [30],
        "spot_per_kwh": [10.82936],
        "per_kwh": [21.95831],
        "date": [datetime.date(2024, 10, 25)],
        "nem_time": [datetime.datetime(2024, 10, 25, 0, 30)],
        "start_time": [
            datetime.datetime(2024, 10, 24, 14, 0, 1, tzinfo=datetime.timezone.utc)
        ],
        "end_time": [
            datetime.datetime(2024, 10, 24, 14, 30, tzinfo=datetime.timezone.utc)
        ],
        "renewables": [31.671],
        "channel_type": ["general"],
        "spike_status": ["none"],
        "descriptor": ["veryLow"],
        "channel_identifier": ["E1"],
        "kwh": [0.069],
        "quality": ["billable"],
        "energy_cost": [1.5151],
    }
