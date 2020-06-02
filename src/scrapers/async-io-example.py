from aiohttp import ClientSession
import asyncio
from timeit import default_timer

grub_hub_headers = {
    ':authority': 'api-gtm.grubhub.com',
    ':method': 'POST',
    ':path': '/auth',
    ':scheme': 'https',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US',
    'authorization': 'Bearer',
    'content-length': '109',
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://www.grubhub.com',
    'referer': 'https://www.grubhub.com/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/81.0.4044.138 Safari/537.36'
}
default_headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/81.0.4044.138 Safari/537.36'
}

RESPONSES = dict()

async def fetch_all(urls):
    tasks = []
    async with ClientSession(headers=default_headers) as session:
    #async with ClientSession(headers=headers) as session:
        for method, url in urls:
            task = asyncio.create_task(fetch(method, url, session))
            tasks.append(task)
        all_done = await asyncio.gather(*tasks)
        return all_done

async def fetch(method, url, session):
    if method == "get":
        async with session.get(url) as response:
            resp = await response.read()
            RESPONSES[url] = resp
            return resp

    elif method == "post":
        async with session.post(url) as response:
            resp = await response.read()
            RESPONSES[url] = resp
            return resp

def main():
    urls = [
        ("get", "https://google.com"),
        ("get", "https://theguardian.com/us"),
        #("post", "https://api-gtm.grubhub.com"),
    ]
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(fetch_all(urls))
    loop.run_until_complete(future)

    return future

x = main()
import pdb; pdb.set_trace()
