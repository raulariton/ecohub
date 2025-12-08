import datetime
from models.SmartDevice import SmartDevice


class SmartCamera(SmartDevice):
    def __init__(
        self,
        name,
        location,
        motion_detected: bool,
        battery_level: int,
        last_snapshot: datetime.datetime,
    ):
        super().__init__(name, location)
        self._motion_detected = motion_detected
        self._battery_level = battery_level
        self._last_snapshot = last_snapshot
        self._device_type = "CAMERA"

    def get_status(self) -> dict:
        return {
            "id": str(self._id),
            "name": self._name,
            "location": self._location.value,
            "device_type": self._device_type,
            "resolution": self._resolution,
            "is_recording": self._is_recording,
        }

    def execute_command(self, command: str) -> None:
        if command == "start_recording":
            self._is_recording = True
        elif command == "stop_recording":
            self._is_recording = False
        else:
            print(f"Unknown command: {command}")
