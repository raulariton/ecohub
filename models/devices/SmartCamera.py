from datetime import datetime
from .SmartDevice import SmartDevice
from dataclasses import dataclass
import random


@dataclass
class CameraPayload:
    device_id: str
    name: str
    location: str
    motion_detected: bool
    battery_level: int
    last_snapshot: datetime | None


class SmartCamera(SmartDevice):
    def __init__(
        self,
        name,
        location,
        battery_level: int,
    ):
        super().__init__(name, location)
        self._motion_detected = False  # start with no motion detected by default
        self._battery_level = battery_level
        self._last_snapshot = None  # no snapshot yet since no motion detected
        self._device_type = "CAMERA"

    def get_status(self) -> dict:
        return {
            "id": str(self._id),
            "name": self._name,
            "location": self._location.value,
            "motion_detected": self._motion_detected,
            "battery_level": self._battery_level,
            "last_snapshot": (
                self._last_snapshot.isoformat() if self._last_snapshot else None
            ),
            "device_type": self._device_type,
        }

    def update_state(self) -> None:
        # simulate motion detection randomly
        self._motion_detected = random.choice([True, False])

        # decrease battery level over time
        self._battery_level -= 0.25 if self._battery_level > 0 else 0

    def execute_command(self, command: str) -> None:
        if command == "take_snapshot":
            # take a snapshot
            self._last_snapshot = datetime.now()
        else:
            print(f"Unknown command: {command}")
