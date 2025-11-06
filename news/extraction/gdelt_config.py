"""
This class will return the necessary
data to start with requests building.
"""

import pandas as pd
from gdelt_helpers import read_json
import sys

RAW_NEWS = "news/gdelt/data/gdelt_raw.csv"
CONFIG_PARAMS = "news/gdelt/json/params.json"


def load_saved_urls():
    """
    Load previously fetched request URLs from the raw-news CSV.

    - If the CSV does not exist or is empty, leaves `saved_urls` empty.
    - If it exists, reads the 'url' column.

    Returns:
        int: Number of unique saved URLs loaded into memory.
    """
    try:
        saved_urls = list()  # Empty init list

        print(f">> Looking for data in {RAW_NEWS}")
        df = pd.read_csv(RAW_NEWS)
    except FileNotFoundError:
        print(">> CSV file not found. Starting fresh.")
        saved_urls = []
    else:
        saved_urls = list(df["url"])
        print(f">> Loaded {len(saved_urls):,} saved URLs")
    return saved_urls

def load_params() -> dict:
    """
    Loads GDELT pipeline settings from `json/params.json`.

    Expected JSON shape:
        {
            "zones": { "country": ["domain1", "domain2", ...], ... },
            "themes": ["ECONOMY", "POLITICS", ...],
            "dates": { "start": "YYYYMMDD", "end": "YYYYMMDD" },
            "sort": "date|relevance|...",
            "fmt": "json|csv"
        }

    Returns:
        dict: {
            "zones": dict[str, list[str]],
            "themes": list[str],
            "start": str,
            "end": str,
            "sort": str,
            "fmt": str,
        }
    """
    path = CONFIG_PARAMS

    print(f">> Loading params from: {path}")
    try:
        cfg = read_json(path)
        zones = cfg["zones"]
        themes = cfg["themes"]
        start  = cfg["dates"]["start"]
        end    = cfg["dates"]["end"]
        sort   = cfg["sort"]
        fmt    = cfg["fmt"]
    except FileNotFoundError:
        print(f">> Params file not found: {path}")
        print("Create the params file and try again.")
        sys.exit(1)
    except KeyError as e:
        print(f">> Missing key in params.json: {e}")
        sys.exit(1)
    else:
        total_domains = sum(len(v) for v in zones.values())
        print(
            f">> Params OK — zones: {len(zones)}, domains: {total_domains}, "
            f"themes: {len(themes)}, date range: {start} → {end}, sort: {sort}, fmt: {fmt}"
        )
        return {
            "zones": zones,
            "themes": themes,
            "start": start,
            "end": end,
            "sort": sort,
            "fmt": fmt,
        }


