import logging

from datetime import datetime
from .base import BaseScraper


logger = logging.getLogger()


class GrubHubScraper(BaseScraper):

    auth_page = "https://www.grubhub.com"
    search_page = "https://api-gtm.grubhub.com/restaurants/search/search_listing"

    def _get_headers(self, api_key):
        return {
            'authority': 'api-gtm.grubhub.com',
            'cache-control': 'max-age=0',
            'accept': 'application/json',
            'authorization': f'Bearer {api_key}',
            'if-modified-since': '0',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36 Edg/83.0.478.37',
            'origin': 'https://www.grubhub.com',
            'sec-fetch-site': 'same-site',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept-language': 'en-US,en;q=0.9',
        }

    def __init__(self, **kwargs):
        super().__init__(search_page, **kwargs)

        for api_key in ("token_expire_time", "access_token", "browser"):
            api_value = kwargs.get(api_key, None)
            if api_value is None:
                raise Exception(f"{api_key} needed for GrubHubScraper")
            setattr(self, api_key, api_value)
        self.token_expire_time = self.timestamp_from_epoch_milliseconds(
            self.token_expire_time
        )
        # TODO change to aiohttp
        self.session = Session()
        self.session.headers.update(
            self._get_headers(self.api_key)
        )

    def timestamp_from_epoch_milliseconds(self, ts):
        return datetime.fromtimestamp(ts // 1000)

    @property
    def is_valid(self):
        datetime.now() <= self.token_expire_time

    def refresh(self, **kwargs):
        self.access_token = kwargs["access_token"]
        self.token_expire_time = self.timestamp_from_epoch_milliseconds(
            kwargs["token_expire_time"]
        )
        self.session.headers.update(
            self._get_headers(kwargs["access_token"])
        )

    def search(self, longitude, latitude, page_size=20, page_num=0):
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
        try:
            resp = self.session.get(self.search_page)
        except Exception as ex:
            print(str(ex))
            logger.error(ex)

        content = json.loads(resp.content)

        results = content['results']
        pager = content['pager']
        return (
            content['results'],
            pager['total_pages'] == pager['current_page']
        )
