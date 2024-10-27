import psycopg2
import os
from utils.amber_utils import EnergyUsage
from psycopg2.extras import execute_values

username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST", "localhost")
database = "amber"


def connect():
    connection = psycopg2.connect(
        database="amber", user=username, password=password, host=host, port="5432"
    )
    connection.autocommit = True
    return connection


def insert_into_usage_table(energy_list: list[EnergyUsage]):
    with connect().cursor() as cursor:
        execute_values(
            cur=cursor,
            sql="INSERT INTO amber_usage VALUES %s",
            argslist=[
                (
                    energy["energy_type"],
                    energy["duration"],
                    energy["spot_per_kwh"],
                    energy["per_kwh"],
                    energy["date"],
                    energy["nem_time"],
                    energy["start_time"],
                    energy["end_time"],
                    energy["renewables"],
                    energy["channel_type"],
                    energy["spike_status"],
                    energy["descriptor"],
                    energy["channel_identifier"],
                    energy["kwh"],
                    energy["quality"],
                    energy["energy_cost"],
                )
                for energy in energy_list
            ],
        )
