import asyncio

from env import require_env
from log import log
from myPyllant.api import MyPyllantAPI


class Fetcher:
    def __init__(self):
        self.user = require_env("VAILLANT_USER")
        self.password = require_env("VAILLANT_PASSWORD")
        self.brand = "vaillant"
        self.country = "unitedkingdom"

    def fetch(self):
        return asyncio.run(self._fetch())

    async def _fetch(self):
        async with MyPyllantAPI(self.user, self.password, self.brand, self.country) as api:
            log("Fetching system from API")
            async for system in api.get_systems():
                return system
