import json

from collections import DefaultDict
from .grubhub import GrubHubScraper
from ../selenium/chrome import HeadlessChrome


class ScraperRunner:

    TOKEN_MAP = {
        GrubHubScraper: self.get_grubhub_token,
    }

    def __init__(self, config):
        self.browser = HeadlessChrome()
        self.scrapers = dict()
        for scraper_type, num in config.items():
            scrapers[scraper_type] = {
                "num": num,
                "active_searches": set(),
                "scrapers": [],
            }

    def start(self):
        for scraper_type in self.scrapers.keys():
            sc = self.scrapers[scraper_type]
            starting_func = self.START_MAP.get(scraper_type)

            for i in range(sc["num"]):
                payload = {}
                if starting_func:
                    payload = starting_func()

                self.scrapers[scraper_type]["scrapers"].append(
                    scraper_type(**payload)
                )

    def run(self):
        self.start()
        self._run()

    def _run(self):

        # refactor to async
        for scraper_type in self.scrapers:
            for scraper in self.scrapers[scraper_type]:

                if not scraper.is_valid():
                    refresh_func = self.TOKEN_MAP[scraper_type]
                    payload = refresh_func()
                    self.scraper.refresh(payload)

                # get relevant (longitude, latitude) to search.
                # add (longitude, latitude) to active_searches. 
                # scraper.search()
                # save results to DB.


    def get_grubhub_token(self):
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

        return session_handle

# move this to main
if __name__ == "__main__":
