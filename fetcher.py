import asyncio
import datetime
import sys
import traceback

from env import require_env
from log import log
from myPyllant.api import MyPyllantAPI
from myPyllant.enums import DeviceDataBucketResolution


class Fetcher:
    def __init__(self):
        self.user = require_env("VAILLANT_USER")
        self.password = require_env("VAILLANT_PASSWORD")
        self.brand = "vaillant"
        self.country = "unitedkingdom"

    def fetch_system(self):
        return asyncio.run(self._fetch_system())

    async def _fetch_system(self):
        async with MyPyllantAPI(self.user, self.password, self.brand, self.country) as api:
            log("Fetching system from API")
            async for system in api.get_systems():
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
