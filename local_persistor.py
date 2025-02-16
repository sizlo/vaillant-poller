import os
import csv
import jsonpickle
import glob
import errno


from env import require_env
from log import log


class LocalPersistor:
    def __init__(self, now):
        self.path = require_env("VAILLANT_LOCAL_STORAGE_PATH")
        self.now = now
        self.num_daily_system_dumps_to_keep = 100

    def persist(self, system, state):
        self._persist_state(state)
        self._persist_system(system)
        self._purge_old_system_dumps()

    def _persist_state(self, state):
        filepath = os.path.join(self.path, "state_samples", f"vaillant_state_{self.now.strftime('%Y-%m')}.csv")
        if os.path.isfile(filepath):
            _append_csv(filepath, state)
        else:
            _create_csv(filepath, state)

    def _persist_system(self, system):
        system_json = jsonpickle.encode(system)
        daily_filepath = os.path.join(self.path, "system_dumps", "daily", f"vaillant_system_{self.now.strftime('%Y-%m-%d')}.json")
        monthly_filepath = os.path.join(self.path, "system_dumps", "monthly", f"vaillant_system_{self.now.strftime('%Y-%m')}.json")
        dump_system_to_file(daily_filepath, system_json)
        dump_system_to_file(monthly_filepath, system_json)

    def _purge_old_system_dumps(self):
        all_dumps = glob.glob(os.path.join(self.path, "system_dumps", "daily", "*.json"))
        oldest_dumps = sorted(all_dumps, reverse=True)[self.num_daily_system_dumps_to_keep:]
        for dump in oldest_dumps:
            log(f"Deleting old system dump {dump}")
            os.remove(dump)


def _append_csv(filepath, state):
    log(f"Appending state to csv {filepath}")
    ensure_dirs_exist(filepath)
    with open(filepath, "a") as f:
        writer = csv.writer(f)
        writer.writerow(state.values())


def _create_csv(filepath, state):
    log(f"Creating state csv {filepath}")
    ensure_dirs_exist(filepath)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(state.keys())
        writer.writerow(state.values())


def dump_system_to_file(filepath, system):
    ensure_dirs_exist(filepath)
    if not os.path.isfile(filepath):
        log(f"Dumping system to file {filepath}")
        with open(filepath, "w") as f:
            f.write(system)


def ensure_dirs_exist(filepath):
    try:
        os.makedirs(os.path.dirname(filepath))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
