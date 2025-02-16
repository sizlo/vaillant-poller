import traceback
import sys


class StateBuilder:
    def __init__(self, now):
        self.state = None
        self.now = now

    def build(self, system):
        self.state = {"sample_time": self.now}
        self._add_value("outdoor_temperature", lambda: system.outdoor_temperature)
        self._add_value("outdoor_temperature_average24h", lambda: system.state["system"]["outdoor_temperature_average24h"])
        self._add_value("current_room_temperature", lambda: system.zones[0].current_room_temperature)
        self._add_value("current_room_humidity", lambda: system.zones[0].current_room_humidity)
        self._add_value("current_dhw_temperature", lambda: system.domestic_hot_water[0].current_dhw_temperature)
        self._add_value("water_pressure", lambda: system.water_pressure)
        self._add_value("current_circuit_flow_temperature", lambda: system.circuits[0].current_circuit_flow_temperature)
        self._add_value("heating_circuit_flow_setpoint", lambda: system.circuits[0].extra_fields["heating_circuit_flow_setpoint"])
        self._add_value("energy_manager_state", lambda: system.state["system"]["energy_manager_state"])
        self._add_value("operation_mode_heating", lambda: system.zones[0].heating.operation_mode_heating)
        self._add_value("desired_room_temperature_setpoint_heating", lambda: system.zones[0].desired_room_temperature_setpoint_heating)
        self._add_value("desired_room_temperature_setpoint", lambda: system.zones[0].desired_room_temperature_setpoint)
        self._add_value("set_back_temperature", lambda: system.zones[0].heating.set_back_temperature)
        self._add_value("manual_mode_setpoint_heating", lambda: system.zones[0].heating.manual_mode_setpoint_heating)
        self._add_value("heat_demand_limited_by_outside_temperature", lambda: system.circuits[0].heat_demand_limited_by_outside_temperature)
        self._add_value("heating_curve", lambda: system.circuits[0].heating_curve)
        self._add_value("operation_mode_dhw", lambda: system.domestic_hot_water[0].operation_mode_dhw)
        self._add_value("tapping_setpoint", lambda: system.domestic_hot_water[0].tapping_setpoint)
        self._add_value("dhw_hysteresis", lambda: system.configuration["system"]["dhw_hysteresis"])
        self._add_value("dhw_maximum_loading_time", lambda: system.configuration["system"]["dhw_maximum_loading_time"])
        self._add_value("current_special_function", lambda: system.domestic_hot_water[0].current_special_function)
        return self.state

    def _add_value(self, key, getter):
        try:
            self.state[key] = getter()
        except:
            print(f"Error trying to get value for {key}, using None instead", file=sys.stderr)
            traceback.print_exc()
            return None
