from datetime import datetime
from typing import Dict, List, Tuple

from .base import BaseScraper


class GrubHubScraper(BaseScraper):

    auth_page = "https://www.grubhub.com"
    search_page = "https://api-gtm.grubhub.com/restaurants/search/search_listing"

    @staticmethod
    def _get_headers(api_key: str) -> Dict[str, str]:
        return {
            'authority': 'api-gtm.grubhub.com',
            'cache-control': 'max-age=0',
            'accept': 'application/json',
            'authorization': f'Bearer {api_key}',
            'if-modified-since': '0',
            'origin': 'https://www.grubhub.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept-language': 'en-US,en;q=0.9',
        }

    def __init__(self, access_token, token_expire_time, *args, **kwargs):
        self.access_token = access_token
        self.token_expire_time = token_expire_time
        super().__init__(*args, **kwargs)

        self.token_expire_time = self.timestamp_from_epoch_milliseconds(
            self.token_expire_time
        )
        kwargs.get("headers", dict()).update(self._get_headers(self.access_token))


    def timestamp_from_epoch_milliseconds(self, ts: int) -> datetime:
        return datetime.fromtimestamp(ts // 1000)

    @property
    def is_valid(self) -> bool:
        datetime.now() <= self.token_expire_time

    def refresh(self, **kwargs):
        self.access_token = kwargs["access_token"]
        self.token_expire_time = self.timestamp_from_epoch_milliseconds(
            kwargs["token_expire_time"]
        )
        # TODO fix
        #self.session.headers.update(
        #    self._get_headers(kwargs["access_token"])
        #)


    async def _search(self, headers, longitude, latitude, page_num, page_size):
        params = self._get_params(longitude, latitude, page_num, page_size)
        return await self.get_json(
            self.search_page,
            headers=headers,
            params=params
        )
    
    def _get_params(self, longitude, latitude, page_num, page_size):
        params = [
            ('orderMethod', 'delivery'),
            ('locationMode', 'DELIVERY'),
            ('facetSet', 'umamiV2'),
            ('pageSize', f'{page_size}'),
            ('hideHateos', 'true'),
            ('searchMetrics', 'true'),
            ('location', f'POINT({longitude}%20{latitude})'),
            ('preciseLocation', 'true'),
            ('sortSetId', 'umamiv3'),
            ('countOmittingTimes', 'true'),
        ]
        if page_num > 0:
            params.append(('pageNum', f'{page_num}'))
        return params

    async def search(
        self,
        longitude: str,
        latitude: str,
        page_size: int=20,
        page_num: int=0
    ) -> List[Dict[str,str]]:

        headers = self._get_headers(self.access_token)
        complete = False
        search_results = []
        while not complete:
            resp = await self._search(headers, longitude, latitude, page_num, page_size)

            search_results += resp.get("results", [])
            pager = resp.get("pager", None)
            
            if pager is None:
                break
            print(f"grabbed: {len(resp.get('results', []))}, pager: {pager}")

            complete = pager['total_pages'] == pager['current_page']
            page_num += 1
            self.random_sleep()

        return search_results