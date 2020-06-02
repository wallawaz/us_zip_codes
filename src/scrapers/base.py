import asyncio
import random
from typing import List, Optional

from aiohttp import ClientSession, ClientResponse
from aiohttp.hdrs import METH_GET

from .user_agents import USER_AGENTS


class BaseScraper(ClientSession):
    def __init__(
        self,
        user_agents: Optional[List[str]] = None,
        use_random_user_agent: bool = True,
        *args,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.use_random_user_agent = use_random_user_agent or bool(self.user_agents)
        self.user_agents = user_agents
        if self.user_agents is None and use_random_user_agent:
            self.user_agents = USER_AGENTS


    async def get_json(self, url: str, **kwargs) -> dict:
        return await (
            await self._request(
                METH_GET,
                url,
                json=True,
                mime_type="application/json",
                **kwargs,
            )
        ).json()

    async def get_html(self, url: str, **kwargs) -> str:
        return await (
            await self._request(METH_GET, url, mime_type="text/html", **kwargs)
        ).text()

    async def search(self):
        raise NotImplementedError

    async def _request(
        self,
        *args,
        retries: int = 3,
        start_delay: float = 15.0,
        json: bool = False,
        mime_type: Optional[str] = None,
        **kwargs,
    ) -> ClientResponse:

        attempts = 0
        stats = []
        while retries > 0:
            if self.use_random_user_agent:
                kwargs.get("headers", dict())["user-agent"] = random.choice(
                    self.user_agents
                )
            try:
                # call aiohttp request
                resp = await super()._request(*args, **kwargs)

                if not 200 <= resp.status < 300:
                    raise Unsuccessful(f"Unsuccessful: status code: {resp.status}")

                if mime_type:
                    resp_mime_type = resp.headers.get("content-type", "")
                    resp_mime_match = mime_type.lower() in resp_mime_type.lower()

                    if not resp_mime_match:
                        raise Unsuccessful(
                            f"MIME mismatch. (Expected '{mime_type}', got '{resp_mime_type}')"
                        )
                if json:
                    try:
                        await resp.json()
                    except Exception as ex:
                        raise Unsuccessful(f"Cannot parse JSON: {ex}")
                return resp

            except Exception as ex:
                stats.append(str(ex))
                retries -= 1

                if retries > 0:
                    if not attempts:
                        delay = start_delay
                    else:
                        delay = min(2 ** attempts)

                    time_perc = delay * 0.2 // 1
                    delay += random.randint(-1 * time_perc, time_perc)

                    await asyncio.sleep(delay)

                    attempts += 1

        raise AllRetriesFailed(str(stats))
