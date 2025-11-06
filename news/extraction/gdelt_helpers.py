import json
import datetime as dt
import calendar
from pathlib import Path
import csv

BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc?query="

RAW_NEWS = "news/gdelt/data/gdelt_raw.csv"
BLACKLIST_URLS = "news/gdelt/json/blacklisted.json"

COLUMNS = [
    "url",
    "oficial_url",
    "title",
    "seendate",
    "domain",
    "language",
    "sourcecountry",
]


# -----
# Files
# -----
def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        file = json.load(f)

    return file


def write_json(path, content):
    with open(path, "w") as f:
        json.dump(content, f, indent=4)


# ---------
# URL STUFF
# ---------
def gen_queries(pairs: list[tuple]) -> list:
    """
    Works with `pairs` to create the "query string"
    for each pair of (domain, theme)

    Query structure:

    - domain
    - theme
    """
    queries = list()
    for pair in pairs:
        query = f"%20domainis:{pair[0]}%20theme:{pair[1]}"
        queries.append(query)

    return queries


def _get_date_range(start_date, end_date):
    """
    Return a list of (start_raw, end_raw) monthly ranges between start_date and end_date.
    """
    start = dt.datetime.strptime(start_date, "%Y%m%d").date()
    end = dt.datetime.strptime(end_date, "%Y%m%d").date()

    dates = []
    # jump to the first day of the start month
    current = start.replace(day=1)

    while current <= end:
        # month boundaries
        last_day = calendar.monthrange(current.year, current.month)[1]
        m_start = current
        m_end = dt.date(current.year, current.month, last_day)

        # clamp to requested range
        rng_start = max(m_start, start)
        rng_end = min(m_end, end)

        # convert to datetimes and raw strings
        s_dt = dt.datetime.combine(rng_start, dt.time(0, 0, 0))
        e_dt = dt.datetime.combine(rng_end, dt.time(23, 59, 59))
        dates.append((s_dt.strftime("%Y%m%d%H%M%S"), e_dt.strftime("%Y%m%d%H%M%S")))

        # advance to first day of next month
        if current.month == 12:
            current = dt.date(current.year + 1, 1, 1)
        else:
            current = dt.date(current.year, current.month + 1, 1)

    return dates


def gen_urls(queries, start_date, end_date, sort, format):
    dates = _get_date_range(start_date, end_date)

    urls = list()

    for date in dates:
        for query in queries:
            params = f"{query}&startdatetime={date[0]}&enddatetime={date[1]}&sort={sort}&format={format}"
            urls.append(BASE_URL + params)

    print(f"Total de URLS generadas: {len(urls)}")
    return urls


# ----------------
# FETCHING HELPERS
# ----------------
def to_blacklist(url):
    data = read_json(BLACKLIST_URLS)

    if url not in data["urls"]:
        data["urls"].append(url)

    write_json(BLACKLIST_URLS, data)


def url_to_df(url, res):
    resp = json.loads(res)

    articles = resp.get("articles", [])

    p = Path(RAW_NEWS)
    p.parent.mkdir(parents=True, exist_ok=True)
    file_exists = p.exists()

    with p.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        if not file_exists:
            writer.writeheader()

        for art in articles:
            row = {
                "title": art.get("title", ""),
                "seendate": art.get("seendate", ""),
                "domain": art.get("domain", ""),
                "language": art.get("language", ""),
                "sourcecountry": art.get("sourcecountry", ""),
                "url": url,
                "oficial_url": art.get("url", ""),
            }
            writer.writerow(row)

