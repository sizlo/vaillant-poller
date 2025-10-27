import datetime
import traceback
import time

from consumption_buckets_builder import ConsumptionBucketsBuilder
from fetcher import Fetcher
from local_persistor import LocalPersistor
from metrics_pusher import MetricsPusher
from metrics_server import MetricsServer
from missing_consumption_days_getter import MissingConsumptionDaysGetter
from state_builder import StateBuilder
from log import log
from env import require_env

poll_delay = int(require_env("VAILLANT_POLL_DELAY_SECONDS"))


def main():
    metrics_server = MetricsServer()
    fetcher = Fetcher()
    while True:
        try:
            now = datetime.datetime.now()
            state_builder = StateBuilder(now)
            consumption_buckets_builder = ConsumptionBucketsBuilder()
            local_persistor = LocalPersistor(now)
            missing_consumption_days_getter = MissingConsumptionDaysGetter(now, fetcher, local_persistor, consumption_buckets_builder)
            metrics_pusher = MetricsPusher()

            system = fetcher.fetch_system()
            state = state_builder.build(system)
            consumption_days = missing_consumption_days_getter.get_missing_consumption_days(system)
            local_persistor.persist(system, state, consumption_days)
            metrics_pusher.push(state)
            metrics_server.update(state)
        except:
            traceback.print_exc()
        finally:
            log(f"Waiting {poll_delay} seconds")
            time.sleep(poll_delay)


if __name__ == "__main__":
    main()
