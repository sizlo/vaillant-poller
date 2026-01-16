import os
import csv
import jsonpickle
import glob
import errno
import shutil


from env import require_env
from log import log


class LocalPersistor:
    def __init__(self, now):
        self.path = require_env("VAILLANT_LOCAL_STORAGE_PATH")
        self.num_daily_system_dumps_to_keep = int(require_env("VAILLANT_NUM_DAILY_SYSTEM_DUMPS_TO_KEEP"))
        self.now = now

    def persist(self, system, state, consumption_days):
        self._persist_state(state)
        self._persist_system(system)
        self._purge_old_system_dumps()
        for consumption_day in consumption_days:
            self._persist_consumption_day(consumption_day)

    def consumption_day_file_exists(self, day):
        return os.path.isfile(self._get_consumption_day_file_path(day))

    def _persist_state(self, state):
        filepath = os.path.join(self.path, "state_samples", self.now.strftime("%Y"), f"vaillant_state_{self.now.strftime('%Y-%m')}.csv")
        if os.path.isfile(filepath):
            _append_csv(filepath, state)
        else:
            _create_csv(filepath, state)

    def _persist_system(self, system):
        system_json = jsonpickle.encode(system)
        daily_filepath = os.path.join(self.path, "system_dumps", "daily", self.now.strftime("%Y"), self.now.strftime("%m"), f"vaillant_system_{self.now.strftime('%Y-%m-%d')}.json")
        monthly_filepath = os.path.join(self.path, "system_dumps", "monthly", self.now.strftime("%Y"), f"vaillant_system_{self.now.strftime('%Y-%m')}.json")
        _dump_system_to_file(daily_filepath, system_json)
        _dump_system_to_file(monthly_filepath, system_json)

    def _persist_consumption_day(self, consumption_day):
        day = consumption_day["day"]
        consumption_buckets = consumption_day["consumption_buckets"]
        if len(consumption_buckets) == 0:
            return
        file_path = self._get_consumption_day_file_path(day)
        log(f"Creating consumption csv {file_path}")
        _ensure_dirs_exist(file_path)
        with open(file_path, "w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=consumption_buckets[0].keys())
            writer.writeheader()
            for bucket in consumption_buckets:
                writer.writerow(bucket)

    def _purge_old_system_dumps(self):
        daily_dumps_path = os.path.join(self.path, "system_dumps", "daily")
        all_dumps = glob.glob(os.path.join(daily_dumps_path, "**", "*.json"), recursive=True)
        oldest_dumps = sorted(all_dumps, reverse=True)[self.num_daily_system_dumps_to_keep:]
        for dump in oldest_dumps:
            log(f"Deleting old system dump {dump}")
            os.remove(dump)
        _purge_directories_with_no_subdirectories_and_no_files_with_extension(daily_dumps_path, ".json")

    def _get_consumption_day_file_path(self, day):
        return os.path.join(self.path, "consumption", day.strftime("%Y"), day.strftime("%m"), f"consumption_{day.strftime('%Y-%m-%d')}.csv")


def _append_csv(filepath, state):
    log(f"Appending state to csv {filepath}")
    _ensure_dirs_exist(filepath)
    with open(filepath, "a") as f:
        writer = csv.writer(f)
        writer.writerow(state.values())


def _create_csv(filepath, state):
    log(f"Creating state csv {filepath}")
    _ensure_dirs_exist(filepath)
    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(state.keys())
        writer.writerow(state.values())


def _dump_system_to_file(filepath, system):
    _ensure_dirs_exist(filepath)
    if not os.path.isfile(filepath):
        log(f"Dumping system to file {filepath}")
        with open(filepath, "w") as f:
            f.write(system)


def _ensure_dirs_exist(filepath):
    try:
        os.makedirs(os.path.dirname(filepath))
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


def _purge_directories_with_no_subdirectories_and_no_files_with_extension(root, file_extension):
    did_delete = False

    all_paths = glob.glob(os.path.join(root, "**"), recursive=True)
    for path in all_paths:
        if not os.path.isdir(path):
            continue

        if _delete_directory_if_it_has_no_subdirectories_and_no_files_with_extension(path, file_extension):
            did_delete = True

    # Recurse if we deleted, as this may have made a parent directory eligible for purging
    if did_delete:
        _purge_directories_with_no_subdirectories_and_no_files_with_extension(root, file_extension)


def _delete_directory_if_it_has_no_subdirectories_and_no_files_with_extension(path, file_extension):
    immediate_children = glob.glob(os.path.join(path, "*"))
    for child in immediate_children:
        if os.path.isdir(child):
            return False
        if child.endswith(file_extension):
            return False
    log(f"Purging directory as it no longer contains any {file_extension} files, or subdirectories: {path}")
    shutil.rmtree(path)
    return True
