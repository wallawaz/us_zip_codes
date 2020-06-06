import asyncio
import json
import requests

import os
from time import time

from src.scrapers import GrubHubScraper as GH
from src.db.conn import get_async_conn
from src.db.queries.scraping_queries import QUERY_RANDOM_ZIPCODE


#TOKEN = os.getenv("TOKEN")
TOKEN="ac8dc280-9a01-4a28-8373-96a0e591dd32"
TOKEN_EXPIRE_TIME = time() + 1000000


async def main():
    db = await get_async_conn(
        user=os.getenv("DBUSER"),
        database=os.getenv("DBDATABASE"),
    )
    r = await db.fetchrow(QUERY_RANDOM_ZIPCODE)
    print(f"{r}")
    async with GH(access_token=TOKEN, token_expire_time=TOKEN_EXPIRE_TIME) as session:
        results = await session.search(r['longitude'], r['latitude'])

    await db.close()
    import ipdb; ipdb.set_trace()
    print(results[0])

if __name__ == "__main__":
    asyncio.run(main())