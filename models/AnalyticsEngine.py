import json
from datetime import datetime
from models.devices import ThermostatPayload, BulbPayload, CameraPayload
from .CriticalEvent import CriticalEvent


# NOTE: if we eventually use a dashboard,
#  whether an event is critical or not can be selected by the user
#  and this function will parse that configuration
def is_critical(payload) -> CriticalEvent | None:
    # if payload is from a thermostat
    if isinstance(payload, ThermostatPayload):
        if payload.current_temp < 15.0:
            return CriticalEvent.LOW_TEMPERATURE

        if payload.current_temp > 30.0:
            return CriticalEvent.HIGH_TEMPERATURE

        # low humidity alert
        if payload.humidity < 15.0:
            return CriticalEvent.LOW_HUMIDITY

        if payload.humidity > 80.0:
            return CriticalEvent.HIGH_HUMIDITY

    # if payload is from a camera
    elif isinstance(payload, CameraPayload):
        if payload.motion_detected:
            return CriticalEvent.MOTION_DETECTED

        if payload.battery_level < 15.0:
            return CriticalEvent.LOW_BATTERY

    return None


class AnalyticsEngine:
    @staticmethod
    def map_packet(packet):
        packet_data = json.loads(packet)
        timestamp = datetime.fromisoformat(packet_data["timestamp"])
        device_type = packet_data["payload"]["device_type"]

        if device_type == "THERMOSTAT":
            yield ThermostatPayload(
                device_id=packet_data["device_id"],
                name=packet_data["payload"]["name"],
                location=packet_data["payload"]["location"],
                current_temp=packet_data["payload"]["current_temp"],
                target_temp=packet_data["payload"]["target_temp"],
                humidity=packet_data["payload"]["humidity"],
            )
        elif device_type == "BULB":
            yield BulbPayload(
                device_id=packet_data["device_id"],
                name=packet_data["payload"]["name"],
                location=packet_data["payload"]["location"],
                is_on=packet_data["payload"]["is_on"],
                brightness=packet_data["payload"]["brightness"],
            )
        elif device_type == "CAMERA":
            yield CameraPayload(
                device_id=packet_data["device_id"],
                name=packet_data["payload"]["name"],
                location=packet_data["payload"]["location"],
                motion_detected=packet_data["payload"]["motion_detected"],
                battery_level=packet_data["payload"]["battery_level"],
                last_snapshot=(
                    datetime.fromisoformat(packet_data["payload"]["last_snapshot"])
                    if packet_data["payload"]["last_snapshot"]
                    else None
                ),
            )
        else:
            # unknown device type
            return

    @staticmethod
    def filter_events(stream):
        # filter payloads for critical events only
        critical_payloads = filter(
            lambda payload: is_critical(payload) is not None, stream
        )

        # attach critical event type to payload
        for payload in critical_payloads:
            yield (payload, is_critical(payload))

    @staticmethod
    def reduce(stream) -> dict:
        # using `functools.reduce`, aggregate events
        # into summaries e.g. average house temperature, max humidity, etc.
        pass
