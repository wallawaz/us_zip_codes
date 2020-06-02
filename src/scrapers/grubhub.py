from datetime import datetime
from typing import Dict, List, Tuple

from .base import BaseScraper


class GrubHubScraper(BaseScraper):

    auth_page = "https://www.grubhub.com"
    search_page = "https://api-gtm.grubhub.com/restaurants/search/search_listing"

    @staticmethod
    def _get_headers(api_key:str) -> Dict[str, str]:
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        for api_key in ("token_expire_time", "access_token", "browser"):
            api_value = kwargs.get(api_key, None)
            if api_value is None:
                raise Exception(f"{api_key} needed for GrubHubScraper")
            setattr(self, api_key, api_value)

        self.token_expire_time = self.timestamp_from_epoch_milliseconds(
            self.token_expire_time
        )
        kwargs.get("headers", dict()).update(self._get_headers(self.api_key))

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

    async def search(
        self,
        longitude: str,
        latitude: str,
        page_size: int=20,
        page_num: int=0
    ) -> Tuple[List[Dict[str, str]], bool]:
        params = [
            ('orderMethod', 'delivery'),
            ('locationMode', 'DELIVERY'),
            ('facetSet', 'umamiV2'),
            ('pageSize', f'{page_size}'),
            ('hideHateos', 'true'),
            ('searchMetrics', 'true'),
            ('location', f'POINT({longitude} {latitude})'),
            ('preciseLocation', 'true'),
            ('sortSetId', 'umamiv3'),
            ('countOmittingTimes', 'true'),
        ]
        if page_num > 0:
            params.append(('pageNum', f'{page_num}'))

        resp = self.get_json(self.search_page)

        results = content['results']
        pager = content['pager']
        return (
            content['results'],
            pager['total_pages'] == pager['current_page']
        )
