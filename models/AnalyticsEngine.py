import json
from datetime import datetime
from models.devices import ThermostatPayload, BulbPayload, CameraPayload


# NOTE: if we eventually use a dashboard,
#  whether an event is critical or not can be selected by the user
#  and this function will parse that configuration
def is_critical(payload) -> bool:
    return True  # treat all events as critical for now


"""
{
    "device_id": "123e4567-e89b-12d3-a456-426614174000",
    "payload": {
        "temperature": 22.5,
        "humidity": 45.0
    },
    "timestamp": "2023-10-01T12:00:00Z"
}
"""


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
        return filter(is_critical, stream)

    @staticmethod
    def reduce(stream) -> dict:
        # using `functools.reduce`, aggregate events
        # into summaries e.g. average house temperature, max humidity, etc.
        pass
