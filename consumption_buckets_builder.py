class ConsumptionBucketsBuilder:
    def __init__(self):
        self.consumption_buckets = None

    def build(self, device_datas):
        self.consumption_buckets = {}
        for device_data in device_datas:
            for datapoint in device_data.data:
                self._add_or_append_to_consumption_bucket(device_data, datapoint)
        return list(self.consumption_buckets.values())

    def _add_or_append_to_consumption_bucket(self, device_data, datapoint):
        start_str = datapoint.start_date.strftime("%Y-%m-%dT%H:%M")
        end_str = datapoint.end_date.strftime("%Y-%m-%dT%H:%M")
        bucket_id = f"{start_str} - {end_str}"

        if bucket_id not in self.consumption_buckets.keys():
            self.consumption_buckets[bucket_id] = {
                "start": start_str,
                "end": end_str
            }

        datapoint_id = f"{device_data.operation_mode}.{device_data.energy_type}"
        value = 0 if datapoint.value is None else datapoint.value
        self.consumption_buckets[bucket_id][datapoint_id] = value
