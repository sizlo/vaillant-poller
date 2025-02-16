import asyncio
import datetime
import sys
import traceback

from env import require_env
from log import log
from myPyllant.api import MyPyllantAPI, DeviceDataBucketResolution


class Fetcher:
    def __init__(self, now):
        self.user = require_env("VAILLANT_USER")
        self.password = require_env("VAILLANT_PASSWORD")
        self.brand = "vaillant"
        self.country = "unitedkingdom"
        self.now = now

    def fetch(self):
        return asyncio.run(self._fetch())

    async def _fetch(self):
        async with MyPyllantAPI(self.user, self.password, self.brand, self.country) as api:
            log("Fetching system from API")
            async for system in api.get_systems():
                log("Fetching consumption data from API")
                try:
                    data = [
                        d async for d in api.get_data_by_device(
                            system.devices[0], DeviceDataBucketResolution.HOUR, self.now - datetime.timedelta(hours=2), self.now
                        )
                    ]
                except:
                    print(f"Got error trying to fetch consumption data from API", file=sys.stderr)
                    traceback.print_exc()
                    data = None
                return system, data
