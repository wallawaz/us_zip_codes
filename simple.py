import json
import random
from typing import Dict, Tuple, List

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.browser.chrome import HeadlessChrome
from src.scrapers.exceptions import ChromeError
from src.scrapers import GrubHubScraper

import time

class SimpleRunner:
    def __init__(self):
        self.tasks = []
        self.browser = HeadlessChrome()
        self.token = self.get_grubhub_token()

    def get_grubhub_token(self) -> Dict[str, str]:
        self.browser.get(GrubHubScraper.auth_page)

        WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//button[@at-start-order-search-btn]"
            ))
        )
        time.sleep(2)

        logs = self.browser.get_log("performance")
        auth = None
        for l in logs:
            if "/auth" in str(l):
                auth = l
                break

        if not l:
            raise ChromeError

        auth_message = json.loads(auth["message"])

        # Selenium's requestId.
        request_id = auth_message["message"]["params"]["requestId"]

        # Grab the network response payload
        browser_response = self.browser.execute_cdp_cmd(
            "Network.getResponseBody", {"requestId": request_id}
        )

        response = json.loads(browser_response["body"])
        session_handle = response["session_handle"]
        return session_handle


    async def run_grubhub(self, search):
        search = {"longitude": search[0], "latitude": search[1]}
        with GrubHubScraper(**self.token) as sesssion:
            await asyncio.sleep(random.randint(1,5))
            return await session.search(**search)

    async def main():
        # long, lat
        seaches = [
            # 11222
            ("-73.94980", "40.72720"),
            # 91714
            ("-117.95870", "34.01970"),
            # 07436
            ("-74.23380", "41.02940"),
        ]

        for search in searches:
            task = asyncio.create_task(self.run_grubhub(search))
            self.tasks.append(task)

        responses = await asyncio.gather(*t)
        for res in responses:
            print(res)

if __name__ == "__main__":
    runner = SimpleRunner()
    runner.main()
