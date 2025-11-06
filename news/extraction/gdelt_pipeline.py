
from itertools import product
import requests
import sys
import time
import datetime as dt

from gdelt_config import load_saved_urls, load_params
from gdelt_helpers import read_json, write_json, gen_queries, gen_urls, to_blacklist, url_to_df

GENERATED_URLS = "news/gdelt/json/generated_urls.json"
BLACKLISTED_URLS = "news/gdelt/json/blacklisted.json"

class GDELT:

    def __init__(self, to_wait = 2):
        # Config
        self.zones = {}
        self.themes = []
        self.start_date = ''
        self.end_date = ''
        self.sort = ''
        self.fmt = ''
        
        # Execution must
        self.df_saved_urls = []
        self.to_fetch = [] # _verify_urls
        self.to_wait = to_wait

    def _verify_urls(self):
        final_urls = list()

        blacklisted = 0
        df_saved = 0

        generated_urls = read_json(GENERATED_URLS) #{country: [urls]}
        blacklisted_urls = read_json(BLACKLISTED_URLS)['urls']

        for _, urls in generated_urls.items():
            for url in urls:
                if not (url in self.df_saved_urls or url in blacklisted_urls):
                    final_urls.append(url)
                elif url in blacklisted_urls:
                    blacklisted += 1
                else:
                    df_saved += 1

        print(f'Not considering {blacklisted} urls from BLACKLISTED and {df_saved} ALREADY fetched.')

        self.to_fetch = final_urls
                
    def build_requests(self):
        """
        Build GDELT API request URLs based on the configuration in `params.json`.

        A GDELT API URL is composed of:
        - Base path
        - Query section: built from combinations of domains and themes
        - Other parameters: date range, format, sort order, etc.

        Steps performed:
        1. For each country/region in the config, generate all possible (domain, theme) pairs.
        2. Construct query strings from these pairs.
        3. Generate full GDELT API URLs, including additional parameters such as date range, format, and sort order.
        4. Save all generated URLs to `news/json/config_urls.json`.

        Example:
            Suppose `params.json` contains:
            {
                "zones": {
                    "mexico": ["elfinanciero.com.mx", "milenio.com"],
                    "usa": ["nytimes.com"]
                },
                "themes": ["ECONOMY", "POLITICS"],
                "dates": {
                    "start": "2025-01-01",
                    "end": "2025-01-31"
                },
                "sort": "date",
                "fmt": "json"
            }

            - For "mexico", all (domain, theme) pairs are generated:
                [("elfinanciero.com.mx", "ECONOMY"), ("elfinanciero.com.mx", "POLITICS"),
                ("milenio.com", "ECONOMY"), ("milenio.com", "POLITICS")]

            - Each pair becomes part of a query string, which is then combined with
            the base path, date range, format, and sort order to form full URLs.

            - The final output is saved as a dictionary of country → list of URLs
            in `news/json/config_urls.json`.

        Reference:
            https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
        """

        to_save = dict()

        try:
            for country, domains in self.zones.items():
                # Generar pares de dominio-tema
                pairs = product(domains, self.themes)

                # Generar la parte del query de la url
                queries = gen_queries(pairs)

                # Generar la url completa
                urls = gen_urls(
                    queries, self.start_date, self.end_date, self.sort, self.fmt
                )

                to_save[country] = urls
        except Exception as e:
            print(f"Error preparing requests: {e}")
        else:
            write_json(GENERATED_URLS, to_save)

            print("Urls generated from Params file saved successfully!")

    def fetch(self):
        try:
            print(f'='*60)
            print('*'*20, "FETCHING GDELT API", '*'*20)
            print(f'>> Cleaning generated urls')
            self._verify_urls()
            print(f'>> Total urls to fetch: {len(self.to_fetch)}')
            total_seconds = len(self.to_fetch) * self.to_wait
            print(f'>> Estimated time: {dt.timedelta(seconds=total_seconds)}')
            print(f'='*60)

            count_to_fetch = len(self.to_fetch)
            count_progress = 1

            for url in self.to_fetch:
                print(f'>>> {count_progress}/{count_to_fetch} <<<')
                res = requests.get(url, timeout=10)

                status_code = res.status_code
                if status_code == 429:
                    print(f"{'*'*10} Too many requests {status_code}, aborting. {'*'*10}")
                    sys.exit(1)
                elif res.text == "{}":
                    print(f"{'*'*10} Empty URL, saved to blacklist {'*'*10}")
                    to_blacklist(url)
                elif res.ok:
                    print(f'{'*'*10} URL fetched and containing data, saving to df {'*'*10}')
                    url_to_df(url, res.text)
                else:
                    print(f'>>> HTTP error {status_code} <<<')
                
                count_progress += 1
                time.sleep(self.to_wait)
        except Exception as e:
            print(f'Unexpected error fetching {e}')
            sys.exit(1)
        finally:
            print('DONE')

    def start_pipeline(self):
        self.df_saved_urls = load_saved_urls()

        params = load_params()
        self.zones = params['zones']
        self.themes = params['themes']
        self.start_date = params['start']
        self.end_date = params['end']
        self.sort = params['sort']
        self.fmt = params['fmt']

        self.build_requests()

        self.fetch()



gdelt = GDELT()
gdelt.start_pipeline()
