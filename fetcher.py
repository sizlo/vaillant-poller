import asyncio
import datetime
import sys
import traceback

from cachetools import TTLCache
from myPyllant.api import MyPyllantAPI

from env import require_env
from log import log
from myPyllant.enums import DeviceDataBucketResolution

TWENTY_FOUR_HOURS_IN_SECONDS = 60 * 60 * 24


class Fetcher:
    def __init__(self):
        self.user = require_env("VAILLANT_USER")
        self.password = require_env("VAILLANT_PASSWORD")
        self.brand = "vaillant"
        self.country = "unitedkingdom"
        self.home_cache = TTLCache(maxsize=1, ttl=TWENTY_FOUR_HOURS_IN_SECONDS)

    def fetch_system(self):
        return asyncio.run(self._fetch_system())

    async def _fetch_system(self):
        async with MyPyllantAPI(self.user, self.password, self.brand, self.country) as api:
            home = await self._fetch_home(api)
            log("Fetching system from API")
            async for system in api.get_systems(homes=[home]):
                # This assumes there is only one system on the account
                return system

    def fetch_hourly_device_data_for_day(self, system, day):
        return asyncio.run(self._fetch_hourly_device_data_for_day(system, day))

    async def _fetch_hourly_device_data_for_day(self, system, day):
        start_of_day = datetime.datetime(day.year, day.month, day.day)
        async with MyPyllantAPI(self.user, self.password, self.brand, self.country) as api:
            log(f"Fetching device data from API for day {day.strftime('%Y-%m-%d')}")
            try:
                device_datas = [
                    d async for d in api.get_data_by_device(
                        system.devices[0], DeviceDataBucketResolution.HOUR,
                        start_of_day,
                        start_of_day + datetime.timedelta(days=1)
                    )
                ]
            except Exception as e:
                print(f"Got error trying to fetch consumption data from API for day {day.strftime('%Y-%m-%d')}", file=sys.stderr)
                print(f"Exception: {str(e)}", file=sys.stderr)
                traceback.print_exc()
                device_datas = []
            return device_datas

    async def _fetch_home(self, api):
        if "home" in self.home_cache.keys():
            return self.home_cache["home"]

        log("Fetching home from API")
        async for home in api.get_homes():
            # This assumes there is only one home on the account
            self.home_cache["home"] = home
            return home
