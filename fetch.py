# /// script
# requires-python = ">=3.10"
# dependencies = ["requests"]
# ///

"""Fetch one year of daily Hong Kong rainfall and cache the raw JSON reply.

Run once with:

    uv run fetch.py
"""

from pathlib import Path

import requests


URL = (
    "https://archive-api.open-meteo.com/v1/archive"
    "?latitude=22.3193&longitude=114.1694"
    "&start_date=2025-01-01&end_date=2025-12-31"
    "&daily=precipitation_sum&timezone=Asia%2FHong_Kong"
)
FILE = "open-meteo-hong-kong-daily-rainfall-2025.json"

HERE = Path(__file__).parent
DATA = HERE / "data"


def fetch(url, path):
    """Fetch a published file once; keep the existing cached copy thereafter."""
    if path.exists():
        print(
            f"data/{path.name} is already here "
            f"({path.stat().st_size // 1024} KB); nothing was downloaded."
        )
        return path

    DATA.mkdir(exist_ok=True)
    print(f"requesting {url}")
    reply = requests.get(
        url,
        timeout=60,
        headers={"User-Agent": "SD5913 student data-visualisation assignment"},
    )
    reply.raise_for_status()
    path.write_bytes(reply.content)
    print(f"saved data/{path.name} ({path.stat().st_size // 1024} KB)")
    return path


if __name__ == "__main__":
    fetch(URL, DATA / FILE)

