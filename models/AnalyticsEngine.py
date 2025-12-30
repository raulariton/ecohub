import functools
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
    def get_metrics(connected_devices) -> dict:
        # average house temperature
        temperature_sum = functools.reduce(lambda sum_, payload: sum_ + AnalyticsEngine.get_temperature(payload),
                                   connected_devices.values(), 0.0)
        total_thermostats = sum(1 for payload in connected_devices.values() if isinstance(payload, ThermostatPayload))
        average_temperature = temperature_sum / total_thermostats if total_thermostats > 0 else 0.0

        # average house humidity
        humidity_sum = functools.reduce(lambda sum_, payload: sum_ + AnalyticsEngine.get_humidity(payload),
                                   connected_devices.values(), 0.0)
        average_humidity = humidity_sum / total_thermostats if total_thermostats > 0 else 0.0

        # total connected devices
        total_devices = len(connected_devices)
        return {
            "average_temperature": average_temperature,
            "average_humidity": average_humidity,
            "total_connected_devices": total_devices,
        }

    @staticmethod
    def get_temperature(payload) -> float:
        """
        Given a payload, returns the temperature if the payload
        is from a thermostat device and from an indoor location.
        """
        INDOOR_LOCATIONS = [
            DeviceLocation.LIVING_ROOM,
            DeviceLocation.BEDROOM,
            DeviceLocation.KITCHEN,
            DeviceLocation.BATHROOM,
            DeviceLocation.OFFICE,
            DeviceLocation.HALLWAY,
            DeviceLocation.DINING_ROOM
        ]
        if isinstance(payload, ThermostatPayload) and payload.location in INDOOR_LOCATIONS:
            return payload.current_temp
        return 0.0

    @staticmethod
    def get_humidity(payload) -> float:
        """
        Given a payload, returns the humidity if the payload
        is from a thermostat device.
        """
        if isinstance(payload, ThermostatPayload):
            return payload.humidity
        return 0.0


