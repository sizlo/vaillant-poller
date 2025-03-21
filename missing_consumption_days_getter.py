import datetime

from env import require_env


class MissingConsumptionDaysGetter:
    def __init__(self, now, fetcher, local_persistor, consumption_buckets_builder):
        self.lookback_days = int(require_env("VAILLANT_CONSUMPTION_LOOKBACK_DAYS"))
        self.now = now
        self.fetcher = fetcher
        self.local_persistor = local_persistor
        self.consumption_buckets_builder = consumption_buckets_builder

    def get_missing_consumption_days(self, system):
        consumption_days = []
        today = self.now.date()

        # Start from 2 days ago, because yesterday's data might not be ready when this runs just after midnight
        for offset in range(2, self.lookback_days):
            day = today - datetime.timedelta(days=offset)

            if not self.local_persistor.consumption_day_file_exists(day):
                data = self.fetcher.fetch_hourly_device_data_for_day(system, day)
                if len(data) == 0:
                    continue

                consumption_buckets = self.consumption_buckets_builder.build(data)
                consumption_days.append({"day": day, "consumption_buckets": consumption_buckets})

        return consumption_days
