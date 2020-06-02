import asyncio
import json
from typing import Dict
import yaml

from ../db import queries as q
from .grubhub import GrubHubScraper
from ../browser/chrome import HeadlessChrome


class ScraperRunner:

    CLASS_MAP = {
        "grubhub": {
            "_class": GrubHubScraper,
            "init": self.get_grubhub_token,
            "refresh": self.get_grubhub_token,
        },
    }

    def __init__(self, config):
        self._parse_config(config)
        self.browser = HeadlessChrome()
        self.tasks = []

    def _parse_config(self, config_fp):
        with open(config_fp) as fp:
            conf = yaml.load(fp)
            self.db_pool = await self._parse_db(conf)
            self.scrapers = await self._get_scrapers(conf)

    async def _parse_db(self, conf):
        _dsn = conf["db"]["dsn"]
        async with aiopg.create_pool(_dsn) as pool:
            return await pool

    async def _get_scrapers(self, config):
        scrapers = dict()
        for scraper_type, num in conf['scrapers'].items():
            scraper_definition = self.CLASS_MAP.get(scraper_type, None):
                if scraper_definition is None:
                    raise Exception(f"Invalid scraper_type: '{scraper_type}'")

                scrapers[scraper_type] = scraper_definition.update({
                    "num": num,
                    "active_searches": set(),
                })
        return scrapers

    def _reload(self):
        self.browser.close()
        self.browser = HeadlessChrome()

    async def start(self):
        for scraper_type in self.scrapers.keys():
            scraper_def = self.scrapers[scraper_type]
            scraper_cls = scraper_def["_class"]
            payload = scraper_def.get("init", dict())

            for i in range(scraper_def["num"]):
                if payload:
                    payload = payload()

                self.scrapers[scraper_type]["scrapers"].append(
                    scraper_cls(**payload)
                )

    async def run(self):
        await self.start()
        await self._run()

    async def get_search_string(self, scraper_type):
        async with self.pool.acquire() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    q.QUERY_SEARCH_STRING,
                    (
                        tuple(self.scrapers[scraper_type]["active_searches"]),
                        scraper_type,
                    )
                )
                return await cur.fetchone()

    async def _run(self):
        for scraper_type in self.scrapers.keys():
            for i in range(self.scrapers[scraper_type]["scrapers"]):

                if not self.scrapers[scraper_type]["scrapers"][i].is_valid():
                    # refactor to separate func.
                    _ = self.scrapers[scraper_type]["scrapers"].pop(i)
                    payload = self.scrapers[scraper_type].get("refresh", dict())
                    if payload:
                        payload = payload()

                    self.scrapers[scraper_type]["scrapers"].append(
                        self.scrapers[scraper_type]["_class"](**payload)
                    )
                # get relevant (longitude, latitude) to search.
                # add (longitude, latitude) to active_searches. 
                # scraper.search()
                # save results to DB.
                search_string = await self.get_search_string(self, scraper_type)
                task = asyncio.create_task(
                    self._run_scraper(
                        self.scrapers[scraper_type]["scrapers"][i],
                        search_string
                    )
                )
                self.tasks.append(task)

        await asyncio.gather(self.*tasks)

    async def _run_scraper(self, scraper, search_string):
        self.scrapers[scraper_type]["active_searches"].add(search_string)
        async with scraper() as session:
            return await scraper.search(search_string)

    def get_grubhub_token(self) -> Dict[str, str]:
        self.browser.get(GrubHubScraper.auth_page)
        logs = browser.get_log("performance")

        auth = None
        for l in logs:
            if "/auth" in str(l):
                auth = json.loads(l)
                break

        auth_message = json.loads(auth)

        # Selenium's requestId.
        request_id = auth_message["message"]["params"]["requestId"]

        # Grab the network response payload
        browser_response = browser.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})

        response = json.loads(browser_response["body"])
        session_handle = response["session_handle"]
        self._reload()
        return session_handle

# move this to main
if __name__ == "__main__":
