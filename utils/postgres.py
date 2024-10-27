import psycopg2
import os
from utils.amber_utils import EnergyUsage
from psycopg2.extensions import AsIs


username = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
host = os.getenv("POSTGRES_HOST", "localhost")


def connect():
    return psycopg2.connect(
        database="amber", user=username, password=password, host=host, port="5432"
    )


def insert_into_usage_table(energy_use: EnergyUsage):
    conn = connect()
    cursor = conn.cursor()

    columns = energy_use.keys()
    values = energy_use.values()

    query = "INSERT INTO amber_usage (%s) VALUES (%s)"
    values = [tuple(value) for value in values]
    formatted_query = cursor.mogrify(query, (AsIs(",".join(columns)), tuple(values)))
    print(formatted_query)
    cursor.execute(formatted_query)
    conn.commit()
    conn.close()
