class Consumption:
    def __init__(self, energy_type, operation_mode, start_date, end_date, value):
        self.energy_type = energy_type
        self.operation_mode = operation_mode
        self.start_date = start_date
        self.end_date = end_date
        self.value = value


class ConsumptionBuilder:
    def build(self, data):
        if data is None:
            return []

        consumptions = []

        for device_data in data:
            for bucket in device_data.data:
                consumptions.append(
                    Consumption(
                        device_data.energy_type.lower(),
                        device_data.operation_mode.lower(),
                        bucket.start_date,
                        bucket.end_date,
                        0 if bucket.value is None else bucket.value
                    )
                )

        return consumptions