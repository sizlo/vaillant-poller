import datetime
import traceback
import time

from fetcher import Fetcher
from local_persistor import LocalPersistor
from metrics_pusher import MetricsPusher
from state_builder import StateBuilder
from log import log
from env import require_env

poll_delay = int(require_env("VAILLANT_POLL_DELAY_SECONDS"))


def main():
    while True:
        try:
            now = datetime.datetime.now()
            system = Fetcher().fetch()
            state = StateBuilder(now).build(system)
            LocalPersistor(now).persist(system, state)
            MetricsPusher().push(state)
        except:
            traceback.print_exc()
        finally:
            log(f"Waiting {poll_delay} seconds")
            time.sleep(poll_delay)


if __name__ == "__main__":
    main()
