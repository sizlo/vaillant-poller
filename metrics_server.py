import random
import time
import sys

from log import log
from prometheus_client import start_http_server, Gauge
from myPyllant.enums import CircuitState, ZoneOperatingMode, DHWOperationMode, DHWCurrentSpecialFunction

# I'm using a bit of a hack to allow me to clear metrics when they are missing from the API response, instead of sending their previous value again.
# When metrics have a label, you can use the .clear() method to remove values for all the current labels. This means the scraper will not see
# anything for those metrics.
# By setting a "source" label on all my metrics this allows me to use .clear(). In normal uses you would configure the scraper to add a "source" label
# too all metrics it scrapes from your service.
SOURCE = "vaillant-poller"

class MetricsServer:
    def __init__(self):
        self.metrics = {
            "outdoor_temperature": Gauge("outdoor_temperature", "The actual temperature ready by the outdoor temperature sensor", ["source"]),
            "outdoor_temperature_average24h": Gauge("outdoor_temperature_average24h", "The average of the actual temperature ready by the outdoor temperature sensor over the past 24 hours", ["source"]),
            "current_room_temperature": Gauge("current_room_temperature", "The actual room temperature read by the wireless control unit", ["source"]),
            "current_room_humidity": Gauge("current_room_humidity", "The actual room humidity read by the wireless control unit", ["source"]),
            "current_dhw_temperature": Gauge("current_dhw_temperature", "The actual hot water temperature read by a sensor in the hot water tank", ["source"]),
            "water_pressure": Gauge("water_pressure", "The actual water pressure, the location of the sensor reading this is unknown", ["source"]),
            "current_circuit_flow_temperature": Gauge("current_circuit_flow_temperature", "The actual flow temperate, I assume this is read by a sensor inside the heat pump", ["source"]),
            "heating_circuit_flow_setpoint": Gauge("heating_circuit_flow_setpoint", "The current desired flow temperature", ["source"]),
            "desired_room_temperature_setpoint_heating": Gauge("desired_room_temperature_setpoint_heating", "The current desired room temperature. While the schedule is active this is the desired temperature defined in the schedule. While the schedule is inactive this is the setback temperature. While the system is in manual mode this is the desired temperature defined for manual mode.", ["source"]),
            "desired_room_temperature_setpoint": Gauge("desired_room_temperature_setpoint", "The current desired room temperature. While the schedule is active this is the desired temperature defined in the schedule. While the schedule is inactive this is the setback temperature. While the system is in manual mode this is the desired temperature defined for manual mode.", ["source"]),
            "set_back_temperature": Gauge("set_back_temperature", "Setting for the desired room temperature for inactive periods of the heating schedule", ["source"]),
            "manual_mode_setpoint_heating": Gauge("manual_mode_setpoint_heating", "Setting for The desired room temperature when in manual heating mode", ["source"]),
            "heat_demand_limited_by_outside_temperature": Gauge("heat_demand_limited_by_outsidt_temperature", "Setting for the temperature which when the average outside temperature over the last 24 hours falls below, the heating system will be disabled", ["source"]),
            "heating_curve": Gauge("heating_curve", "Setting for the heat curve", ["source"]),
            "tapping_setpoint": Gauge("tapping_setpoint", "Setting for the desired temperature to heat the water tank to", ["source"]),
            "dhw_hysteresis": Gauge("dhw_hysteresis", "Setting for the temperature buffer where the water tank will not be reheated. E.g if the desired tank temperature is 48 and the hysteresis is 7, the water tank will not be heated until the actual tank temperature falls below 41.", ["source"]),
            "dhw_maximum_loading_time": Gauge("dhw_maximum_loading_time", "Setting for how long the system will prioritise hot water over central heating for", ["source"]),
            "energy_manager_state": Gauge("energy_manager_state", "The current priority of the system (hot water or heating)", ["source", "str_value"]),
            "operation_mode_heating": Gauge("operation_mode_heating", "Setting for the current heating mode (schedule, manual, etc)", ["source", "str_value"]),
            "operation_mode_dhw": Gauge("operation_mode_dhw", "Setting for the current hot water mode (schedule, manual, etc)", ["source", "str_value"]),
            "current_special_function": Gauge("current_special_function", "If the hot water is currently in a special mode (e.g boost)", ["source", "str_value"]),
        }

        self.server_running = False

    def update(self, state):
        log("Updating metrics")
        self._set_numeric_metric(state, "outdoor_temperature")
        self._set_numeric_metric(state, "outdoor_temperature_average24h")
        self._set_numeric_metric(state, "current_room_temperature")
        self._set_numeric_metric(state, "current_room_humidity")
        self._set_numeric_metric(state, "current_dhw_temperature")
        self._set_numeric_metric(state, "water_pressure")
        self._set_numeric_metric(state, "current_circuit_flow_temperature")
        self._set_numeric_metric(state, "heating_circuit_flow_setpoint")
        self._set_numeric_metric(state, "desired_room_temperature_setpoint_heating")
        self._set_numeric_metric(state, "desired_room_temperature_setpoint")
        self._set_numeric_metric(state, "set_back_temperature")
        self._set_numeric_metric(state, "manual_mode_setpoint_heating")
        self._set_numeric_metric(state, "heat_demand_limited_by_outside_temperature")
        self._set_numeric_metric(state, "heating_curve")
        self._set_numeric_metric(state, "tapping_setpoint")
        self._set_numeric_metric(state, "dhw_hysteresis")
        self._set_numeric_metric(state, "dhw_maximum_loading_time")
        self._set_enum_metric(state, "energy_manager_state", [e.value for e in CircuitState])
        self._set_enum_metric(state, "operation_mode_heating", [e.value for e in ZoneOperatingMode])
        self._set_enum_metric(state, "operation_mode_dhw", [e.value for e in DHWOperationMode])
        self._set_enum_metric(state, "current_special_function", [e.value for e in DHWCurrentSpecialFunction])

        if not self.server_running:
            log("Starting metrics server on port 9200")
            start_http_server(9200)
            self.server_running = True

    def _set_numeric_metric(self, state, key):
        value = state[key]
        if value is None:
            print(f"Missing value for {key} metric, removing this metric until a value is present", file=sys.stderr)
            self.metrics[key].clear()
            return
        self.metrics[key].labels(SOURCE).set(value)

    def _set_enum_metric(self, state, key, enum_values):
        # Clear values for all labels of this metric, since we will only be updating the one where label str_value == <the current state value>
        # We don't want the previous values of other labels to appear in our metrics
        self.metrics[key].clear()

        str_value = state[key]
        if str_value is None:
            print(f"Missing value for {key} metric, removing this metric until a value is present", file=sys.stderr)
            return ""

        try:
            index = enum_values.index(str_value)
        except ValueError:
            index = 0.5

        self.metrics[key].labels(SOURCE, str_value).set(index)
