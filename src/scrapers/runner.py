import asyncio
import json
from typing import Dict
import yaml

from proxyscrape import create_collector

from src.db.conn import get_async_conn
from src.browser.chrome import HeadlessChrome
from src.scrapers import GrubHubScraper


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
        self.browser = HeadlessChrome(proxy=self.proxy_collector.get_proxy())
        self.tasks = []

    def _parse_config(self, config_fp):
        with open(config_fp) as fp:
            conf = yaml.load(fp)
            self.db = self._parse_db(conf)
            self.scrapers = self._get_scrapers(conf)
            self.proxy_collector = self._get_proxy_collector(conf)
    
    def _get_proxy_collector(self, conf):
        name, proxy_types = conf["proxies"]["name"], conf["proxies"]["type"]
        collector = create_collector(name, proxy_types)
        collector.refresh_proxies(force=True)
        return collector

    async def _parse_db(self, conf):
        dsn = conf["db"]["dsn"]
        return await get_async_conn(
            dsn
        )

    async def _get_scrapers(self, conf):
        scrapers = dict()
        for scraper_type, num in conf["scrapers"].items():
            scraper_definition = self.CLASS_MAP.get(scraper_type, None)
            if scraper_definition is None:
                raise Exception(f"Invalid scraper_type: '{scraper_type}'")

                scrapers[scraper_type] = scraper_definition.update({
                    "active_searches": set(),
                    "proxies": [None for i in range(num)],
                    "scrapers": [None for i in range(num)],
                })
        return scrapers

    def _get_proxy(self):
        return self.proxy_collector.get_proxy({
            "anonymous": True,
            # currently only US.
            "code": "us",
        })

    def _reload_browser(self):
        self.browser.close()
        self.browser = HeadlessChrome(proxy=self.proxy_collector.get_proxy())

    async def _start(self):
        for scraper_type in self.scrapers.keys():
            scraper_def = self.scrapers[scraper_type]
            scraper_cls = scraper_def["_class"]
            payload = scraper_def.get("init", dict())

            for i in range(len(scraper_def["scrapers"])):
                if payload:
                    payload = payload()
                self.scrapers[scraper_type]["scrapers"][i] = scraper_cls(**payload)
                self.scrapers[scraper_type]["proxies"][i] = self._get_proxy()

    async def run(self):
        await self._start()
        await self._run()

    async def get_search_string(self, scraper_type):
        return await self.db.fetchrow(
            q.QUERY_SEARCH_STRING,
            (
                tuple(self.scrapers[scraper_type]["active_searches"]),
                scraper_type,
            )
        )

    async def _refresh_invalid_scraper(self, scraper_type, scraper_index):
        self.scrapers[scraper_type]["scrapers"][scraper_index] = None
        payload = self.scrapers[scraper_type].get("refresh", dict())
        if payload:
            payload = payload()

        self.scrapers[scraper_type]["scrapers"].append(
            self.scrapers[scraper_type]["_class"](**payload)
        )

    async def _run(self):
        for scraper_type in self.scrapers.keys():
            for i in range(len(self.scrapers[scraper_type]["scrapers"])):

                if not self.scrapers[scraper_type]["scrapers"][i].is_valid():
                    self._refresh_invalid_scraper(scraper_type, i)

                # get relevant (longitude, latitude) to search.
                # add (longitude, latitude) to active_searches. 
                # scraper.search()
                # save results to DB.
                search_string = self.get_search_string(self, scraper_type)
                task = asyncio.create_task(
                    self._run_scraper(
                        scraper_type,
                        self.scrapers[scraper_type]["scrapers"][i],
                        self.scrapers[scraper_type]["proxies"][i],
                        search_string,
                    )
                )
                self.tasks.append(task)

        await asyncio.gather(*self.tasks)

    async def _run_scraper(self, scraper_type, scraper, proxy, search_string):
        self.scrapers[scraper_type]["active_searches"].add(search_string)
        async with scraper(proxy) as scraper_session:
            return await scraper_session.search(search_string)

    def get_grubhub_token(self) -> Dict[str, str]:
        self.browser.get(GrubHubScraper.auth_page)
        logs = self.browser.get_log("performance")

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
        self._reload_browser()
        return session_handle