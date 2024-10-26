from dotenv import load_dotenv
import os

load_dotenv()

test_site_id = os.getenv("SITE_ID")
amber_key = os.getenv("AMBER_KEY")


def test_str_site_id():
    assert isinstance(test_site_id, str)


def test_str_amber_key():
    assert isinstance(amber_key, str)
