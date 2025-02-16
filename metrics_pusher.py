import requests
import sys
import datetime
import pytz

from myPyllant.enums import CircuitState, ZoneOperatingMode, DHWOperationMode, DHWCurrentSpecialFunction
from env import require_env
from log import log


class MetricsPusher:
    def __init__(self):
        self.url = require_env("VAILLANT_METRICS_URL")
        self.api_key = require_env("VAILLANT_METRICS_API_KEY")

    def push(self, state, consumptions):
        body = build_body(state, consumptions)
        log(f"Pushing {len(body.splitlines())} metrics")
        response = requests.post(
            self.url,
            headers={
                "Content-Type": "text/plain",
                "Authorization": f"Bearer {self.api_key}"
            },
            data=body,
        )
        if not response.ok:
            print(f"Error pushing metrics. status_code={response.status_code}. body={response.text}.", file=sys.stderr)


def build_body(state, consumptions):
    body = ""
    body += get_numeric_metric(state, "outdoor_temperature")
    body += get_numeric_metric(state, "outdoor_temperature_average24h")
    body += get_numeric_metric(state, "current_room_temperature")
    body += get_numeric_metric(state, "current_room_humidity")
    body += get_numeric_metric(state, "current_dhw_temperature")
    body += get_numeric_metric(state, "water_pressure")
    body += get_numeric_metric(state, "current_circuit_flow_temperature")
    body += get_numeric_metric(state, "heating_circuit_flow_setpoint")
    body += get_numeric_metric(state, "desired_room_temperature_setpoint_heating")
    body += get_numeric_metric(state, "desired_room_temperature_setpoint")
    body += get_numeric_metric(state, "set_back_temperature")
    body += get_numeric_metric(state, "manual_mode_setpoint_heating")
    body += get_numeric_metric(state, "heat_demand_limited_by_outside_temperature")
    body += get_numeric_metric(state, "heating_curve")
    body += get_numeric_metric(state, "tapping_setpoint")
    body += get_numeric_metric(state, "dhw_hysteresis")
    body += get_numeric_metric(state, "dhw_maximum_loading_time")
    body += get_enum_metric(state, "energy_manager_state", [e.value for e in CircuitState])
    body += get_enum_metric(state, "operation_mode_heating", [e.value for e in ZoneOperatingMode])
    body += get_enum_metric(state, "operation_mode_heating", [e.value for e in DHWOperationMode])
    body += get_enum_metric(state, "current_special_function", [e.value for e in DHWCurrentSpecialFunction])
    for consumption in consumptions:
        body += get_consumption_metric(consumption)
    return body


def get_numeric_metric(state, key):
    value = state[key]
    if value is None:
        print(f"Missing value for {key} metric, skipping pushing this metric to server", file=sys.stderr)
        return ""
    return f"{key},source=vaillant-poller value={state[key]}\n"


def get_enum_metric(state, key, enum_values):
    str_value = state[key]
    if str_value is None:
        print(f"Missing value for {key} metric, skipping pushing this metric to server", file=sys.stderr)
        return ""

    try:
        index = enum_values.index(str_value)
    except ValueError:
        index = 0.5
    return f"{key},source=vaillant-poller,str_value={str_value} value={index}\n"


def get_consumption_metric(consumption):
    if consumption.start_date > datetime.datetime.now(pytz.timezone("Europe/London")):
        return ""
    start_date_nano_ts = int(consumption.start_date.timestamp() * 1000000000)
    return f"{consumption.energy_type},source=vaillant-poller-new,operation_mode={consumption.operation_mode} value={consumption.value} {start_date_nano_ts}\n"
